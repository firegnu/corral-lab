#!/bin/sh
# 41 起要复用 lab-a/review；只在单独重跑时 stop
. "$(dirname "$0")/../common.sh"
"$BIN/unwatch" lab-a
rm -f "$RUN/lab-a/long-context.md" "$RUN/lab-a/long-token.txt"
echo "已删长文件；lab-a/review 保留（要停：corral stop lab-a/review）"
