#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/unwatch" lab-b
corral stop lab-b/review --timeout 45 || true
corral stop lab-b/dev --timeout 45 || true
