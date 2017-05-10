#!/usr/bin/env python

try:
    from hal_rpi import *
except ImportError:
    print("----- Hardware not detected, using virtual environment -----")
    print("----- Use M111 command to enable more detailed debug -----")
    from hal_virtual import *
