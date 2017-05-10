#!/bin/sh
set -e
PASS=raspberry
ADDR=pi@192.168.0.208
if [ ! -z $1 ]; then
    ADDR=$1
fi
tar -cvjSf $(dirname "$0")/pycnc.tar.bz2 $(dirname "$0")/*.py > /dev/null
sshpass -p${PASS} scp $(dirname "$0")/pycnc.tar.bz2 "${ADDR}:~/pycnc"
sshpass -p${PASS} ssh -t ${ADDR} "(cd ~/pycnc && tar xvf pycnc.tar.bz2) > /dev/null"  &> /dev/null
sshpass -p${PASS} ssh -t ${ADDR} "sudo pypy ~/pycnc/main.py"
