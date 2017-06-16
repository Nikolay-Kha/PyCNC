import time
import math


class Pid(object):
    # PID coefficients
    P = 0.422
    I = 0.208
    D = 0.014
    WINDUP_LIMIT = 3.0
    FIX_ACCURACY = 0.01
    FIX_TIME_S = 2.5

    def __init__(self, target_value, start_time=time.time()):
        """
        Proportional-integral-derivative controller implementation.
        :param target_value: value which PID should achieve.
        :param start_time: start time, current system time by default.
        """
        self._last_time = start_time
        self._target_value = target_value
        self._integral = 0
        self._last_error = 0
        self._is_target_fixed = False
        self._target_fix_timer = None

    def update(self, current_value, current_time=time.time()):
        """
        Update PID with new current value.
        :param current_value: current value.
        :param current_time: time when current value measured, current system
                             time if not specified.
        :return: value in range 0..1.0 which represents PID output.
        """
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
        """
        Check if target value is reached and PID maintains this value.
        :return: boolean value
        """
        return self._is_target_fixed


# for test purpose, see details in corresponding test file
if __name__ == "__main__":
    p = Pid(230, 0)
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
