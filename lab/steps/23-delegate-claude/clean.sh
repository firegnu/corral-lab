#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/strays" --stop
corral stop lab-a/dev-cx --timeout 45 || true
