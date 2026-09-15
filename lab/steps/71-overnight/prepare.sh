#!/bin/sh
# 晚上运行
. "$(dirname "$0")/../common.sh"
title "71 过夜（晚上）"
"$BIN/need" lab-a/dev=idle lab-a/review=idle
no_watcher lab-a
"$BIN/wake" lab-a/dev "今天先到这里。明天做 TASKS.md 任务 5，今晚不用动，回复「好」就行。"
"$BIN/snapshot" save evening
cat <<EOF

就这样放着过夜（电脑可以睡眠，不要重启）。明天早上运行：
  $STEP_DIR/morning.sh
EOF
