#!/bin/bash

echo 'GIT pull'
cd /home/pi/PyIOT

/usr/bin/git pull

echo 'restart'
sudo systemctl restart pyiot.service