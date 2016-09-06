#!/bin/sh

remove_module(){
set +e	
	lsmod |grep g_mass_storage > /dev/null
	if [ $? == 0 ]; then
		rmmod g_mass_storage
	fi
set -e	
}

if [ -e "backing-file" ]; then
	BACKING_FILE="./backing-file"
else
	BACKING_FILE="./bin/usb/backing-file"
fi

remove_module
modprobe g_mass_storage file=$BACKING_FILE
