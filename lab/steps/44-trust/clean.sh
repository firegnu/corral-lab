#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/unwatch" lab-a
corral stop lab-a/review-new --timeout 45 || true
if [ -f "$RUN/lab-a/untrusted.txt" ]; then
  rm -rf "$(cat "$RUN/lab-a/untrusted.txt")" "$RUN/lab-a/untrusted.txt"
  echo "已删未信任目录"
fi
