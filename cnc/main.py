#!/usr/bin/env python

import sys
import readline
import logging
logging.basicConfig(level=logging.CRITICAL,
                    format='[%(levelname)s] %(message)s')

from cnc.gcode import GCode, GCodeException
from cnc.gmachine import GMachine, GMachineException

try: # python3 compatibility
    type(raw_input)
except NameError:
    raw_input = input

machine = GMachine()


def do_line(line):
    try:
        g = GCode.parse_line(line)
        machine.do_command(g)
    except (GCodeException, GMachineException) as e:
        print('ERROR ' + str(e))
        return False
    print('OK')
    return True


def main():
    try:
        if len(sys.argv) > 1:
            # Read file with gcode
            with open(sys.argv[1], 'r') as f:
                for line in f:
                    line = line.strip()
                    print('> ' + line)
                    if not do_line(line):
                        break
        else:
            # Main loop for interactive shell
            # Use stdin/stdout, additional interfaces like
            # UART, Socket or any other can be added.
            print("*************** Welcome to PyCNC! ***************")
            while True:
                line = raw_input('> ')
                if line == 'quit' or line == 'exit':
                    break
                do_line(line)
    except KeyboardInterrupt:
        pass
    print("\r\nExiting...")
    machine.release()

if __name__ == "__main__":
    main()

