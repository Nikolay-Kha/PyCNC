# This implementation allows to use different hardware.
# Imported module contains functions for hardware access fo some board/SoC.
# List of HAL methods that should be implemented in each module:
#    def init():
#        """ Initialize GPIO pins and machine itself, including calibration if
#            needed. Do not return till all procedure is completed.
#        """
#        logging.info("initialize hal")
#        do_something()
#
#
#    def spindle_control(percent):
#        """ Spindle control implementation.
#        :param percent: Spindle speed in percent. 0 turns spindle off.
#        """
#        logging.info("spindle control: {}%".format(percent))
#        do_something()
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
if 'move' not in locals():
    raise NotImplementedError("hal.move() not implemented")
if 'join' not in locals():
    raise NotImplementedError("hal.join() not implemented")
if 'deinit' not in locals():
    raise NotImplementedError("hal.deinit() not implemented")
