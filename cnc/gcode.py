import re

from cnc.coordinates import Coordinates

gpattern = re.compile('([A-Z])([-+]?[0-9.]+)')
cleanpattern = re.compile('\s+|\(.*?\)|;.*') # white spaces and comments start with ';' and in '()'


class GCodeException(Exception):
    """ Exceptions while parsing gcode.
    """
    pass


class GCode(object):
    """ This object represent single line of gcode.
        Do not create it manually, use parse_line() instead.
    """
    def __init__(self, params):
        """ Create object.
        :param params: dict with gcode key-values.
        """
        self.params = params

    def get(self, argname, default=None, multiply=1.0):
        """ Get value from gcode line.
        :param argname: Value name.
        :param default: Default value if value doesn't exist.
        :param multiply: if value exist, multiply it by this value.
        :return: Value if exists or default otherwise.
        """
        if argname not in self.params:
            return default
        return float(self.params[argname]) * multiply

    def coordinates(self, default, multiply):
        """ Get X, Y and Z values as Coord object.
        :param default: Default values, if any of coords is not specified.
        :param multiply: If value exist, multiply it by this value.
        :return: Coord object.
        """
        x = self.get('X', default.x, multiply)
        y = self.get('Y', default.y, multiply)
        z = self.get('Z', default.z, multiply)
        return Coordinates(x, y, z)

    def has_coordinates(self):
        """ Check if at least one of the coordinates is present.
        :return: Boolean value.
        """
        return 'X' in self.params or 'Y' in self.params or 'Z' in self.params

    def command(self):
        """ Get value from gcode line.
        :return: String with command or None if no command specified.
        """
        if 'G' in self.params:
            return 'G' + self.params['G']
        if 'M' in self.params:
            return 'M' + self.params['M']
        return None

    @staticmethod
    def parse_line(line):
        """ Parse line.
        :param line: String with gcode line.
        :return: gcode objects.
        """
        line = line.upper()
        line = re.sub(cleanpattern, '', line)
        if len(line) == 0:
            return None
        if line[0] == '%':
            return None
        m = gpattern.findall(line)
        if not m:
            raise GCodeException('gcode not found')
        if len(''.join(["%s%s" % i for i in m])) != len(line):
            raise GCodeException('extra characters in line')
        params = dict(m)
        if len(params) != len(m):
            raise GCodeException('duplicated gcode entries')
        if 'G' in params and 'M' in params:
            raise GCodeException('g and m command found')
        return GCode(params)
