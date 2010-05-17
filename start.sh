#!/bin/bash

echo 6 > /sys/class/backlight/openframe-bl/brightness

ping -c 1 google.co.uk
while [ $? != 0 ]
do
	sleep 1
	ping -c 1 google.co.uk
done

cd $(dirname $0)
python touchmenu.py
