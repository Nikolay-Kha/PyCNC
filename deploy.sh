#!/bin/sh
set -e
PASS=raspberry
ADDR=pi@192.168.0.208
if [ ! -z $1 ]; then
    ADDR=$1
fi
find . -name "*.py" -o -name "pycnc" | tar -cjf $(dirname "$0")/pycnc.tar.bz2 -T -
sshpass -p${PASS} scp $(dirname "$0")/pycnc.tar.bz2 "${ADDR}:~/pycnc"
sshpass -p${PASS} ssh -t ${ADDR} "(cd ~/pycnc && tar xvf pycnc.tar.bz2) > /dev/null"  &> /dev/null
sshpass -p${PASS} ssh -t ${ADDR} "sudo pypy ~/pycnc/pycnc"
