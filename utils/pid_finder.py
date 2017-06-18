#!/usr/bin/env python
import os
import sys
import time

cnc_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(cnc_dir)
from cnc.hal_raspberry import hal

"""
This executable module is looking for PID coefficients.
Can be ran only on real hardware.
"""

# change settings below for your hardware/environment
EXTRUDER_TARGET_TEMPERATURE = 200
BED_TARGET_TEMPERATURE = 70
DUMMY_CYCLES = 2
TOTAL_CYCLES = 7


# finder itself
def finder(target_temperature, get_temperature, control):
    print("Heating...")
    on = True
    control(100)
    last_t = get_temperature()
    last_time = time.time()
    max_t = 0
    min_t = 10000
    cycle_number = 0
    cycle_accumulator = 0
    cycle_counter = 0
    cycle_time = 0
    while True:
        current_time = time.time()
        t = get_temperature()
        time_filter = (current_time - last_time) > 0.1
        if t >= target_temperature and on and time_filter:
            on = False
            control(0)
            last_time = current_time
            cycle_number += 1
            if cycle_number > DUMMY_CYCLES:
                print("Cycle took {} s".format(current_time - cycle_time))
                cycle_accumulator += current_time - cycle_time
                cycle_counter += 1
            cycle_time = current_time
        if t < target_temperature and not on and time_filter:
            if cycle_number > TOTAL_CYCLES:
                break
            on = True
            control(100)
            last_time = current_time
        if abs(last_t - t) >= 1:
            print("Temperature is {}, cycle #{}".format(t, cycle_number))
            last_t = t
        if cycle_number > DUMMY_CYCLES:
            if t > max_t:
                max_t = t
            if t < min_t:
                min_t = t
        time.sleep(0.001)
    d_temperature = max_t - min_t
    d_time = cycle_accumulator / cycle_counter
    print("dT={}, dt={}".format(d_temperature, d_time))
    p = 1.0 / (1.2 * d_temperature)
    i = 1.0 / (15.0 * d_time)
    d = 1.0 / (0.15 * d_time)
    print("Finder result P={}, I={}, D={}".format(p, i, d))
    return p, i, d


# finder itself
def main():
    hal.init()
    try:
        hal.fan_control(True)
        print("Running for extruder...")
        try:
            ep, ei, ed = finder(EXTRUDER_TARGET_TEMPERATURE,
                                hal.get_extruder_temperature,
                                hal.extruder_heater_control)
        except (IOError, OSError):
            ep, ei, ed = None, None, None
            print("Extruder malfunction")
        hal.extruder_heater_control(0)
        print("Running for bed...")
        try:
            bp, bi, bd = finder(BED_TARGET_TEMPERATURE,
                                hal.get_bed_temperature,
                                hal.bed_heater_control)
        except (IOError, OSError):
            bp, bi, bd = None, None, None
            print("Bed malfunction")
        print("Done")
        print("Extruder P={}, I={}, D={}".format(ep, ei, ed))
        print("Bed P={}, I={}, D={}".format(bp, bi, bd))
        hal.bed_heater_control(0)
        hal.fan_control(False)
    except KeyboardInterrupt:
        pass
    hal.deinit()


if __name__ == '__main__':
    main()
