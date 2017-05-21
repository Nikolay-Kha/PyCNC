""" This module describes system wide enums.
"""

class Plane:
    """ Enum for choosing plane for circular interpolation.
    """
    PLANE_XY = 1
    PLANE_ZX = 2
    PLANE_YZ = 3


class RotationDirection:
    """ Enum for choosing rotation direction.
    """
    CW = 1
    CCW = 2
