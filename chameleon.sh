#!/bin/bash
# SCRIPT TO EAT ALL IP ADDRESSES IN A /24
# SET DEFAULT VALUE
IFACE="EMPTY"

# GET COMMAND LINE OPTION FOR INTERFACE
while getopts i: option
do
case "${option}"
in
i) IFACE="${OPTARG}";;
esac
done

# CHECK TO SEE IF COMMAND LINE ARG WAS SPECIFIED
if [ "$IFACE" == "EMPTY" ]
then
	echo "Please specify a command-line interface: ./bradware.sh -i eth0"
	exit 1
fi
echo $IFACE

# GET CURRENT IP ADDRESS FROM PRIMARY INTERFACE
IP="$(ifconfig | sed -En 's/127.0.0.1//;s/.*inet (addr:)?(([0-9]*\.){3}[0-9]*).*/\2/p')"
echo $IP

# CUT FIRST THREE OCTETS
IP_BEGIN="$(echo $IP | cut -d'.' -f1-3)"
echo $IP_BEGIN

# LOOP THROUGH AND ALIAS INTERFACE
for i in $(seq 2 1 254)
do

	# ALIAS THE INTERFACE
	ifconfig $IFACE:$i $IP_BEGIN.$i up
	echo "Alias $IFACE:$i -- $IP_BEGIN:$i"
done
