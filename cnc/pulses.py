from __future__ import division
import math
import logging

from cnc.config import *
from cnc.coordinates import Coordinates

SECONDS_IN_MINUTE = 60


class PulseGenerator(object):
    """ Stepper motors pulses generator.
        It generates time for each pulses for specified path as accelerated
        movement for specified velocity, then moves linearly and then braking
        with the same acceleration.
        Internally this class treat movement as uniform movement and then
        translate timings to accelerated movements. To do so, it base on
        formulas for distance of uniform movement and accelerated move.
            S = V * Ta = a * Tu^2 / 2
        where Ta - time for accelerated and Tu for uniform movement.
        Velocity will never be more then Vmax - maximum velocity of all axises.
        At the point of maximum velocity we change accelerated movement to
        uniform, so we can translate time for accelerated movement with this
        formula:
            Ta(Tu) = a * Tu^2 / Vmax / 2
        Now we need just to calculate how much time will accelerate and
        brake will take and recalculate time for them. Linear part will be as
        is. Since maximum velocity and acceleration is always the same, there
        is the ACCELERATION_FACTOR_PER_SEC variable.
        In the same way round or other interpolation can be implemented based on
        this class.
        Note: round interpolation would require direction change during movement.
        It's not implemented yet.
    """

    def __init__(self):
        """ Create object. Do not create directly this object, inherit this class
            and implement interpolation function and related methods.
            All child have to call this method ( super().__init__() ).
        """
        self._iteration_x = 0
        self._iteration_y = 0
        self._iteration_z = 0
        self._acceleration_time_s = 0.0
        self._linear_time_s = 0.0
        self._2Vmax_per_a = 0.0

    def _get_movement_parameters(self):
        """ Get for interpolation. This method have to be reimplemented
            in parent classes and should calculate 3 parameters.
        :return: Tuple of three values:
                acceleration_time_s: time for accelerating and breaking motors
                                     during movement
                linear_time_s: time for uniform movement, it is total movement
                               time minus acceleration and braking time
                max_axis_velocity_mm_per_sec: maximum velocity of any of axis during
                                              movement. Even if whole movement is
                                              accelerated, this value should be
                                              calculated as top velocity.
        """
        raise NotImplemented

    def _interpolation_function(self, pulse_number):
        """ Get function for interpolation path. This function should returned
            values as it is uniform movement. There is only one trick, function
            must be expressed in terms of position, i.e. t = S / V for linear,
            where S - distance would be increment on motor minimum step.
        :param pulse_number: number of pulse.
        :return: time for each axis or None if movement for axis is finished.
        """
        raise NotImplemented

    def __iter__(self):
        """ Get iterator.
        :return: iterable object.
        """
        self._acceleration_time_s, self._linear_time_s, \
        max_axis_velocity_mm_per_sec = self._get_movement_parameters()
        # helper variable
        self._2Vmax_per_a = 2.0 * max_axis_velocity_mm_per_sec \
                            / STEPPER_MAX_ACCELERATION_MM_PER_S2
        self._iteration_x = 0
        self._iteration_y = 0
        self._iteration_z = 0
        logging.debug(', '.join("%s: %s" % i for i in vars(self).items()))
        return self

    def _to_accelerated_time(self, pt_s):
        """ Internal function to translate uniform movement time to time for
            accelerated movement.
        :param pt_s: pseudo time of uniform movement.
        :return: time for each axis or None if movement for axis is finished.
        """
        # acceleration
        # S = Tpseudo * Vmax = a * t^2 / 2
        t = math.sqrt(pt_s * self._2Vmax_per_a)
        if t <= self._acceleration_time_s:
            return t

        # linear
        # pseudo acceleration time Tpseudo = t^2 / ACCELERATION_FACTOR_PER_SEC
        t = self._acceleration_time_s + pt_s - (self._acceleration_time_s ** 2
                                                / self._2Vmax_per_a)
        # pseudo breaking time
        bt = t - self._acceleration_time_s - self._linear_time_s
        if bt <= 0:
            return t

        # braking
        # Vmax * Tpseudo = Vlinear * t - a * t^2 / 2
        # V on start braking is Vlinear = Taccel * a = Tbreaking * a
        # Vmax * Tpseudo = Tbreaking * a * t - a * t^2 / 2
        return 2.0 * self._acceleration_time_s + self._linear_time_s \
               - math.sqrt(self._acceleration_time_s ** 2 - self._2Vmax_per_a * bt)

    def __next__(self):
        # for python3
        return self.next()

    def next(self):
        """ Iterate pulses.
        :return: Tuple of three values for each axis which represent time for
                 the next pulse. If there is no pulses left  None will be
                 returned.
        """
        tx, ty, tz = self._interpolation_function(self._iteration_x,
                                                  self._iteration_y,
                                                  self._iteration_z)
        # check condition to stop
        if tx is None and ty is None and tz is None:
            raise StopIteration

        # convert to real time
        m = min(x for x in (tx, ty, tz) if x is not None)
        am = self._to_accelerated_time(m)
        # sort pulses in time
        if tx is not None:
            if tx > m:
                tx = None
            else:
                tx = am
                self._iteration_x += 1
        if ty is not None:
            if ty > m:
                ty = None
            else:
                ty = am
                self._iteration_y += 1
        if tz is not None:
            if tz > m:
                tz = None
            else:
                tz = am
                self._iteration_z += 1

        return tx, ty, tz

    def total_time_s(self):
        """ Get total time for movement.
        :return: time in seconds.
        """
        acceleration_time_s, linear_time_s, _ = self._get_movement_parameters()
        return acceleration_time_s * 2.0 + linear_time_s


class PulseGeneratorLinear(PulseGenerator):
    def __init__(self, delta_mm, velocity_mm_per_min):
        """ Create pulse generator for linear interpolation.
        :param delta_mm: movement distance of each axis.
        :param velocity_mm_per_min: desired velocity.
        """
        super(PulseGeneratorLinear, self).__init__()
        # this class doesn't care about direction
        self._distance_mm = abs(delta_mm)
        # velocity of each axis
        distance_xyz_mm = self._distance_mm.length()
        self.max_velocity_mm_per_sec = self._distance_mm * (
            velocity_mm_per_min / SECONDS_IN_MINUTE / distance_xyz_mm)
        # acceleration time
        self.acceleration_time_s = self.max_velocity_mm_per_sec.find_max() \
                              / STEPPER_MAX_ACCELERATION_MM_PER_S2
        # check if there is enough space to accelerate and brake, adjust time
        # S = a * t^2 / 2
        if STEPPER_MAX_ACCELERATION_MM_PER_S2 * self.acceleration_time_s ** 2 \
                > distance_xyz_mm:
            self.acceleration_time_s = math.sqrt(distance_xyz_mm /
                                                  STEPPER_MAX_ACCELERATION_MM_PER_S2)
            self.linear_time_s = 0.0
            # V = a * t -> V = 2 * S / t, take half of total distance for acceleration and braking
            self.max_velocity_mm_per_sec = self._distance_mm / self.acceleration_time_s
        else:
            # calculate linear time
            linear_distance_mm = distance_xyz_mm\
                                      - self.acceleration_time_s ** 2 \
                                      * STEPPER_MAX_ACCELERATION_MM_PER_S2
            self.linear_time_s = linear_distance_mm \
                                 / self.max_velocity_mm_per_sec.length()

    def _get_movement_parameters(self):
        """ Return movement parameters, see super class for details.
        """
        return self.acceleration_time_s, \
               self.linear_time_s, \
               self.max_velocity_mm_per_sec.find_max()

    def __linear(self, position_mm, distance_mm, velocity_mm_per_sec):
        """ Helper function for linear movement.
        """
        # check if need to calculate for this axis
        if distance_mm == 0.0 or position_mm >= distance_mm:
            return None
        # Linear movement, S = V * t -> t = S / V
        return position_mm / velocity_mm_per_sec

    def _interpolation_function(self, ix, iy, iz):
        """ Calculate interpolation values for linear movement, see super class
            for details.
        """
        t_x = self.__linear(ix / STEPPER_PULSES_PER_MM, self._distance_mm.x,
                            self.max_velocity_mm_per_sec.x)
        t_y = self.__linear(iy / STEPPER_PULSES_PER_MM, self._distance_mm.y,
                            self.max_velocity_mm_per_sec.y)
        t_z = self.__linear(iz / STEPPER_PULSES_PER_MM, self._distance_mm.z,
                            self.max_velocity_mm_per_sec.z)
        return t_x, t_y, t_z
