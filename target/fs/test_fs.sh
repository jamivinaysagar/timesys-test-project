#!/bin/sh -e

trap cleanup EXIT

cleanup(){
	if [ -e "$INFILE" ]; then
		rm $INFILE
	fi
	if [ -e "$OUTFILE" ]; then
		rm $OUTFILE
	fi
}

write_verify_test(){
	BS=1k
	COUNT=$(shuf -i 1-10000 -n 1)

	if [ ! -z "$MAX_SIZE" ]; then
		if [ "$COUNT" -gt "$MAX_SIZE" ]; then
			COUNT=$MAX_SIZE
		fi
	fi

	echo "+++ Generating random data"
	dd if=/dev/urandom of=$INFILE bs=$BS count=$COUNT

	echo "+++ Writing random data to $MOUNT_POINT"
	cp $INFILE $OUTFILE
	sync
	echo 3 > /proc/sys/vm/drop_caches 

	echo "+++ Reading data from $MOUNT_POINT"
	MD5IN=$(md5sum $INFILE | awk '{print $1}')
	MD5OUT=$(md5sum $OUTFILE | awk '{print $1}')

	if [[ "$MD5IN" == "$MD5OUT" ]]; then
		echo "+++ Files match"
		cleanup
	else
		echo "+++ Data mismatch"
		exit 1
	fi
}

usage()
{
	echo "Usage: $0 [OPTIONS]" >&2
	echo ""
	echo "Options: -r [Duration in seconds] How long the test needs to run for"
	echo "         -t [Handle type]         device or mount"
	echo "         -f [Filesystem path]     Handle to mount point or folder"
	echo "         -l                       Perform test on last mounted device"	
	echo "Examples: $0 -t device -f /dev/mmcblk0p1 -r 10"
	echo "          $0 -t mount -f /run/media/sdc"
	echo "          $0 -l"
}

while getopts ":r:t:f:l" opt; do
	case "$opt" in
	r)		
		RUN_DURATION=$OPTARG
		;;
	t)
		HANDLE_TYPE=$OPTARG
		;;
	f)
		FILE_PATH=$OPTARG
		;;
	l)
		LAST_MOUNTED_DEV=1
		;;
	\?)
		usage
		echo $opt
		exit 1
		;;
	esac
done

if [ $# -eq 0 ]; then
	usage
	exit 1
fi

if [ ! -z "$RUN_DURATION" ]; then
	START_TIME=$(date +%s)
	END_TIME=$(($START_TIME + $RUN_DURATION))
fi

if [ "$LAST_MOUNTED_DEV" == "1" ]; then
	MOUNT_POINT=$(mount |tail -1 | awk '{ print $3 }')
elif [ "$HANDLE_TYPE" == "mount" ]; then
	MOUNT_POINT=$FILE_PATH	
elif [ "$HANDLE_TYPE" == "device" ]; then
	MOUNT_POINT=$(mount |grep $FILE_PATH | awk '{ print $3 }')
else
	usage
	exit 1
fi

if [ ! -d $MOUNT_POINT ] || [ -z $MOUNT_POINT ]; then
	echo "$MOUNT_POINT not valid directory"
	exit 1
fi

INFILE=/tmp/input.dat
OUTFILE=$MOUNT_POINT/output.dat
MAX_SIZE=$(df | grep $MOUNT_POINT | awk '{ print $4 }')

while true; do 
	write_verify_test
	if [ ! -z "$END_TIME" ]; then
		CURRENT_TIME=$(date +%s)
		if [ "$CURRENT_TIME" -gt "$END_TIME" ]; then
			exit 0
		fi
	else
		exit 0
	fi
done
