import unittest

from cnc.pulses import *
from cnc.config import *
from cnc.coordinates import *
from cnc import hal_virtual


class TestPulses(unittest.TestCase):
    def setUp(self):
        self.v = STEPPER_MAX_VELOCITY_MM_PER_MIN

    def tearDown(self):
        pass

    def test_zero(self):
        # PulseGenerator should never receive empty movement.
        self.assertRaises(ZeroDivisionError,
                          PulseGeneratorLinear,
                          Coordinates(0, 0, 0, 0), self.v)
        self.assertRaises(ZeroDivisionError, PulseGeneratorCircular,
                          Coordinates(0, 0, 0, 0), Coordinates(0, 0, 9, 9),
                          PLANE_XY, CW, self.v)
        self.assertRaises(ZeroDivisionError, PulseGeneratorCircular,
                          Coordinates(0, 0, 0, 0), Coordinates(9, 0, 0, 9),
                          PLANE_YZ, CW, self.v)
        self.assertRaises(ZeroDivisionError, PulseGeneratorCircular,
                          Coordinates(0, 0, 0, 0), Coordinates(0, 9, 0, 9),
                          PLANE_ZX, CW, self.v)

    def test_step_linear(self):
        # Check if PulseGenerator returns correctly single step movement.
        g = PulseGeneratorLinear(Coordinates(1.0 / STEPPER_PULSES_PER_MM_X,
                                             0, 0, 0),
                                 self.v)
        i = 0
        for direction, px, py, pz, pe in g:
            if direction:
                continue
            i += 1
            self.assertEqual(px, 0)
            self.assertEqual(py, None)
            self.assertEqual(pz, None)
            self.assertEqual(pe, None)
        self.assertEqual(i, 1)
        g = PulseGeneratorLinear(Coordinates(
                                             1.0 / STEPPER_PULSES_PER_MM_X,
                                             1.0 / STEPPER_PULSES_PER_MM_Y,
                                             1.0 / STEPPER_PULSES_PER_MM_Z,
                                             1.0 / STEPPER_PULSES_PER_MM_E),
                                 self.v)
        i = 0
        for direction, px, py, pz, pe in g:
            if direction:
                continue
            i += 1
            self.assertEqual(px, 0)
            self.assertEqual(py, 0)
            self.assertEqual(pz, 0)
            self.assertEqual(pe, 0)
        self.assertEqual(i, 1)

    def __check_circular(self, delta, radius, plane, direction=CW):
        g = PulseGeneratorCircular(delta, radius, plane, direction, self.v)
        x, y, z, e = 0, 0, 0, 0
        dx, dy, dz, de = None, None, None, None
        dir_changed = 0
        dir_requested = False
        t = -1
        for direction_i, px, py, pz, pe in g:
            if direction_i:
                dx, dy, dz, de = px, py, pz, pe
                dir_requested = True
                continue
            if dir_requested:  # ignore last change
                dir_requested = False
                dir_changed += 1
            if px is not None:
                x += dx
            if py is not None:
                y += dy
            if pz is not None:
                z += dz
            if pe is not None:
                e += de
            v = list(i for i in (px, py, pz, pe) if i is not None)
            self.assertEqual(min(v), max(v))
            self.assertLessEqual(t, min(v))
            t = max(v)
        return dir_changed, Coordinates(x / STEPPER_PULSES_PER_MM_X,
                                        y / STEPPER_PULSES_PER_MM_Y,
                                        z / STEPPER_PULSES_PER_MM_Z,
                                        e / STEPPER_PULSES_PER_MM_E)

    def test_single_radius_circles(self):
        # Check if PulseGenerator returns correctly single radius movement in
        # both direction.
        zero_delta = Coordinates(0, 0, 0, 0)
        radius = Coordinates(1.0 / STEPPER_PULSES_PER_MM_X, 0, 0, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_XY, CW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(-1.0 / STEPPER_PULSES_PER_MM_X, 0, 0, 0)
        _, pos = self.__check_circular(zero_delta, radius,
                                       PLANE_XY, CW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(0, 1.0 / STEPPER_PULSES_PER_MM_Y, 0, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_YZ, CW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(0, -1.0 / STEPPER_PULSES_PER_MM_Y, 0, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_YZ, CW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(0, 0, 1.0 / STEPPER_PULSES_PER_MM_Z, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_ZX, CW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(0, 0, -1.0 / STEPPER_PULSES_PER_MM_Z, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_ZX, CW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(1.0 / STEPPER_PULSES_PER_MM_X, 0, 0, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_XY, CCW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(-1.0 / STEPPER_PULSES_PER_MM_X, 0, 0, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_XY, CCW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(0, 1.0 / STEPPER_PULSES_PER_MM_Y, 0, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_YZ, CCW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(0, -1.0 / STEPPER_PULSES_PER_MM_Y, 0, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_YZ, CCW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(0, 0, 1.0 / STEPPER_PULSES_PER_MM_Z, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_ZX, CCW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))
        radius = Coordinates(0, 0, -1.0 / STEPPER_PULSES_PER_MM_Z, 0)
        _, pos = self.__check_circular(zero_delta, radius, PLANE_ZX, CCW)
        self.assertEqual(pos, Coordinates(0, 0, 0, 0))

    def test_with_hal_virtual(self):
        # Using hal_virtual module for this test, it already contains plenty
        # of asserts for wrong number of pulses, pulse timing issues etc
        hal_virtual.move(PulseGeneratorLinear(Coordinates(1, 0, 0, 0),
                                              self.v))
        hal_virtual.move(PulseGeneratorLinear(Coordinates(25.4, 0, 0, 0),
                                              self.v))
        hal_virtual.move(PulseGeneratorLinear(Coordinates(25.4, 0, 0, 0),
                                              self.v))
        hal_virtual.move(PulseGeneratorLinear(Coordinates(25.4, 0, 0, 0),
                                              self.v))
        hal_virtual.move(PulseGeneratorLinear(Coordinates(TABLE_SIZE_X_MM,
                                                          TABLE_SIZE_Y_MM,
                                                          TABLE_SIZE_Z_MM,
                                                          100.0), self.v))
        hal_virtual.move(PulseGeneratorCircular(Coordinates(0, 20, 0, 0),
                                                Coordinates(-10, 10, 0, 0),
                                                PLANE_XY, CW, self.v))
        hal_virtual.move(PulseGeneratorCircular(Coordinates(-4, -4, 0, 0),
                                                Coordinates(-2, -2, 0, 0),
                                                PLANE_XY, CW, self.v))
        delta = Coordinates(- 2.0 / STEPPER_PULSES_PER_MM_X,
                            - 2.0 / STEPPER_PULSES_PER_MM_Y, 0, 0)
        radius = Coordinates(- 1.0 / STEPPER_PULSES_PER_MM_X,
                             - 1.0 / STEPPER_PULSES_PER_MM_Y, 0, 0)
        hal_virtual.move(PulseGeneratorCircular(delta, radius, PLANE_XY, CW,
                                                self.v))

    def test_twice_faster_linear(self):
        # Checks if one axis moves exactly twice faster, pulses are correct.
        m = Coordinates(2, 4, 0, 0)
        g = PulseGeneratorLinear(m, self.v)
        i = 0
        for direction, px, py, pz, pe in g:
            if direction:
                continue
            if i % 2 == 0:
                self.assertNotEqual(px, None)
            else:
                self.assertEqual(px, None)
            self.assertNotEqual(py, None)
            self.assertEqual(pz, None)
            self.assertEqual(pe, None)
            i += 1
        self.assertEqual(m.find_max() * STEPPER_PULSES_PER_MM_Y, i)

    def test_pulses_count_and_timings(self):
        # Check if number of pulses is equal to specified distance.
        m = Coordinates(TABLE_SIZE_X_MM, TABLE_SIZE_Y_MM, TABLE_SIZE_Z_MM,
                        100.0)
        g = PulseGeneratorLinear(m, self.v)
        ix = 0
        iy = 0
        iz = 0
        ie = 0
        t = -1
        for direction, px, py, pz, pe in g:
            if direction:
                continue
            if px is not None:
                ix += 1
            if py is not None:
                iy += 1
            if pz is not None:
                iz += 1
            if pe is not None:
                ie += 1
            v = list(x for x in (px, py, pz, pe) if x is not None)
            self.assertEqual(min(v), max(v))
            self.assertLess(t, min(v))
            t = max(v)
        self.assertEqual(m.x * STEPPER_PULSES_PER_MM_X, ix)
        self.assertEqual(m.y * STEPPER_PULSES_PER_MM_Y, iy)
        self.assertEqual(m.z * STEPPER_PULSES_PER_MM_Z, iz)
        self.assertEqual(m.e * STEPPER_PULSES_PER_MM_E, ie)
        self.assertLessEqual(t, g.total_time_s())
        _, pos = self.__check_circular(Coordinates(0, 8, 0, 7),
                                       Coordinates(1, 0, 1, 0),
                                       PLANE_ZX, CCW)
        self.assertEqual(pos, Coordinates(0, 8, 0, 7))
        _, pos = self.__check_circular(Coordinates(5, 0, 0, 6),
                                       Coordinates(0, 1, -1, 0),
                                       PLANE_YZ, CW)
        self.assertEqual(pos, Coordinates(5, 0, 0, 6))
        _, pos = self.__check_circular(Coordinates(-2, -2, 3, 2),
                                       Coordinates(-1, -1, 0, 0),
                                       PLANE_XY, CCW)
        self.assertEqual(pos, Coordinates(-2, -2, 3, 2))

    def test_acceleration_velocity(self):
        # Check if acceleration present in pulses sequence and if velocity
        # is correct, since PulseGenerator is responsible for this, check only
        # one child class.
        m = Coordinates(TABLE_SIZE_X_MM, 0, 0, 0)
        g = PulseGeneratorLinear(m, self.v)
        i = 0
        lx = 0
        lt, at, bt = None, None, None
        for direction, px, py, pz, pe in g:
            if direction:
                continue
            if i == 2:
                at = px - lx
            if i == TABLE_SIZE_X_MM * STEPPER_PULSES_PER_MM_X / 2:
                lt = px - lx
            bt = px - lx
            lx = px
            i += 1
        self.assertEqual(round(60.0 / lt / STEPPER_PULSES_PER_MM_X),
                         round(self.v))
        self.assertGreater(at, lt)
        self.assertGreater(bt, lt)

    def test_directions(self):
        # Check if directions are set up correctly.
        m = Coordinates(1, -2, 3, -4)
        g = PulseGeneratorLinear(m, self.v)
        dir_found = False
        for direction, px, py, pz, pe in g:
            if direction:
                # should be once
                self.assertFalse(dir_found)
                dir_found = True
                # check dirs
                self.assertTrue(px > 0 and py < 0 and pz > 0 and pe < 0)
        m = Coordinates(-1, 2, -3, 4)
        g = PulseGeneratorLinear(m, self.v)
        dir_found = False
        for direction, px, py, pz, pe in g:
            if direction:
                # should be once
                self.assertFalse(dir_found)
                dir_found = True
                # check dirs
                self.assertTrue(px < 0 and py > 0 and pz < 0 and pe > 0)
        # check for circle, full circle
        dir_changed, _ = self.__check_circular(Coordinates(0, 0, 0, 0),
                                               Coordinates(1.0, 1.0, 0, 0),
                                               PLANE_ZX, CCW)
        self.assertEqual(dir_changed, 4)


if __name__ == '__main__':
    unittest.main()
