import unittest

from cnc.coordinates import *


class TestCoordinates(unittest.TestCase):
    def setUp(self):
        self.default = Coordinates(96, 102, 150, 228)

    def tearDown(self):
        pass

    def test_constructor(self):
        # constructor rounds values to 10 digits after the point
        self.assertRaises(TypeError, Coordinates)
        c = Coordinates(1.00000000005, 2.00000000004, -3.5000000009, 0.0)
        self.assertEqual(c.x, 1.0000000001)
        self.assertEqual(c.y, 2.0)
        self.assertEqual(c.z, -3.5000000009)
        self.assertEqual(c.e, 0.0)

    def test_zero(self):
        c = Coordinates(0, 0, 0, 0)
        self.assertTrue(c.is_zero())

    def test_aabb(self):
        # aabb - Axis Aligned Bounded Box.
        # original method checks if point belongs aabb.
        p1 = Coordinates(0, 0, 0, 0)
        p2 = Coordinates(2, 2, 2, 0)
        c = Coordinates(1, 1, 1, 0)
        self.assertTrue(c.is_in_aabb(p1, p2))
        self.assertTrue(c.is_in_aabb(p2, p1))
        c = Coordinates(0, 0, 0, 0)
        self.assertTrue(c.is_in_aabb(p1, p2))
        c = Coordinates(2, 2, 2, 0)
        self.assertTrue(c.is_in_aabb(p1, p2))
        c = Coordinates(2, 3, 2, 0)
        self.assertFalse(c.is_in_aabb(p1, p2))
        c = Coordinates(-1, 1, 1, 0)
        self.assertFalse(c.is_in_aabb(p1, p2))
        c = Coordinates(1, 1, 3, 0)
        self.assertFalse(c.is_in_aabb(p1, p2))

    def test_length(self):
        c = Coordinates(-1, 0, 0, 0)
        self.assertEqual(c.length(), 1)
        c = Coordinates(0, 3, -4, 0)
        self.assertEqual(c.length(), 5)
        c = Coordinates(3, 4, 12, 0)
        self.assertEqual(c.length(), 13)
        c = Coordinates(1, 1, 1, 1)
        self.assertEqual(c.length(), 2)

    def test_round(self):
        # round works in another way then Python's round.
        # This round() rounds digits with specified step.
        c = Coordinates(1.5, -1.4, 3.05, 3.5)
        r = c.round(1, 1, 1, 1)
        self.assertEqual(r.x, 2.0)
        self.assertEqual(r.y, -1.0)
        self.assertEqual(r.z, 3.0)
        self.assertEqual(r.e, 4.0)
        r = c.round(0.25, 0.25, 0.25, 0.25)
        self.assertEqual(r.x, 1.5)
        self.assertEqual(r.y, -1.5)
        self.assertEqual(r.z, 3.0)
        self.assertEqual(r.e, 3.5)

    def test_max(self):
        self.assertEqual(self.default.find_max(), max(self.default.x,
                                                      self.default.y,
                                                      self.default.z,
                                                      self.default.e))

    # build-in function overriding tests
    def test_add(self):
        r = self.default + Coordinates(1, 2, 3, 4)
        self.assertEqual(r.x, self.default.x + 1)
        self.assertEqual(r.y, self.default.y + 2)
        self.assertEqual(r.z, self.default.z + 3)
        self.assertEqual(r.e, self.default.e + 4)

    def test_sub(self):
        r = self.default - Coordinates(1, 2, 3, 4)
        self.assertEqual(r.x, self.default.x - 1)
        self.assertEqual(r.y, self.default.y - 2)
        self.assertEqual(r.z, self.default.z - 3)
        self.assertEqual(r.e, self.default.e - 4)

    def test_mul(self):
        r = self.default * 2
        self.assertEqual(r.x, self.default.x * 2)
        self.assertEqual(r.y, self.default.y * 2)
        self.assertEqual(r.z, self.default.z * 2)
        self.assertEqual(r.e, self.default.e * 2)

    def test_div(self):
        r = self.default / 2
        self.assertEqual(r.x, self.default.x / 2)
        self.assertEqual(r.y, self.default.y / 2)
        self.assertEqual(r.z, self.default.z / 2)
        self.assertEqual(r.e, self.default.e / 2)

    def test_truediv(self):
        r = self.default / 3.0
        self.assertEqual(r.x, self.default.x / 3.0)
        self.assertEqual(r.y, self.default.y / 3.0)
        self.assertEqual(r.z, self.default.z / 3.0)
        self.assertEqual(r.e, self.default.e / 3.0)

    def test_eq(self):
        a = Coordinates(self.default.x, self.default.y, self.default.z,
                        self.default.e)
        self.assertTrue(a == self.default)
        a = Coordinates(-self.default.x, self.default.y, self.default.z,
                        self.default.e)
        self.assertFalse(a == self.default)
        a = Coordinates(self.default.x, -self.default.y, self.default.z,
                        self.default.e)
        self.assertFalse(a == self.default)
        a = Coordinates(self.default.x, self.default.y, -self.default.z,
                        self.default.e)
        self.assertFalse(a == self.default)
        a = Coordinates(self.default.x, self.default.y, self.default.z,
                        -self.default.e)
        self.assertFalse(a == self.default)

    def test_str(self):
        self.assertTrue(isinstance(str(self.default), str))

    def test_abs(self):
        c = Coordinates(-1, -2.5, -99, -23)
        # noinspection PyTypeChecker
        r = abs(c)
        self.assertEqual(r.x, 1.0)
        self.assertEqual(r.y, 2.5)
        self.assertEqual(r.z, 99.0)
        self.assertEqual(r.e, 23.0)


if __name__ == '__main__':
    unittest.main()
