import unittest

from cnc.gcode import *
from cnc.gmachine import *
from cnc.coordinates import *
from cnc.heater import *
from cnc.pid import *
from cnc.config import *


class TestGMachine(unittest.TestCase):
    def setUp(self):
        Pid.FIX_TIME_S = 0.01
        Heater.LOOP_INTERVAL_S = 0.001

    def tearDown(self):
        pass

    def test_reset(self):
        # reset() resets all configurable from gcode things.
        m = GMachine()
        m.do_command(GCode.parse_line("G20"))
        m.do_command(GCode.parse_line("G91"))
        m.do_command(GCode.parse_line("X1Y1Z1"))
        m.reset()
        m.do_command(GCode.parse_line("X3Y4Z5E6"))
        self.assertEqual(m.position(), Coordinates(3, 4, 5, 6))

    def test_safe_zero(self):
        m = GMachine()
        m.do_command(GCode.parse_line("X1Y2Z3E4"))
        m.safe_zero()
        self.assertEqual(m.position(), Coordinates(0, 0, 0, 4))

    def test_none(self):
        # GMachine must ignore None commands, since GCode.parse_line()
        # returns None if no gcode found in line.
        m = GMachine()
        m.do_command(None)
        self.assertEqual(m.position(), Coordinates(0, 0, 0, 0))

    def test_unknown(self):
        # Test commands which doesn't exists
        m = GMachine()
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G99699X1Y2Z3"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("M99699"))

    # Test gcode commands.
    def test_g0_g1(self):
        m = GMachine()
        m.do_command(GCode.parse_line("G0X10Y10Z11"))
        self.assertEqual(m.position(), Coordinates(10, 10, 11, 0))
        m.do_command(GCode.parse_line("G0X3Y2Z1E-2"))
        self.assertEqual(m.position(), Coordinates(3, 2, 1, -2))
        m.do_command(GCode.parse_line("G1X1Y2Z3E4"))
        self.assertEqual(m.position(), Coordinates(1, 2, 3, 4))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1F-1"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1X-1Y0Z0"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1X0Y-1Z0"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1X0Y0Z-1"))

    def test_feed_rate(self):
        PulseGenerator.AUTO_VELOCITY_ADJUSTMENT = False
        m = GMachine()
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1X1F-1"))
        cl = "G1X1F" + str(MIN_VELOCITY_MM_PER_MIN - 0.0000001)
        self.assertRaises(GMachineException, m.do_command,
                          GCode.parse_line(cl))
        m.do_command(GCode.parse_line("G1X100F"
                                      + str(MAX_VELOCITY_MM_PER_MIN_X)))
        m.do_command(GCode.parse_line("G1Y100F"
                                      + str(MAX_VELOCITY_MM_PER_MIN_Y)))
        m.do_command(GCode.parse_line("G1Z100F"
                                      + str(MAX_VELOCITY_MM_PER_MIN_Z)))
        m.do_command(GCode.parse_line("G1E100F"
                                      + str(MAX_VELOCITY_MM_PER_MIN_E)))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1X0F999999"))
        s = "G1X0F" + str(MAX_VELOCITY_MM_PER_MIN_X + 1)
        self.assertRaises(GMachineException, m.do_command, GCode.parse_line(s))
        s = "G1Y0F" + str(MAX_VELOCITY_MM_PER_MIN_Y + 1)
        self.assertRaises(GMachineException, m.do_command, GCode.parse_line(s))
        s = "G1Z0F" + str(MAX_VELOCITY_MM_PER_MIN_Z + 1)
        self.assertRaises(GMachineException, m.do_command, GCode.parse_line(s))
        s = "G1E0F" + str(MAX_VELOCITY_MM_PER_MIN_E + 1)
        self.assertRaises(GMachineException, m.do_command, GCode.parse_line(s))
        PulseGenerator.AUTO_VELOCITY_ADJUSTMENT = True
        m.do_command(GCode.parse_line("G1X10Y10Z10F9999999999999999999"))
        m.do_command(GCode.parse_line("G2I0.1F9999999999999999999"))
        m.do_command(GCode.parse_line("G2I10F9999999999999999999"))
        PulseGenerator.AUTO_VELOCITY_ADJUSTMENT = AUTO_VELOCITY_ADJUSTMENT

    def test_g2_g3(self):
        m = GMachine()
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G3I1J1F-1"))
        m.do_command(GCode.parse_line("G19"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G3I1J0K0"))
        m.do_command(GCode.parse_line("G18"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G3I0J1K0"))
        m.do_command(GCode.parse_line("G17"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G3I0J0K1"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G2X99999999Y99999999"
                                                         "I1J1"))
        self.assertRaises(GMachineException,
                          m.do_command,
                          GCode.parse_line("G2X2Y2Z99999999I1J1"))
        self.assertEqual(m.position(), Coordinates(0, 0, 0, 0))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G2X4Y4I2J2"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G3X4Y4I2J2"))
        m.do_command(GCode.parse_line("G17"))
        m.do_command(GCode.parse_line("G1X1"))
        m.do_command(GCode.parse_line("G2J1"))
        m.do_command(GCode.parse_line("G3J1"))
        self.assertEqual(m.position(), Coordinates(1, 0, 0, 0))
        m.do_command(GCode.parse_line("G1X10Y10"))
        m.do_command(GCode.parse_line("G2X9I1"))
        self.assertEqual(m.position(), Coordinates(9, 10, 0, 0))
        m.do_command(GCode.parse_line("G19"))
        m.do_command(GCode.parse_line("G1X10Y10Z10"))
        m.do_command(GCode.parse_line("G3Y8K1"))
        self.assertEqual(m.position(), Coordinates(10, 8, 10, 0))
        m.do_command(GCode.parse_line("G17"))
        m.do_command(GCode.parse_line("G1X5Y5Z0"))
        m.do_command(GCode.parse_line("G2X0Y0Z5I-2J-2"))
        self.assertEqual(m.position(), Coordinates(0, 0, 5, 0))
        m.do_command(GCode.parse_line("G17"))
        m.do_command(GCode.parse_line("G1X90Y90"))
        m.do_command(GCode.parse_line("G2X90Y70I-5J-5"))
        self.assertEqual(m.position(), Coordinates(90, 70, 5, 0))
        m.do_command(GCode.parse_line("G18"))
        m.do_command(GCode.parse_line("G1X90Y90Z20E0"))
        m.do_command(GCode.parse_line("G2Z20X70I-5K-5E22"))
        self.assertEqual(m.position(), Coordinates(70, 90, 20, 22))
        m.do_command(GCode.parse_line("G19"))
        m.do_command(GCode.parse_line("G1X90Y90Z20"))
        m.do_command(GCode.parse_line("G2Y90Z0J-5K-5E27"))
        self.assertEqual(m.position(), Coordinates(90, 90, 0, 27))

    def test_g4(self):
        m = GMachine()
        st = time.time()
        m.do_command(GCode.parse_line("G4P0.5"))
        self.assertLess(0.5, time.time() - st)
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G4P-0.5"))

    def test_g17_g18_g19(self):
        m = GMachine()
        m.do_command(GCode.parse_line("G19"))
        self.assertEqual(m.plane(), PLANE_YZ)
        m.do_command(GCode.parse_line("G18"))
        self.assertEqual(m.plane(), PLANE_ZX)
        m.do_command(GCode.parse_line("G17"))
        self.assertEqual(m.plane(), PLANE_XY)

    def test_g20_g21(self):
        m = GMachine()
        m.do_command(GCode.parse_line("G20"))
        m.do_command(GCode.parse_line("X3Y2Z1E0.5"))
        self.assertEqual(m.position(), Coordinates(76.2, 50.8, 25.4, 12.7))
        m.do_command(GCode.parse_line("G21"))
        m.do_command(GCode.parse_line("X3Y2Z1E0.5"))
        self.assertEqual(m.position(), Coordinates(3, 2, 1, 0.5))

    def test_g90_g91(self):
        m = GMachine()
        m.do_command(GCode.parse_line("G91"))
        m.do_command(GCode.parse_line("X1Y1Z1E1"))
        m.do_command(GCode.parse_line("X1Y1Z1"))
        m.do_command(GCode.parse_line("X1Y1"))
        m.do_command(GCode.parse_line("X1"))
        self.assertEqual(m.position(), Coordinates(4, 3, 2, 1))
        m.do_command(GCode.parse_line("X-1Y-1Z-1E-1"))
        m.do_command(GCode.parse_line("G90"))
        m.do_command(GCode.parse_line("X1Y1Z1E1"))
        self.assertEqual(m.position(), Coordinates(1, 1, 1, 1))

    def test_g53_g92(self):
        m = GMachine()
        m.do_command(GCode.parse_line("G92X100Y100Z100E100"))
        m.do_command(GCode.parse_line("X101Y102Z103E104"))
        self.assertEqual(m.position(), Coordinates(1, 2, 3, 4))
        m.do_command(GCode.parse_line("G92X-1Y-1Z-1E-1"))
        m.do_command(GCode.parse_line("X1Y1Z1E1"))
        self.assertEqual(m.position(), Coordinates(3, 4, 5, 6))
        m.do_command(GCode.parse_line("G92X3Y4Z5E6"))
        m.do_command(GCode.parse_line("X0Y0Z0E0"))
        self.assertEqual(m.position(), Coordinates(0, 0, 0, 0))
        m.do_command(GCode.parse_line("X1Y2Z3E4"))
        self.assertEqual(m.position(), Coordinates(1, 2, 3, 4))
        m.do_command(GCode.parse_line("G53"))
        m.do_command(GCode.parse_line("X6Y7Z8E9"))
        self.assertEqual(m.position(), Coordinates(6, 7, 8, 9))
        m.do_command(GCode.parse_line("G92E0"))
        m.do_command(GCode.parse_line("X6Y7Z8E1"))
        self.assertEqual(m.position(), Coordinates(6, 7, 8, 10))
        m.do_command(GCode.parse_line("G92"))
        m.do_command(GCode.parse_line("X1Y1Z1E1"))
        self.assertEqual(m.position(), Coordinates(7, 8, 9, 11))

    def test_g53_g91_g92(self):
        m = GMachine()
        m.do_command(GCode.parse_line("G92X-50Y-60Z-70E-80"))
        m.do_command(GCode.parse_line("X-45Y-55Z-65E-75"))
        self.assertEqual(m.position(), Coordinates(5, 5, 5, 5))
        m.do_command(GCode.parse_line("G91"))
        m.do_command(GCode.parse_line("X-1Y-2Z-3E-4"))
        self.assertEqual(m.position(), Coordinates(4, 3, 2, 1))

    def test_m3_m5(self):
        m = GMachine()
        m.do_command(GCode.parse_line("M3S" + str(SPINDLE_MAX_RPM)))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("M3S-10"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("M3S999999999"))
        m.do_command(GCode.parse_line("M5"))

    def test_m104_m109(self):
        m = GMachine()
        m.do_command(GCode.parse_line("M104S"+str(MIN_TEMPERATURE)))
        self.assertEqual(m.extruder_target_temperature(), MIN_TEMPERATURE)
        m.do_command(GCode.parse_line("M104S0"))
        self.assertEqual(m.extruder_target_temperature(), 0)
        # blocking heating should be called with max temperature since virtual
        # hal always return this temperature.
        m.do_command(GCode.parse_line("M109S" + str(EXTRUDER_MAX_TEMPERATURE)))
        self.assertEqual(m.extruder_target_temperature(),
                         EXTRUDER_MAX_TEMPERATURE)
        m.do_command(GCode.parse_line("M104S0"))
        self.assertEqual(m.extruder_target_temperature(), 0)
        self.assertRaises(GMachineException, m.do_command,
                          GCode.parse_line("M104S"+str(MIN_TEMPERATURE - 1)))
        et = EXTRUDER_MAX_TEMPERATURE + 1
        self.assertRaises(GMachineException, m.do_command,
                          GCode.parse_line("M109S" + str(et)))
        self.assertRaises(GMachineException, m.do_command,
                          GCode.parse_line("M109"))

    def test_m106_m107(self):
        m = GMachine()
        m.do_command(GCode.parse_line("M106"))
        self.assertTrue(m.fan_state())
        m.do_command(GCode.parse_line("M106S0"))
        self.assertFalse(m.fan_state())
        m.do_command(GCode.parse_line("M106S123"))
        self.assertTrue(m.fan_state())
        m.do_command(GCode.parse_line("M107"))
        self.assertFalse(m.fan_state())
        # check auto fan feature
        m.AUTO_FAN_ON = True
        m.do_command(GCode.parse_line("M104S" + str(MIN_TEMPERATURE)))
        self.assertTrue(m.fan_state())
        m.do_command(GCode.parse_line("M104S0"))
        self.assertTrue(m.fan_state())
        m.do_command(GCode.parse_line("M107"))
        self.assertFalse(m.fan_state())
        m.AUTO_FAN_ON = False

    def test_m140_m190(self):
        m = GMachine()
        m.do_command(GCode.parse_line("M140S"+str(MIN_TEMPERATURE)))
        self.assertEqual(m.bed_target_temperature(), MIN_TEMPERATURE)
        m.do_command(GCode.parse_line("M140S0"))
        self.assertEqual(m.bed_target_temperature(), 0)
        # blocking heating should be called with max temperature since virtual
        # hal always return this temperature.
        m.do_command(GCode.parse_line("M190S" + str(BED_MAX_TEMPERATURE)))
        self.assertEqual(m.bed_target_temperature(), BED_MAX_TEMPERATURE)
        m.do_command(GCode.parse_line("M190S0"))
        self.assertEqual(m.bed_target_temperature(), 0)
        self.assertRaises(GMachineException, m.do_command,
                          GCode.parse_line("M140S"+str(MIN_TEMPERATURE - 1)))
        self.assertRaises(GMachineException, m.do_command,
                          GCode.parse_line("M190S"
                                           + str(BED_MAX_TEMPERATURE + 1)))
        self.assertRaises(GMachineException, m.do_command,
                          GCode.parse_line("M190"))


if __name__ == '__main__':
    unittest.main()
