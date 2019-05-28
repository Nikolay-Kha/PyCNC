#!/bin/sh
set -e
PASS=raspberry
ADDRESS=pi@192.168.0.211
if [ ! -z $1 ]; then
    if [[ $1 == *"@"* ]]; then
        ADDRESS=$1
    else
        ADDRESS=pi@$1
    fi
fi
find . -name "*.py" -o -name "pycnc" -o -name "*.gcode" | tar -cjf $(dirname "$0")/pycnc.tar.bz2 -T -
sshpass -p${PASS} scp $(dirname "$0")/pycnc.tar.bz2 "${ADDRESS}:~/pycnc"
sshpass -p${PASS} ssh -t ${ADDRESS} "(cd ~/pycnc && tar xvf pycnc.tar.bz2) > /dev/null"  &> /dev/null
sshpass -p${PASS} ssh -t ${ADDRESS} "sudo pypy ~/pycnc/pycnc"
