#!/bin/bash
set -e
cd "$(dirname "$0")/.."

IMG="ghcr.io/mpepping/solarman-mqtt:dev"
RUNTIME="docker"

$RUNTIME build . -t $IMG -f Dockerfile --force-rm
$RUNTIME inspect $IMG
$RUNTIME run --rm -it $IMG --validate -f config.sample.json
$RUNTIME rmi $IMG