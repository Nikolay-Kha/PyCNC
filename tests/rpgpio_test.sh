#!/bin/sh
set -e
PASS=raspberry
ADDR=pi@192.168.0.208
if [ ! -z $1 ]; then
    ADDR=pi@$1
fi
sshpass -p${PASS} scp $(dirname "$0")/../cnc/hal_raspberry/rpgpio_private.py "${ADDR}:~"
sshpass -p${PASS} scp $(dirname "$0")/../cnc/hal_raspberry/rpgpio.py "${ADDR}:~"
sshpass -p${PASS} ssh -t ${ADDR} "sudo ~/rpgpio.py"
