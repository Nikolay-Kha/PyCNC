"""
This module reads temperature from NTC thermistor connected to ads111x.
Circuit diagram for this module should be like this:

     Vcc
     ---
      |
      |
     .-.
     | |
     | |   R1
     '-'
      |
      o----------------o------------> ads111x input
      |                |
      | |              |
     .-./              |
     | /             + |
     |/|   R0 NTC    -----  10 uF
     /-'             -----
    / |                |
      |                |
     _|_              _|_
     GND              GND

Since ads111x uses internal reference voltage, Vcc should be well regulated.
"""

from __future__ import division
import math
import time

import ads111x as adc

CELSIUS_TO_KELVIN = 273.15

# Circuit parameters, resistance in Ohms, temperature in Celsius.
# Beta is thermistor parameter:
# https://en.wikipedia.org/wiki/Thermistor#B_or_.CE.B2_parameter_equation
Vcc = 3.3
R0 = 100000
T0 = 25
BETA = 4092
R1 = 4700

Rinf = R0 * math.exp(-BETA / (T0 + CELSIUS_TO_KELVIN))


def get_temperature(channel):
    """
    Measure temperature on specified channel.
    :param channel: ads111x channel.
    :return: temperature in Celsius
    """
    v = adc.measure(channel)
    if v >= Vcc:
        raise IOError("Thermistor not connected")
    if v <= 0:
        raise IOError("Short circuit")
    r = v * R1 / (Vcc - v)
    return (BETA / math.log(r / Rinf)) - CELSIUS_TO_KELVIN


# for test purpose
if __name__ == "__main__":
    while True:
        for i in range(0, 4):
            print("T{}={}".format(i, get_temperature(i)))
        print("-----------------------------")
        time.sleep(0.5)
