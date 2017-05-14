import unittest
import time

from cnc.coordinates import *
from cnc.pulses import *
from cnc.config import *
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
                          Coordinates(0, 0, 0), self.v)

    def test_step(self):
        # Check if PulseGenerator returns correctly single step movement.
        g = PulseGeneratorLinear(Coordinates(1.0 / STEPPER_PULSES_PER_MM, 0, 0),
                                 self.v)
        i = 0
        for px, py, pz in g:
            i += 1
            self.assertEqual(px, 0)
            self.assertEqual(py, None)
            self.assertEqual(pz, None)
        self.assertEqual(i, 1)
        g = PulseGeneratorLinear(Coordinates(
                                             1.0 / STEPPER_PULSES_PER_MM,
                                             1.0 / STEPPER_PULSES_PER_MM,
                                             1.0 / STEPPER_PULSES_PER_MM),
                                 self.v)
        i = 0
        for px, py, pz in g:
            i += 1
            self.assertEqual(px, 0)
            self.assertEqual(py, 0)
            self.assertEqual(pz, 0)
        self.assertEqual(i, 1)

    def test_linear_with_hal_virtual(self):
        # Using hal_virtual module for this test, it already contains plenty
        # of asserts for wrong number of pulses, pulse timing issues etc
        hal_virtual.move_linear(Coordinates(1, 0, 0), self.v)
        hal_virtual.move_linear(Coordinates(25.4, 0, 0), self.v)
        hal_virtual.move_linear(Coordinates(25.4, 0, 0), self.v)
        hal_virtual.move_linear(Coordinates(25.4, 0, 0), self.v)
        hal_virtual.move_linear(Coordinates(TABLE_SIZE_X_MM,
                                            TABLE_SIZE_Y_MM,
                                            TABLE_SIZE_Z_MM), self.v)

    def test_twice_faster(self):
        # Checks if one axis moves exactly twice faster, pulses are correct.
        m = Coordinates(2, 4, 0)
        g = PulseGeneratorLinear(m, self.v)
        i = 0
        for px, py, pz in g:
            if i % 2 == 0:
                self.assertNotEqual(px, None)
            else:
                self.assertEqual(px, None)
            self.assertNotEqual(py, None)
            self.assertEqual(pz, None)
            i += 1
        self.assertEqual(m.find_max() * STEPPER_PULSES_PER_MM, i)

    def test_pulses_count_and_timings(self):
        # Check if number of pulses is equal to specified distance.
        m = Coordinates(TABLE_SIZE_X_MM, TABLE_SIZE_Y_MM, TABLE_SIZE_Z_MM)
        g = PulseGeneratorLinear(m, self.v)
        ix = 0
        iy = 0
        iz = 0
        t = -1
        for px, py, pz in g:
            if px is not None:
                ix += 1
            if py is not None:
                iy += 1
            if pz is not None:
                iz += 1
            v = list(x for x in (px, py, pz) if x is not None)
            self.assertEqual(min(v), max(v))
            self.assertLess(t, min(v))
            t = max(v)
        self.assertEqual(m.x * STEPPER_PULSES_PER_MM, ix)
        self.assertEqual(m.y * STEPPER_PULSES_PER_MM, iy)
        self.assertEqual(m.z * STEPPER_PULSES_PER_MM, iz)
        self.assertLessEqual(t, g.total_time_s())

    def test_acceleration_velocity(self):
        # Check if acceleration present in pulses sequence and if velocity
        # is correct
        m = Coordinates(TABLE_SIZE_X_MM, 0, 0)
        g = PulseGeneratorLinear(m, self.v)
        i = 0
        lx = 0
        for px, py, pz in g:
            if i == 2:
                at = px - lx
            if i == TABLE_SIZE_X_MM * STEPPER_PULSES_PER_MM / 2:
                lt = px - lx
            bt = px - lx
            lx = px
            i += 1
        self.assertEqual(round(60.0 / lt / STEPPER_PULSES_PER_MM), round(self.v))
        self.assertGreater(at, lt)
        self.assertGreater(bt, lt)

if __name__ == '__main__':
    unittest.main()