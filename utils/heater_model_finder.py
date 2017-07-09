#!/usr/bin/env python

import os
import sys
import time

cnc_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(cnc_dir)
from cnc.hal_raspberry import hal


"""
This executable module is looking for heating and cooling transfer
coefficients. Can be ran only on real hardware.
"""

# change settings below for your hardware/environment
EXTRUDER_MAX_TEMPERATURE = 200
EXTRUDER_DELTA_TEMPERATURE = 50
BED_MAX_TEMPERATURE = 70
BED_DELTA_TEMPERATURE = 10
ENVIRONMENT_TEMPERATURE = 25


# finder itself
def finder(max_temperature, delta_temperature, get_temperature, control):
    ca = 0
    cn = 0
    ha = 0
    hn = 0
    print("Heating...")
    control(100)
    last_t = get_temperature()
    last_time = time.time()
    heated = False
    while True:
        t = get_temperature()
        if t >= max_temperature:
            if not heated:
                control(0)
                heated = True
        if heated and t <= max_temperature:
            break
        if abs(last_t - t) >= 1:
            print("Temperature is " + str(t))
            last_time = time.time()
            last_t = t
        time.sleep(0.1)
    print("Heated, measure cooling transfer coefficient.")
    while True:
        t = get_temperature()
        if abs(last_t - t) >= 1:
            current_time = time.time()
            if t <= max_temperature - delta_temperature:
                break
            v = abs(last_t - t) \
                / abs((last_t + t) / 2.0 - ENVIRONMENT_TEMPERATURE) \
                / (current_time - last_time)
            print("Temperature is {}, coefficient is {}".format(t, v))
            ca += v
            cn += 1
            last_time = current_time
            last_t = t
        time.sleep(0.001)
    c = ca / float(cn)
    print("Cooled off, waiting...")
    time.sleep(60)
    print("Heating, measure heating transfer coefficient.")
    control(100)
    heat_start = 0
    while True:
        t = get_temperature()
        if abs(last_t - t) >= 1:
            current_time = time.time()
            if t > max_temperature:
                heat_end = current_time
                break
            if t >= max_temperature - delta_temperature:
                ct = last_t \
                     - c * (current_time - last_time) \
                     * abs((last_t + t) / 2.0 - ENVIRONMENT_TEMPERATURE)
                v = abs(t - ct) / (current_time - last_time)
                print("Temperature is {}, coefficient is {}".format(t, v))
                if hn == 0:
                    heat_start = current_time
                ha += v
                hn += 1
            else:
                print("Temperature is " + str(t))
            last_time = current_time
            last_t = t
        time.sleep(0.001)
    h = ha / float(hn)
    control(0)
    print("Testing results...")
    # quick test
    heat_time = heat_end - heat_start
    t = max_temperature - delta_temperature
    for i in range(0, int(heat_time + 0.5)):
        t -= abs((t - ENVIRONMENT_TEMPERATURE)) * c
        t += h
    model_status = abs(max_temperature - t) < max_temperature * 0.1
    print("Model quick test result is {}/{} - {}"
          .format(t, max_temperature, model_status))
    print("Cooling transfer coefficient is " + str(c))
    print("Heating transfer coefficient is " + str(h))
    return c, h


# finder itself
def main():
    hal.init()
    try:
        hal.fan_control(True)
        print("Running for extruder...")
        try:
            ec, eh = finder(EXTRUDER_MAX_TEMPERATURE,
                            EXTRUDER_DELTA_TEMPERATURE,
                            hal.get_extruder_temperature,
                            hal.extruder_heater_control)
        except (IOError, OSError):
            ec, eh = None, None
            print("Extruder malfunction")
        hal.extruder_heater_control(0)
        print("Running for bed...")
        try:
            bc, bh = finder(BED_MAX_TEMPERATURE,
                            BED_DELTA_TEMPERATURE,
                            hal.get_bed_temperature,
                            hal.bed_heater_control)
        except (IOError, OSError):
            bc, bh = None, None
            print("Bed malfunction")
        hal.bed_heater_control(0)
        print("Done")
        print("Extruder transfer coefficients, cooling {}, heating {}"
              .format(ec, eh))
        print("Bed transfer coefficients, cooling {}, heating {}"
              .format(bc, bh))
        hal.fan_control(False)
    except KeyboardInterrupt:
        pass
    hal.deinit()


if __name__ == '__main__':
    main()
