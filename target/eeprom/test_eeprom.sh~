#!/bin/sh

DEVICE=$1
PAGESIZE=$2

if [ -e "$DEVICE" ]; then
    SIZE=32768 #$(stat -c%s $DEVICE)
else
    echo "+++ File ${DEVICE} not found"
    echo
    echo "+++ Usage: $0 [device name]"
    exit 1
fi

if [ -n "$PAGESIZE" ]; then
    BS=$PAGESIZE
    COUNT=$(($SIZE/$BS))
else
    BS=1
    COUNT=$SIZE
fi

echo "+++ Device=${DEVICE} Size=${SIZE} Pagesize=${BS}"

touch /tmp/input.dat
touch /tmp/out.dat
chmod 777 /tmp/input.dat
chmod 777 /tmp/output.dat

INFILE=/tmp/input.dat
OUTFILE=/tmp/output.dat

echo "+++ Generating random data"
dd if=/dev/urandom of=$INFILE bs=$BS count=$COUNT

echo "+++ Writing random data to $DEVICE"
dd if=$INFILE of=$DEVICE bs=$BS count=$COUNT

echo "+++ Reading data from $DEVICE"
dd if=$DEVICE of=$OUTFILE bs=$BS count=$COUNT

MD5IN=$(md5sum $INFILE | awk '{print $1}')
MD5OUT=$(md5sum $OUTFILE | awk '{print $1}')

rm $INFILE $OUTFILE

if [[ "$MD5IN" == "$MD5OUT" ]]; then
    echo "+++ Files match"
    exit 0
else
    echo "+++ Data mismatch"
    exit 1
fi

