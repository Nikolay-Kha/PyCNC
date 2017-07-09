import unittest

from cnc.heater import *
from cnc.pid import *
from cnc.config import *


class TestHeater(unittest.TestCase):
    def setUp(self):
        self._target_temp = 100
        Pid.FIX_TIME_S = 0
        Heater.LOOP_INTERVAL_S = 0.001
        self._control_counter = 0

    def tearDown(self):
        pass

    def __get_temperature(self):
        return self._target_temp

    def __get_bad_temperature(self):
        return self._target_temp / 2

    # noinspection PyUnusedLocal
    def __control(self, percent):
        self._control_counter += 1

    def test_start_stop(self):
        # check if thread stops correctly
        he = Heater(self._target_temp, EXTRUDER_PID, self.__get_temperature,
                    self.__control)
        self.assertEqual(self._target_temp, he.target_temperature())
        he.stop()
        self._control_counter = 0
        he.join(5)
        self.assertEqual(self._control_counter, 0)
        self.assertFalse(he.is_alive())

    def test_async(self):
        # check asynchronous heating
        self._control_counter = 0
        he = Heater(self._target_temp, EXTRUDER_PID, self.__get_temperature,
                    self.__control)
        j = 0
        while self._control_counter < 3:
            time.sleep(0.01)
            j += 1
            if j > 500:
                he.stop()
                raise Exception("Heater timeout")
        he.stop()
        self.assertTrue(he.is_fixed())

    def test_sync(self):
        # test wait() method
        self._control_counter = 0
        he = Heater(self._target_temp, EXTRUDER_PID, self.__get_temperature,
                    self.__control)
        he.wait()
        he.stop()
        self.assertGreater(self._control_counter, 1)  # one call for stop()
        self.assertTrue(he.is_fixed())

    def test_fail(self):
        # check if heater will not fix with incorrect temperature
        self._control_counter = 0
        he = Heater(self._target_temp, EXTRUDER_PID,
                    self.__get_bad_temperature, self.__control)
        j = 0
        while self._control_counter < 10:
            time.sleep(0.01)
            j += 1
            if j > 500:
                he.stop()
                raise Exception("Heater timeout")
        he.stop()
        self.assertGreater(self._control_counter, 10)  # one call for stop()
        self.assertFalse(he.is_fixed())


if __name__ == '__main__':
    unittest.main()
