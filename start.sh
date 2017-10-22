#!/bin/bash

if [ -e ./temp ]
then
  pid=`cat temp`
  echo "Process already exists; $pid"
else
  script='/home/pi/PyIOT/app.py'
  echo 'starting $script'
  /usr/bin/python3 $script &
  echo $! > temp
fi