import unittest

from cnc.pid import *


class TestPid(unittest.TestCase):
    def setUp(self):
        self._environment_temp = 25
        # Coefficients below were chosen by an experimental way with a real
        # hardware: reprap heating bed and extruder.
        self._bed_c = 0.00231  # bed cooling coefficient
        self._bed_h = 0.25  # bed heating coefficient
        self._extruder_c = 0.0039  # extruder cooling coefficient
        self._extruder_h = 3.09  # extruder heating coefficient

    def tearDown(self):
        pass

    def __simulate(self, target_temp, environment_temp, cool, heat):
        # Simulate heating some hypothetical thing with heater(h is a heat
        # transfer coefficient, which becomes just a delta temperature each
        # second) from environment temperature to target_temp. Consider that
        # there is natural air cooling process with some heat transfer
        # coefficient c. Heating power is controlled by PID.
        pid = Pid(target_temp, 0)
        temperature = environment_temp
        heater_power = 0
        fixed_at = None
        zeros_counter = 0
        for j in range(1, 15 * 60 + 1):  # simulate for 15 minutes
            # natural cooling
            temperature -= (temperature - environment_temp) * cool
            # heating
            temperature += heat * heater_power
            heater_power = pid.update(temperature, j)
            if fixed_at is None:
                if pid.is_fixed():
                    fixed_at = j
            else:
                self.assertLess(abs(temperature - target_temp),
                                pid.FIX_ACCURACY * target_temp,
                                msg="PID failed to control temperature "
                                "{}/{} {}".format(temperature, target_temp, j))
            if heater_power == 0.0:
                zeros_counter += 1
        self.assertLess(zeros_counter, 20, msg="PID turns on/off, instead of "
                                               "fine control")
        self.assertLess(fixed_at, 600,
                        msg="failed to heat in 10 minutes, final temperature "
                            "{}/{}".format(temperature, target_temp))

    def test_simple(self):
        pid = Pid(50, 0)
        self.assertEqual(0, pid.update(100, 1))
        self.assertEqual(1, pid.update(0, 2))

    def test_bed(self):
        # check if bed typical temperatures can be reached in simulation
        for target in range(50, 101, 10):
            self.__simulate(target, self._environment_temp,
                            self._bed_c, self._bed_h)

    def test_extruder(self):
        # check if extruder typical temperatures can be reached in simulation
        for target in range(150, 251, 10):
            self.__simulate(target, self._environment_temp,
                            self._extruder_c, self._extruder_h)


if __name__ == '__main__':
    unittest.main()
