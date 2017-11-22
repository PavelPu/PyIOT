#!/bin/bash

echo 'GIT pull'
/usr/bin/git pull

echo 'restart'
sudo systemctl restart pyiot.service