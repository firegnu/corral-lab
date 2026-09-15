#!/bin/sh
# 只在单独重跑时用：31 要复用 lab-a/review
. "$(dirname "$0")/../common.sh"
"$BIN/unwatch" lab-a
corral stop lab-a/review --timeout 45 || true
