#!/bin/bash

set -e

echo '**********************************************************************'
echo '* Testing PyCNC modules.                                             *'
echo '* Hint: pass -v to this script arguments to see more verbose output. *'
echo '* Note: HAL tests should be run manually on corresponding board. For *'
echo '* example Raspberry Pi tests is tests/rpgpio_test.sh which should be *'
echo '* run with RPi board with connected to pin GPIO21 LED. LED should    *'
echo '* light up on pullup, set, and DMA test events.                      *'
echo '**********************************************************************'
echo '---------------------------Unit tests---------------------------------'
pypy -m unittest discover "$@" --pattern="test_*.py"
echo '-----------------------Integration tests------------------------------'
sudo pip install .
res="$(pycnc tests/rects.gcode 2>&1)"
res="$res$(pycnc tests/test_parser.gcode 2>&1)"
sudo pip uninstall -y pycnc
if echo "$res" | grep -q -i error; then
  echo "$res"
  exit 1
fi

