#!/bin/sh
# 第二天早上运行
. "$(dirname "$0")/../common.sh"
title "71 过夜（早上）"
"$BIN/snapshot" save morning
"$BIN/snapshot" compare evening morning || true
cat <<EOF

然后：
  corral attach lab-a/dev          看昨天的对话还在
在里面说：
  做 TASKS.md 任务 5，测试通过后提交。然后写 $RUN/lab-a/request.md（第一行只写 LAB-A-TOKEN，要求评审结果第一行抄写它）请评审任务 5 的提交，运行 lab/bin/handoff lab-a，结束这一轮。
这一轮结束后：
  $STEP_DIR/check.sh
EOF
