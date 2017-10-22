#!/bin/bash

if [ -e ./temp ]
then
  pid=`cat temp`
  echo "killing $pid"
  kill -15 $PID
  rm temp
else
  echo "Process not started"
fi