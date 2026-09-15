#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/unwatch" lab-a
corral stop lab-a/review --timeout 45 || true
