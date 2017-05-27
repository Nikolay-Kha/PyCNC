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
    ix = iy = iz = ie = 0
    generator = PulseGeneratorLinear(delta, velocity)
    lx, ly, lz, le = None, None, None, None
    dx, dy, dz, de = 0, 0, 0, 0
    mx, my, mz, me = 0, 0, 0, 0
    st = time.time()
    for tx, ty, tz, te in generator:
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
        if te is not None:
            if te > me:
                me = te
            te = int(round(te * 1000000))
            ie += 1
            if le is not None:
                de = te - le
                assert de > 0, "negative or zero time delta detected for e"
            le = te
        else:
            de = None
        # very verbose, uncomment on demand
        # logging.debug("Iteration {} is {} {} {} {}".format(max(ix, iy, iz, ie), tx, ty, tz, te))
        f = list(x for x in (tx, ty, tz, te) if x is not None)
        assert f.count(f[0]) == len(f), "fast forwarded pulse detected"
    pt = time.time()
    assert ix / STEPPER_PULSES_PER_MM_X == abs(delta.x), "x wrong number of pulses"
    assert iy / STEPPER_PULSES_PER_MM_Y == abs(delta.y), "y wrong number of pulses"
    assert iz / STEPPER_PULSES_PER_MM_Z == abs(delta.z), "z wrong number of pulses"
    assert ie / STEPPER_PULSES_PER_MM_E == abs(delta.e), "e wrong number of pulses"
    assert max(mx, my, mz, me) <= generator.total_time_s(), "interpolation time or pulses wrong"
    logging.debug("Did {}, {}, {}, {} iterations".format(ix, iy, iz, ie))
    logging.info("prepared in " + str(round(pt - st, 2)) \
                 + "s, estimated " + str(round(generator.total_time_s(), 2)) + "s")


def move_circular(delta, radius, plane, velocity, direction):
    """ Move with circular interpolation.
    :param delta: finish position delta from the beginning, must be on
                  circle on specified plane. Zero means full circle.
    :param radius: vector to center of circle.
    :param plane: plane to interpolate.
    :param velocity: velocity in mm per min.
    :param direction: clockwise or counterclockwise.
    """
    logging.info("TODO move_circular {} {} {} with radius {} and velocity {}".
                 format(plane, delta, direction, radius, velocity))
    # TODO


def join():
    """ Wait till motors work.
    """
    logging.info("hal join()")


def deinit():
    """ De-initialise.
    """
    logging.info("hal deinit()")
