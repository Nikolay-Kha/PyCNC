import threading
import time
import logging

from cnc.pid import Pid


class Heater(threading.Thread):
    LOOP_INTERVAL_S = 0.5
    SENSOR_TIMEOUT_S = 1

    def __init__(self, target_temp, pid_coefficients, measure_method,
                 control_method):
        """ Initialize and run asynchronous heating.
        :param target_temp: temperature which should be reached in Celsius.
        :param pid_coefficients: dict with PID coefficients.
        :param measure_method: Method which should be called to measure
                               temperature, it should return temperature in
                               Celsius.
        :param control_method: Method which should be called to control heater
                               power, it should received one argument with
                               heater power in percent(0..100).
        """
        self._current_power = 0
        threading.Thread.__init__(self)
        self._pid = Pid(target_temp, pid_coefficients)
        self._measure = measure_method
        self._control = control_method
        self._is_run = True
        self._mutex = threading.Lock()
        self.setDaemon(True)
        self.start()
        logging.info("Heating thread start, temperature {}/{} C"
                     .format(self._measure(), self.target_temperature()))

    def target_temperature(self):
        """ Return target temperature which should be reached.
        :return:
        """
        return self._pid.target_value()

    def is_fixed(self):
        """ Check if target value is reached and PID maintains this value.
        :return: boolean value
        """
        return self._pid.is_fixed()

    def run(self):
        """ Thread worker implementation. There is a loop for PID control.
        """
        last_error = None
        while True:
            self._mutex.acquire()
            if not self._is_run:
                break
            try:
                current_temperature = self._measure()
            except (IOError, OSError):
                self._control(0)
                if last_error is None:
                    last_error = time.time()
                else:
                    if time.time() - last_error > self.SENSOR_TIMEOUT_S:
                        logging.critical("No data from temperature sensor."
                                         " Stop heating.")
                        break
                continue
            last_error = None
            self._current_power = self._pid.update(current_temperature) * 100
            self._control(self._current_power)
            self._mutex.release()
            time.sleep(self.LOOP_INTERVAL_S)

    def stop(self):
        """ Stop heating and free this instance.
        """
        # make sure that control will not be called in worker anymore.
        self._mutex.acquire()
        self._is_run = False
        self._mutex.release()
        self._control(0)
        logging.info("Heating thread stop")

    def wait(self):
        """ Block until target temperature is reached.
        """
        i = 0
        while not self._pid.is_fixed():
            if i % 8 == 0:
                logging.info("Heating... current temperature {} C, power {}%".
                             format(self._measure(), int(self._current_power)))
                i = 0
            i += 1
            time.sleep(0.25)
