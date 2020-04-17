#!/usr/bin/env bash

set -e

git pull
if [[ -n "$1" ]]; then
  export TAG=$1
else
  export TAG=$(python greencandle/version.py)
fi
docker-compose -f ./install/docker-compose_stag.yml pull
docker-compose -f ./install/docker-composei_stag.yml up -d

docker system prune --volumes --all -f
