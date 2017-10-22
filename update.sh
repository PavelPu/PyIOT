#!/bin/bash

echo 'GIT pull'
git pull

echo 'restart'
./stop.sh
./start.sh