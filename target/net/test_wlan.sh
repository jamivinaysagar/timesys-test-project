#!/bin/sh

INTERFACE=$1
DRIVERTYPE=$2
NETWORK=$3
PASSWORD=$4
PINGLOC=$5

if [ -z "$INTERFACE" ]; then
    INTERFACE=wlan0
fi

if [ -z "$DRIVERTYPE" ]; then
    DRIVERTYPE=nl80211
fi

if [ -z "$NETWORK" ] || [ -z "$PASSWORD" ]; then
    SKIPCONNECTIONTEST=1
    echo "Skipping connection test"
fi

if [ -z "$PINGLOC" ]; then
    SKIPPINGTEST=1
    echo "Skipping ping test"
fi

if ! ifconfig $INTERFACE; then
    echo "Device $INTERFACE not found!"
    exit 1
fi

# Disable RFKill
if which rfkill > /dev/null; then
    rfkill unblock all
fi

if [ -z "$SKIPCONNECTIONTEST" ]; then
    killall wpa_supplicant
    wpa_passphrase $NETWORK $PASSWORD > /tmp/wpa.conf
    wpa_supplicant -D $DRIVERTYPE -c/tmp/wpa.conf -i$INTERFACE -B

    if ! udhcpc -i $INTERFACE -t 5 -n; then
        echo "Could not get IP Address from $NETWORK"
	killall wpa_supplicant
	rm /tmp/wpa.conf
        exit 1
    fi

    if [ -z "$SKIPPINGTEST" ] && ! ping $PINGLOC -c 5; then
        echo "Could not connect to internet"
	killall wpa_supplicant
	rm /tmp/wpa.conf
        exit 1
    fi

    killall wpa_supplicant
    rm /tmp/wpa.conf
fi

exit 0
