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
python -m unittest discover "$@" --pattern="test_*.py"
echo '-------------------------Integration tests----------------------------'
app="pycnc"
if ! which ${app} &> /dev/null; then
    echo "WARNING pycnc not found in path. Not installed? Using './pycnc'."
    app="./pycnc"
fi
res="$(${app} tests/rects.gcode 2>&1)"
res="${res}$(${app} tests/circles.gcode 2>&1)"
res="${res}$(${app} tests/test_parser.gcode 2>&1)"
if echo "${res}" | grep -q -i error; then
  echo "FAILED"
  echo "$res"
  exit 1
fi
echo "OK"

