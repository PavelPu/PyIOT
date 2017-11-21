#!/bin/bash

echo 'GIT pull'
git pull

echo 'restart'
sudo systemctl restart pyiot.service