import unittest
import time

from cnc.coordinates import *
from cnc.gcode import *
from cnc.gmachine import *


class TestGMachine(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_reset(self):
        # reset() resets all configurable from gcode things.
        m = GMachine()
        m.do_command(GCode.parse_line("G20"))
        m.do_command(GCode.parse_line("G91"))
        m.do_command(GCode.parse_line("X1Y1Z1"))
        m.reset()
        m.do_command(GCode.parse_line("X3Y4Z5"))
        self.assertEqual(m.position(), Coordinates(3, 4, 5))

    def test_release(self):
        # release homes head.
        m = GMachine()
        m.do_command(GCode.parse_line("X1Y2Z3"))
        m.release()
        self.assertEqual(m.position(), Coordinates(0, 0, 0))

    def test_home(self):
        m = GMachine()
        m.do_command(GCode.parse_line("X1Y2Z3"))
        m.home()
        self.assertEqual(m.position(), Coordinates(0, 0, 0))

    def test_none(self):
        # GMachine must ignore None commands, since GCode.parse_line()
        # returns None if no gcode found in line.
        m = GMachine()
        m.do_command(None)
        self.assertEqual(m.position(), Coordinates(0, 0, 0))

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
        m.do_command(GCode.parse_line("G0X3Y2Z1"))
        self.assertEqual(m.position(), Coordinates(3, 2, 1))
        m.do_command(GCode.parse_line("G1X1Y2Z3"))
        self.assertEqual(m.position(), Coordinates(1, 2, 3))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1F-1"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1F999999"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1X-1Y0Z0"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1X0Y-1Z0"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G1X0Y0Z-1"))

    def test_g4(self):
        m = GMachine()
        st = time.time()
        m.do_command(GCode.parse_line("G4P0.5"))
        self.assertLess(0.5, time.time() - st)
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("G4P-0.5"))

    def test_g20_g21(self):
        m = GMachine()
        m.do_command(GCode.parse_line("G20"))
        m.do_command(GCode.parse_line("X3Y2Z1"))
        self.assertEqual(m.position(), Coordinates(76.2, 50.8, 25.4))
        m.do_command(GCode.parse_line("G21"))
        m.do_command(GCode.parse_line("X3Y2Z1"))
        self.assertEqual(m.position(), Coordinates(3, 2, 1))

    def test_g90_g91(self):
        m = GMachine()
        m.do_command(GCode.parse_line("G91"))
        m.do_command(GCode.parse_line("X1Y1Z1"))
        m.do_command(GCode.parse_line("X1Y1"))
        m.do_command(GCode.parse_line("X1"))
        self.assertEqual(m.position(), Coordinates(3, 2, 1))
        m.do_command(GCode.parse_line("X-1Y-1Z-1"))
        m.do_command(GCode.parse_line("G90"))
        m.do_command(GCode.parse_line("X1Y1Z1"))
        self.assertEqual(m.position(), Coordinates(1, 1, 1))

    def test_g90_g92(self):
        m = GMachine()
        m.do_command(GCode.parse_line("G92X100Y100Z100"))
        m.do_command(GCode.parse_line("X101Y102Z103"))
        self.assertEqual(m.position(), Coordinates(1, 2, 3))
        m.do_command(GCode.parse_line("G92X-1Y-1Z-1"))
        m.do_command(GCode.parse_line("X1Y1Z1"))
        self.assertEqual(m.position(), Coordinates(3, 4, 5))
        m.do_command(GCode.parse_line("G92X3Y4Z5"))
        m.do_command(GCode.parse_line("X0Y0Z0"))
        self.assertEqual(m.position(), Coordinates(0, 0, 0))
        m.do_command(GCode.parse_line("G90"))
        m.do_command(GCode.parse_line("X6Y7Z8"))
        self.assertEqual(m.position(), Coordinates(6, 7, 8))

    def test_m3_m5(self):
        m = GMachine()
        m.do_command(GCode.parse_line("M3S" + str(SPINDLE_MAX_RPM)))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("M3S-10"))
        self.assertRaises(GMachineException,
                          m.do_command, GCode.parse_line("M3S999999999"))
        m.do_command(GCode.parse_line("M5"))


if __name__ == '__main__':
    unittest.main()