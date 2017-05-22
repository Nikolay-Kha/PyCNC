""" This module describes system wide enums.
"""


class Enum(object):
    """ Base class for enums
    """
    __global_increment = 1

    def __init__(self, for_str):
        """ Initialize base class for enumerates.
        :param for_str: return value for build in str() function
        """
        self.value = Enum.__global_increment
        self._str = for_str
        Enum.__global_increment += 1

    def __eq__(self, other):
        return self.value == other.value

    def __str__(self):
        return self._str


class Plane(Enum):
    """ Enum for choosing plane for circular interpolation.
    """
    pass

PLANE_XY = Plane("XY")
PLANE_ZX = Plane("ZX")
PLANE_YZ = Plane("YZ")


class RotationDirection(Enum):
    """ Enum for choosing rotation direction.
    """
    pass

CW = RotationDirection("CW")
CCW = RotationDirection("CCW")
