#!/bin/sh
set -e
PASS=raspberry
ADDR=pi@192.168.0.208
if [ ! -z $1 ]; then
    ADDR=pi@$1
fi
find cnc/hal_raspberry -name "rpgpio*.py" -o -name "pycnc" | tar -cjf $(dirname "$0")/../pycnc.tar.bz2 -T -
sshpass -p${PASS} scp $(dirname "$0")/../pycnc.tar.bz2 "${ADDR}:~/pycnc"
sshpass -p${PASS} ssh -t ${ADDR} "(cd ~/pycnc && tar xvf pycnc.tar.bz2) > /dev/null"  &> /dev/null
sshpass -p${PASS} ssh -t ${ADDR} "(cd ~/pycnc && sudo pypy -m cnc.hal_raspberry.rpgpio)"
