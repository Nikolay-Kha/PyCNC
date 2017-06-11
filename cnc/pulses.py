from __future__ import division
import logging

from cnc.config import *
from cnc.coordinates import *
from cnc.enums import *

SECONDS_IN_MINUTE = 60.0


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
        In the same way circular or other interpolation can be implemented
        based this class.
    """

    def __init__(self, delta):
        """ Create object. Do not create directly this object, inherit this
            class and implement interpolation function and related methods.
            All child have to call this method ( super().__init__() ).
            :param delta: overall movement delta in mm, uses for debug purpose.
        """
        self._iteration_x = 0
        self._iteration_y = 0
        self._iteration_z = 0
        self._iteration_e = 0
        self._iteration_direction = None
        self._acceleration_time_s = 0.0
        self._linear_time_s = 0.0
        self._2Vmax_per_a = 0.0
        self._delta = delta

    def _get_movement_parameters(self):
        """ Get parameters for interpolation. This method have to be
            reimplemented in parent classes and should calculate 3 parameters.
        :return: Tuple of three values:
                acceleration_time_s: time for accelerating and breaking motors
                                     during movement
                linear_time_s: time for uniform movement, it is total movement
                               time minus acceleration and braking time
                max_axis_velocity_mm_per_sec: maximum axis velocity of all
                                              axises during movement. Even if
                                              whole movement is accelerated,
                                              this value should be calculated
                                              as top velocity.
        """
        raise NotImplemented

    def _interpolation_function(self, ix, iy, iz, ie):
        """ Get function for interpolation path. This function should returned
            values as it is uniform movement. There is only one trick, function
            must be expressed in terms of position, i.e. t = S / V for linear,
            where S - distance would be increment on motor minimum step.
        :param ix: number of pulse for X axis.
        :param iy: number of pulse for Y axis.
        :param iz: number of pulse for Z axis.
        :param ie: number of pulse for E axis.
        :return: Two tuples. First is tuple is directions for each axis,
                 positive means forward, negative means reverse. Second is
                 tuple of times for each axis in us or None if movement for
                 axis is finished.
        """
        raise NotImplemented

    def __iter__(self):
        """ Get iterator.
        :return: iterable object.
        """
        (self._acceleration_time_s, self._linear_time_s,
         max_axis_velocity_mm_per_sec) = self._get_movement_parameters()
        # helper variable
        self._2Vmax_per_a = (2.0 * max_axis_velocity_mm_per_sec
                             / STEPPER_MAX_ACCELERATION_MM_PER_S2)
        self._iteration_x = 0
        self._iteration_y = 0
        self._iteration_z = 0
        self._iteration_e = 0
        self._iteration_direction = None
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
        d = self._acceleration_time_s ** 2 - self._2Vmax_per_a * bt
        if d > 0:
            d = math.sqrt(d)
        else:
            d = 0
        return 2.0 * self._acceleration_time_s + self._linear_time_s - d

    def __next__(self):
        # for python3
        return self.next()

    def next(self):
        """ Iterate pulses.
        :return: Tuple of five values:
                    - first is boolean value, if it is True, motors direction
                        should be changed and next pulse should performed in
                        this direction.
                    - values for all machine axises. For direction update,
                        positive values means forward movement, negative value
                        means reverse movement. For normal pulse, values are
                        represent time for the next pulse in microseconds.
                 This iteration strictly guarantees that next pulses time will
                 not be earlier in time then current. If there is no pulses
                 left StopIteration will be raised.
        """
        direction, (tx, ty, tz, te) = \
            self._interpolation_function(self._iteration_x, self._iteration_y,
                                         self._iteration_z, self._iteration_e)
        # check if direction update:
        if direction != self._iteration_direction:
            self._iteration_direction = direction
            return (True,) + direction
        # check condition to stop
        if tx is None and ty is None and tz is None and te is None:
            raise StopIteration

        # convert to real time
        m = None
        for i in (tx, ty, tz, te):
            if i is not None and (m is None or i < m):
                m = i
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
        if te is not None:
            if te > m:
                te = None
            else:
                te = am
                self._iteration_e += 1

        return False, tx, ty, tz, te

    def total_time_s(self):
        """ Get total time for movement.
        :return: time in seconds.
        """
        acceleration_time_s, linear_time_s, _ = self._get_movement_parameters()
        return acceleration_time_s * 2.0 + linear_time_s

    def delta(self):
        """ Get overall movement distance.
        :return: Movement distance for each axis in millimeters.
        """
        return self._delta


class PulseGeneratorLinear(PulseGenerator):
    def __init__(self, delta_mm, velocity_mm_per_min):
        """ Create pulse generator for linear interpolation.
        :param delta_mm: movement distance of each axis.
        :param velocity_mm_per_min: desired velocity.
        """
        super(PulseGeneratorLinear, self).__init__(delta_mm)
        # this class doesn't care about direction
        self._distance_mm = abs(delta_mm)  # type: Coordinates
        # velocity of each axis
        distance_total_mm = self._distance_mm.length()
        self.max_velocity_mm_per_sec = self._distance_mm * (
            velocity_mm_per_min / SECONDS_IN_MINUTE / distance_total_mm)
        # acceleration time
        self.acceleration_time_s = (self.max_velocity_mm_per_sec.find_max()
                                    / STEPPER_MAX_ACCELERATION_MM_PER_S2)
        # check if there is enough space to accelerate and brake, adjust time
        # S = a * t^2 / 2
        if STEPPER_MAX_ACCELERATION_MM_PER_S2 * self.acceleration_time_s ** 2 \
                > distance_total_mm:
            self.acceleration_time_s = \
                math.sqrt(distance_total_mm
                          / STEPPER_MAX_ACCELERATION_MM_PER_S2)
            self.linear_time_s = 0.0
            # V = a * t -> V = 2 * S / t, take half of total distance for
            # acceleration and braking
            self.max_velocity_mm_per_sec = (self._distance_mm
                                            / self.acceleration_time_s)
        else:
            # calculate linear time
            linear_distance_mm = distance_total_mm \
                                 - self.acceleration_time_s ** 2 \
                                 * STEPPER_MAX_ACCELERATION_MM_PER_S2
            self.linear_time_s = (linear_distance_mm
                                  / self.max_velocity_mm_per_sec.length())
        self._direction = (math.copysign(1, delta_mm.x),
                           math.copysign(1, delta_mm.y),
                           math.copysign(1, delta_mm.z),
                           math.copysign(1, delta_mm.e))

    def _get_movement_parameters(self):
        """ Return movement parameters, see super class for details.
        """
        return (self.acceleration_time_s,
                self.linear_time_s,
                self.max_velocity_mm_per_sec.find_max())

    @staticmethod
    def __linear(position_mm, distance_mm, velocity_mm_per_sec):
        """ Helper function for linear movement.
        """
        # check if need to calculate for this axis
        if distance_mm == 0.0 or position_mm >= distance_mm:
            return None
        # Linear movement, S = V * t -> t = S / V
        return position_mm / velocity_mm_per_sec

    def _interpolation_function(self, ix, iy, iz, ie):
        """ Calculate interpolation values for linear movement, see super class
            for details.
        """
        t_x = self.__linear(ix / STEPPER_PULSES_PER_MM_X, self._distance_mm.x,
                            self.max_velocity_mm_per_sec.x)
        t_y = self.__linear(iy / STEPPER_PULSES_PER_MM_Y, self._distance_mm.y,
                            self.max_velocity_mm_per_sec.y)
        t_z = self.__linear(iz / STEPPER_PULSES_PER_MM_Z, self._distance_mm.z,
                            self.max_velocity_mm_per_sec.z)
        t_e = self.__linear(ie / STEPPER_PULSES_PER_MM_E, self._distance_mm.e,
                            self.max_velocity_mm_per_sec.e)
        return self._direction, (t_x, t_y, t_z, t_e)


class PulseGeneratorCircular(PulseGenerator):
    def __init__(self, delta, radius, plane, direction, velocity):
        """ Create pulse generator for circular interpolation.
            Position calculates based on formulas:
            R^2 = x^2 + y^2
            x = R * sin(phi)
            y = R * cos(phi)
            phi = omega * t,   2 * pi / omega = 2 * pi * R / V
            phi = V * t / R
            omega is angular_velocity.
            so t = V / R * phi
            phi can be calculated based on steps position.
            Each axis can calculate circle phi base on iteration number, the
            only one difference, that there is four quarters of circle and
            signs for movement and solving expressions are different. So
            we use additional variables to control it.
            :param delta: finish position delta from the beginning, must be on
                          circle on specified plane. Zero means full circle.
            :param radius: vector to center of circle.
            :param plane: plane to interpolate.
            :param direction: clockwise or counterclockwise.
            :param velocity: velocity in mm per min.
        """
        super(PulseGeneratorCircular, self).__init__(delta)
        self._plane = plane
        self._direction = direction
        velocity = velocity / SECONDS_IN_MINUTE
        # Get circle start point and end point.
        if self._plane == PLANE_XY:
            sa = -radius.x
            sb = -radius.y
            ea = sa + delta.x
            eb = sb + delta.y
            apm = STEPPER_PULSES_PER_MM_X
            bpm = STEPPER_PULSES_PER_MM_Y
        elif self._plane == PLANE_YZ:
            sa = -radius.y
            sb = -radius.z
            ea = sa + delta.y
            eb = sb + delta.z
            apm = STEPPER_PULSES_PER_MM_Y
            bpm = STEPPER_PULSES_PER_MM_Z
        elif self._plane == PLANE_ZX:
            sa = -radius.z
            sb = -radius.x
            ea = sa + delta.z
            eb = sb + delta.x
            apm = STEPPER_PULSES_PER_MM_Z
            bpm = STEPPER_PULSES_PER_MM_X
        else:
            raise ValueError("Unknown plane")
        # adjust radius to fit into axises step.
        radius = (round(math.sqrt(sa * sa + sb * sb) * min(apm, bpm))
                  / min(apm, bpm))
        self._radius2 = radius * radius
        self._radius_a_pulses = int(radius * apm)
        self._radius_b_pulses = int(radius * bpm)
        self._start_a_pulses = int(sa * apm)
        self._start_b_pulses = int(sb * bpm)
        assert (round(math.sqrt(ea * ea + eb * eb) * min(apm, bpm))
                / min(apm, bpm) == radius), "Wrong end point"

        # Calculate angles and directions.
        start_angle = self.__angle(sa, sb)
        end_angle = self.__angle(ea, eb)
        delta_angle = end_angle - start_angle
        if delta_angle < 0 or (delta_angle == 0 and direction == CW):
            delta_angle += 2 * math.pi
        if direction == CCW:
            delta_angle -= 2 * math.pi
        if direction == CW:
            if start_angle >= math.pi:
                self._dir_b = 1
            else:
                self._dir_b = -1
            if math.pi / 2 <= start_angle < 3 * math.pi / 2:
                self._dir_a = -1
            else:
                self._dir_a = 1
        elif direction == CCW:
            if 0.0 < start_angle <= math.pi:
                self._dir_b = 1
            else:
                self._dir_b = -1
            if start_angle <= math.pi / 2 or start_angle > 3 * math.pi / 2:
                self._dir_a = -1
            else:
                self._dir_a = 1
        self._side_a = (self._start_b_pulses < 0
                        or (self._start_b_pulses == 0 and self._dir_b < 0))
        self._side_b = (self._start_a_pulses < 0
                        or (self._start_a_pulses == 0 and self._dir_a < 0))
        self._start_angle = start_angle
        logging.debug("start angle {}, end angle {}, delta {}".format(
                      start_angle * 180.0 / math.pi,
                      end_angle * 180.0 / math.pi,
                      delta_angle * 180.0 / math.pi))
        delta_angle = abs(delta_angle)
        self._delta_angle = delta_angle

        # calculate values for interpolation.

        # calculate travel distance for axis in circular move.
        self._iterations_a = 0
        self._iterations_b = 0
        end_angle_m = end_angle
        if start_angle >= end_angle:
            end_angle_m += 2 * math.pi
        quarter_start = int(start_angle / (math.pi / 2.0))
        quarter_end = int(end_angle_m / (math.pi / 2.0))
        if quarter_end - quarter_start >= 4:
            self._iterations_a = 4 * int(radius * apm)
            self._iterations_b = 4 * int(radius * apm)
        else:
            if quarter_start == quarter_end:
                self._iterations_a = int(abs(sa - ea) * apm)
                self._iterations_b = int(abs(sb - eb) * bpm)
            else:
                for r in range(quarter_start, quarter_end + 1):
                    i = r
                    if i >= 4:
                        i -= 4
                    if r == quarter_start:
                        if i == 0 or i == 2:
                            self._iterations_a += int(radius * apm) \
                                                  - int(abs(sa) * apm)
                        else:
                            self._iterations_a += int(abs(sa) * apm)
                        if i == 1 or i == 3:
                            self._iterations_b += int(radius * bpm) \
                                                  - int(abs(sb) * bpm)
                        else:
                            self._iterations_b += int(abs(sb) * bpm)
                    elif r == quarter_end:
                        if i == 0 or i == 2:
                            self._iterations_a += int(abs(ea) * apm)
                        else:
                            self._iterations_a += int(radius * apm) \
                                                  - int(abs(ea) * apm)
                        if i == 1 or i == 3:
                            self._iterations_b += int(abs(eb) * bpm)
                        else:
                            self._iterations_b += int(radius * bpm) \
                                                  - int(abs(eb) * bpm)
                    else:
                        self._iterations_a += int(radius * apm)
                        self._iterations_b += int(radius * bpm)
            if direction == CCW:
                self._iterations_a = 4 * int(radius * apm) - self._iterations_a
                self._iterations_b = 4 * int(radius * bpm) - self._iterations_b

        arc = delta_angle * radius
        e2 = delta.e * delta.e
        if self._plane == PLANE_XY:
            self._iterations_3rd = abs(delta.z) * STEPPER_PULSES_PER_MM_Z
            l = math.sqrt(arc * arc + delta.z * delta.z + e2)
            self._velocity_3rd = abs(delta.z) / l * velocity
            self._third_dir = math.copysign(1, delta.z)
        elif self._plane == PLANE_YZ:
            self._iterations_3rd = abs(delta.x) * STEPPER_PULSES_PER_MM_X
            l = math.sqrt(arc * arc + delta.x * delta.x + e2)
            self._velocity_3rd = abs(delta.x) / l * velocity
            self._third_dir = math.copysign(1, delta.x)
        elif self._plane == PLANE_ZX:
            self._iterations_3rd = abs(delta.y) * STEPPER_PULSES_PER_MM_Y
            l = math.sqrt(arc * arc + delta.y * delta.y + e2)
            self._velocity_3rd = abs(delta.y) / l * velocity
            self._third_dir = math.copysign(1, delta.y)
        else:
            raise ValueError("Unknown plane")
        self._iterations_e = abs(delta.e) * STEPPER_PULSES_PER_MM_E
        # Velocity splits with corresponding distance.
        circular_velocity = arc / l * velocity
        self._r_div_v = radius / circular_velocity
        self._e_velocity = abs(delta.e) / l * velocity
        self._e_dir = math.copysign(1, delta.e)
        self.max_velocity_mm_per_sec = max(circular_velocity,
                                           self._velocity_3rd, self._e_velocity)
        self.acceleration_time_s = (self.max_velocity_mm_per_sec
                                    / STEPPER_MAX_ACCELERATION_MM_PER_S2)
        if STEPPER_MAX_ACCELERATION_MM_PER_S2 * self.acceleration_time_s ** 2 \
                > l:
            self.acceleration_time_s = \
                math.sqrt(l / STEPPER_MAX_ACCELERATION_MM_PER_S2)
            self.linear_time_s = 0.0
            self.max_velocity_mm_per_sec = l / self.acceleration_time_s
        else:
            linear_distance_mm = l - self.acceleration_time_s ** 2 \
                                 * STEPPER_MAX_ACCELERATION_MM_PER_S2
            self.linear_time_s = linear_distance_mm / velocity

    @staticmethod
    def __angle(a, b):
        # Calculate angle of entry point (a, b) of circle with center in (0,0)
        angle = math.acos(b / math.sqrt(a * a + b * b))
        if a < 0:
            return 2 * math.pi - angle
        return angle

    def _get_movement_parameters(self):
        """ Return movement parameters, see super class for details.
        """
        return (self.acceleration_time_s,
                self.linear_time_s,
                self.max_velocity_mm_per_sec)

    @staticmethod
    def __circular_helper(start, i, radius, side, direction):
        np = start + direction * i
        if np > radius:
            np -= 2 * (np - radius)
            direction = -direction
            side = not side
        if np < -radius:
            np -= 2 * (np + radius)
            direction = -direction
            side = not side
        if np > radius:
            np -= 2 * (np - radius)
            direction = -direction
            side = not side
        return np, direction, side

    def __circular_find_time(self, a, b):
        angle = self.__angle(a, b)
        if self._direction == CW:
            delta_angle = angle - self._start_angle
        else:
            delta_angle = self._start_angle - angle
        if delta_angle <= 0:
            delta_angle += 2 * math.pi
        return self._r_div_v * delta_angle

    def __circular_a(self, i, pulses_per_mm):
        if i >= self._iterations_a:
            return self._dir_a, None
        a, direction, side = self.__circular_helper(self._start_a_pulses, i + 1,
                                                    self._radius_a_pulses,
                                                    self._side_a, self._dir_a)
        a /= pulses_per_mm
        # last item can be slightly more then end angle due to float precision
        if i + 1 == self._iterations_a:
            return direction, self._r_div_v * self._delta_angle
        b = math.sqrt(self._radius2 - a * a)
        if side:
            b = -b
        return direction, self.__circular_find_time(a, b)

    def __circular_b(self, i, pulses_per_mm):
        if i >= self._iterations_b:
            return self._dir_b, None
        b, direction, side = self.__circular_helper(self._start_b_pulses, i + 1,
                                                    self._radius_b_pulses,
                                                    self._side_b, self._dir_b)
        b /= pulses_per_mm
        # last item can be slightly more then end angle due to float precision
        if i + 1 == self._iterations_b:
            return direction, self._r_div_v * self._delta_angle
        a = math.sqrt(self._radius2 - b * b)
        if side:
            a = -a
        return direction, self.__circular_find_time(a, b)

    @staticmethod
    def __linear(i, total_i, pulses_per_mm, velocity):
        if i >= total_i:
            return None
        return i / pulses_per_mm / velocity

    def _interpolation_function(self, ix, iy, iz, ie):
        """ Calculate interpolation values for linear movement, see super class
            for details.
        """
        if self._plane == PLANE_XY:
            dx, tx = self.__circular_a(ix, STEPPER_PULSES_PER_MM_X)
            dy, ty = self.__circular_b(iy, STEPPER_PULSES_PER_MM_Y)
            tz = self.__linear(iz, self._iterations_3rd,
                               STEPPER_PULSES_PER_MM_Z, self._velocity_3rd)
            dz = self._third_dir
        elif self._plane == PLANE_YZ:
            dy, ty = self.__circular_a(iy, STEPPER_PULSES_PER_MM_Y)
            dz, tz = self.__circular_b(iz, STEPPER_PULSES_PER_MM_Z)
            tx = self.__linear(ix, self._iterations_3rd,
                               STEPPER_PULSES_PER_MM_X, self._velocity_3rd)
            dx = self._third_dir
        else:  # self._plane == PLANE_ZX:
            dz, tz = self.__circular_a(iz, STEPPER_PULSES_PER_MM_Z)
            dx, tx = self.__circular_b(ix, STEPPER_PULSES_PER_MM_X)
            ty = self.__linear(iy, self._iterations_3rd,
                               STEPPER_PULSES_PER_MM_Y, self._velocity_3rd)
            dy = self._third_dir
        te = self.__linear(ie, self._iterations_e, STEPPER_PULSES_PER_MM_E,
                           self._e_velocity)
        return (dx, dy, dz, self._e_dir), (tx, ty, tz, te)
