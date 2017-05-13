from __future__ import division
import math


class Coordinates(object):
    """ This object represent machine coordinates.
        Machine supports 3 axis, so there are X, Y and Z.
    """
    def __init__(self, x, y, z):
        """ Create object.
        :param x: x coordinated.
        :param y: y coordinated.
        :param z: z coordinated.
        """
        self.x = round(x, 10)
        self.y = round(y, 10)
        self.z = round(z, 10)

    def is_zero(self):
        """ Check if all coordinates are zero.
        :return: boolean value.
        """
        return self.x == 0.0 and self.y == 0.0 and self.z == 0.0

    def is_in_aabb(self, p1, p2):
        """ Check coordinates are in aabb(Axis-Aligned Bounding Box).
            aabb is specified with two points.
        :param p1: First point in Coord object.
        :param p2: Second point in Coord object.
        :return: boolean value.
        """
        minx, maxx = sorted((p1.x, p2.x))
        miny, maxy = sorted((p1.y, p2.y))
        minz, maxz = sorted((p1.z, p2.z))
        if self.x < minx or self.y < miny or self.z < minz:
            return False
        if self.x > maxx or self.y > maxy or self.z > maxz:
            return False
        return True

    def length(self):
        """ Calculate the length of vector.
        :return: Vector length.
        """
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def round(self, base):
        """ Round values to specified base, ie 0.49 with base 0.25 will be 0.5.
        :param base: Base.
        :return: New rounded object.
        """
        return Coordinates(round(self.x / base) * base,
                           round(self.y / base) * base,
                           round(self.z / base) * base)

    def find_max(self):
        """ Find a maximum value of all values.
        :return: maximum value.
        """
        return max(self.x, self.y, self.z)

    # build in function implementation
    def __add__(self, other):
        return Coordinates(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Coordinates(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, v):
        return Coordinates(self.x * v, self.y * v, self.z * v)

    def __div__(self, v):
        return Coordinates(self.x / v, self.y / v, self.z / v)

    def __truediv__(self, v):
        return Coordinates(self.x / v, self.y / v, self.z / v)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __str__(self):
        return '(' + str(self.x) + ', ' + str(self.y) + ', ' + str(self.z) + ')'

    def __abs__(self):
        return Coordinates(abs(self.x), abs(self.y), abs(self.z))
