from __future__ import division
import logging
import time

from cnc.pulses import PulseGeneratorLinear
from cnc.config import *
from cnc.coordinates import Coordinates

""" This is virtual device class which is very useful for debugging.
    It checks PulseGenerator with some tests.
"""


def init():
    """ Initialize GPIO pins and machine itself, including calibration if
        needed. Do not return till all procedure is completed.
    """
    logging.info("initialize hal")


def spindle_control(percent):
    """ Spindle control implementation.
    :param percent: Spindle speed in percent.
    """
    logging.info("spindle control: {}%".format(percent))


def move_linear(delta, velocity):
    """ Move head to specified position
    :param delta: Coordinated object, delta position in mm
    :param velocity: velocity in mm per min
    """
    logging.info("move {} with velocity {}".format(delta, velocity))
    ix = iy = iz = 0
    generator = PulseGeneratorLinear(delta, velocity)
    lx, ly, lz = None, None, None
    dx, dy, dz = 0, 0, 0
    mx, my, mz = 0, 0, 0
    st = time.time()
    for tx, ty, tz in generator:
        if tx is not None:
            if tx > mx:
                mx = tx
            tx = int(round(tx * 1000000))
            ix += 1
            if lx is not None:
                dx = tx - lx
                assert dx > 0, "negative or zero time delta detected for x"
            lx = tx
        else:
            dx = None
        if ty is not None:
            if ty > my:
                my = ty
            ty = int(round(ty * 1000000))
            iy += 1
            if ly is not None:
                dy = ty - ly
                assert dy > 0, "negative or zero time delta detected for y"
            ly = ty
        else:
            dy = None
        if tz is not None:
            if tz > mz:
                mz = tz
            tz = int(round(tz * 1000000))
            iz += 1
            if lz is not None:
                dz = tz - lz
                assert dz > 0, "negative or zero time delta detected for z"
            lz = tz
        else:
            dz = None
        # very verbose, uncomment on demand
        # logging.debug("Iteration {} is {} {} {}".format(max(ix, iy, iz), tx, ty, tz))
        f = list(x for x in (tx, ty, tz) if x is not None)
        assert f.count(f[0]) == len(f), "fast forwarded pulse detected"
    pt = time.time()
    assert ix / STEPPER_PULSES_PER_MM == abs(delta.x), "x wrong number of pulses"
    assert iy / STEPPER_PULSES_PER_MM == abs(delta.y), "y wrong number of pulses"
    assert iz / STEPPER_PULSES_PER_MM == abs(delta.z), "z wrong number of pulses"
    assert max(mx, my, mz) <= generator.total_time_s(), "interpolation time or pulses wrong"
    logging.debug("Did {}, {}, {} iterations".format(ix, iy, iz))
    logging.info("prepared in " + str(round(pt - st, 2)) \
                 + "s, estimated " + str(round(generator.total_time_s(), 2)) + "s")


def join():
    """ Wait till motors work.
    """
    logging.info("hal join()")


def deinit():
    """ De-initialise.
    """
    logging.info("hal deinit()")
