#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/unwatch" lab-a
corral stop lab-a/review-cc --timeout 45 || true
echo "lab-a/review 保留给 43"
