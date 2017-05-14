from __future__ import division
import time
import logging

from cnc import hal
from cnc.coordinates import Coordinates
from cnc.config import *


class GMachineException(Exception):
    """ Exceptions while processing gcode line.
    """
    pass


class GMachine(object):
    """ Main object which control and keep state of whole machine: steppers,
        spindle, extruder etc
    """
    def __init__(self):
        """ Initialization.
        """
        self._position = Coordinates(0.0, 0.0, 0.0)
        # init variables
        self._velocity = 0
        self._spindle_rpm = 0
        self._pause = 0
        self._local = None
        self._convertCoordinates = 0
        self._absoluteCoordinates = 0
        self.reset()
        hal.init()

    def release(self):
        """ Return machine to original position and free all resources.
        """
        self._spindle(0)
        self.home()
        hal.deinit()

    def reset(self):
        """ Reinitialize all program configurable thing.
        """
        self._velocity = 1000
        self._spindle_rpm = 1000
        self._pause = 0
        self._local = Coordinates(0.0, 0.0, 0.0)
        self._convertCoordinates = 1.0
        self._absoluteCoordinates = True

    def _spindle(self, spindle_speed):
        hal.join()
        hal.spindle_control(100.0 * spindle_speed / SPINDLE_MAX_RPM)

    def _move(self, delta, velocity):
        delta = delta.round(1.0 / STEPPER_PULSES_PER_MM)
        if delta.is_zero():
            return
        np = self._position + delta
        if not np.is_in_aabb(Coordinates(0.0, 0.0, 0.0),
                             Coordinates(TABLE_SIZE_X_MM, TABLE_SIZE_Y_MM, TABLE_SIZE_Z_MM)):
            raise GMachineException("out of effective area")
        hal.move_linear(delta, velocity)
        # save position
        self._position = np

    def home(self):
        """ Move head to park position
        """
        d = Coordinates(0, 0, -self._position.z)
        self._move(d, STEPPER_MAX_VELOCITY_MM_PER_MIN)
        d = Coordinates(-self._position.x, -self._position.y, 0)
        self._move(d, STEPPER_MAX_VELOCITY_MM_PER_MIN)

    def position(self):
        """ Return current machine position (after the latest command)
            Note that hal might still be moving motors and in this case
            function will block until motors stops.
            This function for tests only.
        """
        hal.join()
        return self._position

    def do_command(self, gcode):
        """ Perform action.
        :param gcode: GCode object which represent one gcode line
        """
        if gcode is None:
            return
        logging.debug("got command " + str(gcode.params))
        # read command
        c = gcode.command()
        if c is None and gcode.has_coordinates():
            c = 'G1'
        # read parameters
        if self._absoluteCoordinates:
            coord = gcode.coordinates(self._position, self._convertCoordinates)
            coord = coord + self._local
            delta = coord - self._position
        else:
            delta = gcode.coordinates(Coordinates(0.0, 0.0, 0.0), self._convertCoordinates)
            coord = self._position + delta
        velocity = gcode.get('F', self._velocity)
        spindle_rpm = gcode.get('S', self._spindle_rpm)
        pause = gcode.get('P', self._pause)
        # check parameters
        if velocity <= 0 or velocity > STEPPER_MAX_VELOCITY_MM_PER_MIN:
            raise GMachineException("bad feed speed")
        if spindle_rpm < 0 or spindle_rpm > SPINDLE_MAX_RPM:
            raise GMachineException("bad spindle speed")
        if pause < 0:
            raise GMachineException("bad delay")
        # select command and run it
        if c == 'G0':  # rapid move
            self._move(delta, STEPPER_MAX_VELOCITY_MM_PER_MIN)
        elif c == 'G1':  # linear interpolation
            self._move(delta, velocity)
        elif c == 'G4':  # delay in s
            hal.join()
            time.sleep(pause)
        elif c == 'G20':  # switch to inches
            self._convertCoordinates = 25.4
        elif c == 'G21':  # switch to mm
            self._convertCoordinates = 1.0
        elif c == 'G28':  # home
            self.home()
        elif c == 'G90':  # switch to absolute coords
            self._absoluteCoordinates = True
        elif c == 'G91':  # switch to relative coords
            self._absoluteCoordinates = False
        elif c == 'G92':  # switch to local coords
            self._local = self._position - \
                          gcode.coordinates(Coordinates(0.0, 0.0, 0.0), self._convertCoordinates)
        elif c == 'M3':  # spinle on
            self._spindle(spindle_rpm)
        elif c == 'M5':  # spindle off
            self._spindle(0)
        elif c == 'M2' or c == 'M30':  # program finish, reset everything.
            self.reset()
        elif c == 'M111':  # enable debug
            logging.getLogger().setLevel(logging.DEBUG)
        elif c is None:  # command not specified(for example, just F was passed)
            pass
        else:
            raise GMachineException("unknown command")
        # save parameters on success
        self._velocity = velocity
        self._spindle_rpm = spindle_rpm
        self._pause = pause
        logging.debug("position {}, {}, {}".format(
            self._position.x, self._position.y, self._position.z))
