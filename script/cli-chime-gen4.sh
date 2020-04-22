#!/bin/sh

#rm ./output/*.csv

set -e
cd "$(dirname "$0")/.."

script/bootstrap
script/-check-docker-compose

echo
echo "==> Rebuilding containers…"
docker-compose up -d --build

clear

echo ""

echo "Processing models...    "$(date +"%Y-%m-%d-%H:%M:%S")

docker container exec chime_app ls -l ./
docker container exec chime_app python ./src/cli-gen4a.py

echo "Completed processing... "$(date +"%Y-%m-%d-%H:%M:%S")

echo ""

cd ..
