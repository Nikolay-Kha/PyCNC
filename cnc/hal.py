# This implementation allows to use different hardware.
# Imported module contains functions for hardware access fo some board/SoC.
# List of HAL methods that should be implemented in each module:
#    def init():
#        """ Initialize GPIO pins and machine itself.
#        """
#        do_something()
#
#
#    def spindle_control(percent):
#        """ Spindle control implementation.
#        :param percent: Spindle speed in percent 0..100. 0 turns spindle off.
#        """
#        do_something()
#
#
#    def fan_control(on_off):
#        """
#        Cooling fan control.
#        :param on_off: boolean value if fan is enabled.
#        """
#        do_something()
#
#
#    def extruder_heater_control(percent):
#        """ Extruder heater control.
#        :param percent: heater power in percent 0..100. 0 turns heater off.
#        """
#        do_something()
#
#
#    def bed_heater_control(percent):
#        """ Hot bed heater control.
#        :param percent: heater power in percent 0..100. 0 turns heater off.
#        """
#        do_something()
#
#
#    def get_extruder_temperature():
#        """ Measure extruder temperature.
#        Can raise OSError or IOError on any issue with sensor.
#        :return: temperature in Celsius.
#        """
#        return measure()
#
#
#    def get_bed_temperature():
#        """ Measure bed temperature.
#        Can raise OSError or IOError on any issue with sensor.
#        :return: temperature in Celsius.
#        """
#        return measure()
#
#
#    def disable_steppers():
#        """ Disable all steppers until any movement occurs.
#        """
#        do_something()
#
#
#    def calibrate(x, y, z):
#        """ Move head to home position till end stop switch will be triggered.
#        Do not return till all procedures are completed.
#        :param x: boolean, True to calibrate X axis.
#        :param y: boolean, True to calibrate Y axis.
#        :param z: boolean, True to calibrate Z axis.
#        :return: boolean, True if all specified end stops were triggered.
#        """
#        return do_something()
#
#
#    def move(generator):
#        """ Move head to according pulses in PulseGenerator.
#        :param generator: PulseGenerator object
#        """
#        do_something()
#
#
#    def join():
#        """ Wait till motors work.
#        """
#        do_something()
#
#
#    def deinit():
#        """ De-initialise hal, stop any hardware.
#        """
#        do_something()


# check which module to import
try:
    from cnc.hal_raspberry.hal import *
except ImportError:
    print("----- Hardware not detected, using virtual environment -----")
    print("----- Use M111 command to enable more detailed debug -----")
    from cnc.hal_virtual import *

# check if all methods that is needed is implemented
if 'init' not in locals():
    raise NotImplementedError("hal.init() not implemented")
if 'spindle_control' not in locals():
    raise NotImplementedError("hal.spindle_control() not implemented")
if 'fan_control' not in locals():
    raise NotImplementedError("hal.fan_control() not implemented")
if 'extruder_heater_control' not in locals():
    raise NotImplementedError("hal.extruder_heater_control() not implemented")
if 'bed_heater_control' not in locals():
    raise NotImplementedError("hal.bed_heater_control() not implemented")
if 'get_extruder_temperature' not in locals():
    raise NotImplementedError("hal.get_extruder_temperature() not implemented")
if 'get_bed_temperature' not in locals():
    raise NotImplementedError("hal.get_bed_temperature() not implemented")
if 'disable_steppers' not in locals():
    raise NotImplementedError("hal.disable_steppers() not implemented")
if 'calibrate' not in locals():
    raise NotImplementedError("hal.calibrate() not implemented")
if 'move' not in locals():
    raise NotImplementedError("hal.move() not implemented")
if 'join' not in locals():
    raise NotImplementedError("hal.join() not implemented")
if 'deinit' not in locals():
    raise NotImplementedError("hal.deinit() not implemented")
