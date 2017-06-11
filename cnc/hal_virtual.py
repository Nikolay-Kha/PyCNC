from __future__ import division
import time

from cnc.pulses import *
from cnc.config import *

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


# noinspection PyUnusedLocal
def move(generator):
    """ Move head to specified position.
    :param generator: PulseGenerator object.
    """
    delta = generator.delta()
    ix = iy = iz = ie = 0
    lx, ly, lz, le = None, None, None, None
    dx, dy, dz, de = 0, 0, 0, 0
    mx, my, mz, me = 0, 0, 0, 0
    cx, cy, cz, ce = 0, 0, 0, 0
    direction_x, direction_y, direction_z, dire = 1, 1, 1, 1
    st = time.time()
    direction_found = False
    for direction, tx, ty, tz, te in generator:
        if direction:
            direction_found = True
            direction_x, direction_y, direction_z, dire = tx, ty, tz, te
            if isinstance(generator, PulseGeneratorLinear):
                assert ((tx < 0 and delta.x < 0) or (tx > 0 and delta.x > 0)
                        or delta.x == 0)
                assert ((ty < 0 and delta.y < 0) or (ty > 0 and delta.y > 0)
                        or delta.y == 0)
                assert ((tz < 0 and delta.z < 0) or (tz > 0 and delta.z > 0)
                        or delta.z == 0)
                assert ((te < 0 and delta.e < 0) or (te > 0 and delta.e > 0)
                        or delta.e == 0)
            continue
        if tx is not None:
            if tx > mx:
                mx = tx
            tx = int(round(tx * 1000000))
            ix += direction_x
            cx += 1
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
            iy += direction_y
            cy += 1
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
            iz += direction_z
            cz += 1
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
            ie += dire
            ce += 1
            if le is not None:
                de = te - le
                assert de > 0, "negative or zero time delta detected for e"
            le = te
        else:
            de = None
        # very verbose, uncomment on demand
        # logging.debug("Iteration {} is {} {} {} {}".
        #               format(max(ix, iy, iz, ie), tx, ty, tz, te))
        f = list(x for x in (tx, ty, tz, te) if x is not None)
        assert f.count(f[0]) == len(f), "fast forwarded pulse detected"
    pt = time.time()
    assert direction_found, "direction not found"
    assert ix / STEPPER_PULSES_PER_MM_X == delta.x, "x wrong number of pulses"
    assert iy / STEPPER_PULSES_PER_MM_Y == delta.y, "y wrong number of pulses"
    assert iz / STEPPER_PULSES_PER_MM_Z == delta.z, "z wrong number of pulses"
    assert ie / STEPPER_PULSES_PER_MM_E == delta.e, "e wrong number of pulses"
    assert max(mx, my, mz, me) <= generator.total_time_s(), \
        "interpolation time or pulses wrong"
    logging.debug("Moved {}, {}, {}, {} iterations".format(ix, iy, iz, ie))
    logging.info("prepared in " + str(round(pt - st, 2)) + "s, estimated "
                 + str(round(generator.total_time_s(), 2)) + "s")


def join():
    """ Wait till motors work.
    """
    logging.info("hal join()")


def deinit():
    """ De-initialise.
    """
    logging.info("hal deinit()")
