import time
import math


class Pid(object):
    FIX_ACCURACY = 0.01
    FIX_TIME_S = 2.5

    def __init__(self, target_value, coefficients, start_time=None):
        """
        Proportional-integral-derivative controller implementation.
        :param target_value: value which PID should achieve.
        :param coefficients: dict with "P", "I" and "D" coefficients.
        :param start_time: start time, current system time by default.
        """
        if start_time is None:
            self._last_time = time.time()
        else:
            self._last_time = start_time
        self._target_value = target_value
        self.P = coefficients["P"]
        self.I = coefficients["I"]
        self.D = coefficients["D"]
        self.WINDUP_LIMIT = 1.0 / self.I
        self._integral = 0
        self._last_error = 0
        self._is_target_fixed = False
        self._target_fix_timer = None

    def update(self, current_value, current_time=None):
        """
        Update PID with new current value.
        :param current_value: current value.
        :param current_time: time when current value measured, current system
                             time if not specified.
        :return: value in range 0..1.0 which represents PID output.
        """
        if current_time is None:
            current_time = time.time()
        delta_time = current_time - self._last_time
        self._last_time = current_time
        error = self._target_value - current_value
        self._integral += error * delta_time
        # integral windup protection
        if abs(self._integral) > self.WINDUP_LIMIT:
            self._integral = math.copysign(self.WINDUP_LIMIT, self._integral)
        delta_error = error - self._last_error
        self._last_error = error

        res = self.P * error + self.I * self._integral + self.D * delta_error
        if res > 1.0:
            res = 1.0
        if res < 0.0:
            res = 0.0

        if not self._is_target_fixed:
            if abs(error) < self._target_value * self.FIX_ACCURACY \
                    and res < 1.0:
                if self._target_fix_timer is None:
                    self._target_fix_timer = current_time
                elif current_time - self._target_fix_timer > self.FIX_TIME_S:
                    self._is_target_fixed = True
            else:
                self._target_fix_timer = None
        return res

    def is_fixed(self):
        """ Check if target value is reached and PID maintains this value.
        :return: boolean value
        """
        return self._is_target_fixed

    def target_value(self):
        """ Get target value.
        :return: value.
        """
        return self._target_value


# for test purpose, see details in corresponding test file
if __name__ == "__main__":
    p = Pid(230, {"P": 0.1000, "I": 0.0274, "D": 0.2055}, 0)
    c = 0.0039
    h = 3.09
    t0 = 25
    t = t0
    r = 0
    for i in range(1, 601):
        # natural cooling
        t -= (t - t0) * c
        # heating
        t += h * r
        r = p.update(t, i)
        print(i, t, r, p.is_fixed())
