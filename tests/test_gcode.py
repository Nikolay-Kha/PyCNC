import unittest

from cnc.gcode import *


class TestGCode(unittest.TestCase):
    def setUp(self):
        self.default = Coordinates(-7, 8, 9, -10)

    def tearDown(self):
        pass

    def test_constructor(self):
        # GCode shouldn't be created with constructor, but since it uses
        # internally, let's check it.
        self.assertRaises(TypeError, GCode)
        gc = GCode({"X": "1", "Y": "-2", "Z": "0", "E": 99, "G": "1"})
        self.assertEqual(gc.coordinates(self.default, 1).x, 1.0)
        self.assertEqual(gc.coordinates(self.default, 1).y, -2.0)
        self.assertEqual(gc.coordinates(self.default, 1).z, 0.0)
        self.assertEqual(gc.coordinates(self.default, 1).e, 99.0)

    def test_parser(self):
        gc = GCode.parse_line("G1X2Y-3Z4E1.5")
        self.assertEqual(gc.command(), "G1")
        self.assertEqual(gc.coordinates(self.default, 1).x, 2.0)
        self.assertEqual(gc.coordinates(self.default, 1).y, -3.0)
        self.assertEqual(gc.coordinates(self.default, 1).z, 4.0)
        self.assertEqual(gc.coordinates(self.default, 1).e, 1.5)
        gc = GCode.parse_line("")
        self.assertIsNone(gc)

    def test_defaults(self):
        # defaults are values which should be returned if corresponding
        # value doesn't exist in gcode.
        default = Coordinates(11, -12, 14, -10)
        gc = GCode.parse_line("G1")
        self.assertEqual(gc.coordinates(default, 1).x, 11.0)
        self.assertEqual(gc.coordinates(default, 1).y, -12.0)
        self.assertEqual(gc.coordinates(default, 1).z, 14.0)
        self.assertEqual(gc.coordinates(default, 1).e, -10.0)

    def test_commands(self):
        gc = GCode({"G": "1"})
        self.assertEqual(gc.command(), "G1")
        gc = GCode.parse_line("M99")
        self.assertEqual(gc.command(), "M99")

    def test_case_sensitivity(self):
        gc = GCode.parse_line("m111")
        self.assertEqual(gc.command(), "M111")
        gc = GCode.parse_line("g2X3y-4Z5e6")
        self.assertEqual(gc.command(), "G2")
        self.assertEqual(gc.coordinates(self.default, 1).x, 3.0)
        self.assertEqual(gc.coordinates(self.default, 1).y, -4.0)
        self.assertEqual(gc.coordinates(self.default, 1).z, 5.0)
        self.assertEqual(gc.coordinates(self.default, 1).e, 6.0)

    def test_has_coordinates(self):
        gc = GCode.parse_line("X2Y-3Z4")
        self.assertTrue(gc.has_coordinates())
        gc = GCode.parse_line("G1")
        self.assertFalse(gc.has_coordinates())
        gc = GCode.parse_line("X1")
        self.assertTrue(gc.has_coordinates())
        gc = GCode.parse_line("Y1")
        self.assertTrue(gc.has_coordinates())
        gc = GCode.parse_line("Z1")
        self.assertTrue(gc.has_coordinates())
        gc = GCode.parse_line("E1")
        self.assertTrue(gc.has_coordinates())

    def test_radius(self):
        gc = GCode.parse_line("G2I1J2K3")
        self.assertEqual(gc.radius(self.default, 1).x, 1)
        self.assertEqual(gc.radius(self.default, 1).y, 2)
        self.assertEqual(gc.radius(self.default, 1).z, 3)
        gc = GCode.parse_line("G3")
        self.assertEqual(gc.radius(self.default, 1).x, self.default.x)
        self.assertEqual(gc.radius(self.default, 1).y, self.default.y)
        self.assertEqual(gc.radius(self.default, 1).z, self.default.z)

    def test_multiply(self):
        # getting coordinates could modify value be specified multiplier.
        gc = GCode.parse_line("X2 Y-3 Z4 E5")
        self.assertEqual(gc.coordinates(self.default, 25.4).x, 50.8)
        self.assertEqual(gc.coordinates(self.default, 2).y, -6)
        self.assertEqual(gc.coordinates(self.default, 0).y, 0)
        self.assertEqual(gc.coordinates(self.default, 5).e, 25)

    def test_whitespaces(self):
        gc = GCode.parse_line("X1 Y2")
        self.assertEqual(gc.coordinates(self.default, 1).x, 1.0)
        self.assertEqual(gc.coordinates(self.default, 1).y, 2.0)
        gc = GCode.parse_line("X 3 Y4")
        self.assertEqual(gc.coordinates(self.default, 1).x, 3.0)
        self.assertEqual(gc.coordinates(self.default, 1).y, 4.0)
        gc = GCode.parse_line("X 5 Y\t 6")
        self.assertEqual(gc.coordinates(self.default, 1).x, 5.0)
        self.assertEqual(gc.coordinates(self.default, 1).y, 6.0)
        gc = GCode.parse_line(" \tX\t\t  \t\t7\t ")
        self.assertEqual(gc.coordinates(self.default, 1).x, 7.0)

    def test_errors(self):
        self.assertRaises(GCodeException, GCode.parse_line, "X1X1")
        self.assertRaises(GCodeException, GCode.parse_line, "X1+Y1")
        self.assertRaises(GCodeException, GCode.parse_line, "X1-Y1")
        self.assertRaises(GCodeException, GCode.parse_line, "~Y1")
        self.assertRaises(GCodeException, GCode.parse_line, "Y")
        self.assertRaises(GCodeException, GCode.parse_line, "abracadabra")
        self.assertRaises(GCodeException, GCode.parse_line, "G1M1")
        self.assertRaises(GCodeException, GCode.parse_line, "x 1 y 1 z 1 X 1")

    def test_comments(self):
        self.assertIsNone(GCode.parse_line("; some text"))
        self.assertIsNone(GCode.parse_line("    \t   \t ; some text"))
        self.assertIsNone(GCode.parse_line("(another comment)"))
        gc = GCode.parse_line("X2.5 ; end of line comment")
        self.assertEqual(gc.coordinates(self.default, 1).x, 2.5)
        gc = GCode.parse_line("X2 Y(inline comment)7")
        self.assertEqual(gc.coordinates(self.default, 1).x, 2.0)
        self.assertEqual(gc.coordinates(self.default, 1).y, 7.0)
        gc = GCode.parse_line("X2 Y(inline comment)3 \t(one more comment) "
                              "\tz4 ; multi comment test")
        self.assertEqual(gc.coordinates(self.default, 1).x, 2.0)
        self.assertEqual(gc.coordinates(self.default, 1).y, 3.0)
        self.assertEqual(gc.coordinates(self.default, 1).z, 4.0)


if __name__ == '__main__':
    unittest.main()
