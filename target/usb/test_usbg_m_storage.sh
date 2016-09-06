#!/bin/sh -e

trap cleanup EXIT

remove_module(){
set +e	
	lsmod |grep g_mass_storage > /dev/null
	if [ $? == 0 ]; then
		rmmod g_mass_storage
	fi
set -e	
}

cleanup(){
	if [ -e "$INFILE" ]; then
		rm $INFILE
	fi
	if [ -e "$OUTFILE" ]; then
		rm $OUTFILE
	fi	
	remove_module
}

sleep 5
DEVICE=$(readlink -f /dev/disk/by-id/usb-Linux_File-Stor_Gadget-0:0)

MOUNT_POINT=$(mount |grep -i $DEVICE | awk '{ print $3 }')

INFILE=/tmp/input.dat
OUTFILE=$MOUNT_POINT/output.dat

BS=1k
COUNT=500

echo "+++ Generating random data"
dd if=/dev/urandom of=$INFILE bs=$BS count=$COUNT

echo "+++ Writing random data to $MOUNT_POINT"
cp $INFILE $OUTFILE
sync

echo "+++ Reading data from $MOUNT_POINT"
MD5IN=$(md5sum $INFILE | awk '{print $1}')
MD5OUT=$(md5sum $OUTFILE | awk '{print $1}')

if [[ "$MD5IN" == "$MD5OUT" ]]; then
	echo "+++ Files match"
	exit 0
else
	echo "+++ Data mismatch"
	exit 1
fi
