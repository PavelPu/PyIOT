#!/bin/bash

if [ -e ./temp ]
then
  pid=`cat temp`
  echo "Process already exists; $pid"
else
  script='/home/pi/PyIOT/app.py'
  echo 'starting $script'
  nohup $script &
  echo $! > temp
fi