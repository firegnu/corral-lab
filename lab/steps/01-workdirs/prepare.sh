#!/bin/sh
# 01 准备：交接目录和三个 worktree（从 main 当前提交建，分支 lab/wt-*）
. "$(dirname "$0")/../common.sh"
title "01 工作目录"
mkdir -p "$RUN/lab-a" "$RUN/lab-b"
for wt in wt-lab-a-review wt-lab-b wt-lab-b-review; do
  if [ -d "$LAB_TMP/$wt" ]; then
    echo "  已有  $LAB_TMP/$wt"
  else
    git -C "$LAB" worktree add -q -B "lab/$wt" "$LAB_TMP/$wt" main
    echo "  新建  ${LAB_TMP}/${wt}（分支 lab/${wt}）"
  fi
done
echo
echo "下一步：$STEP_DIR/probe.py start"
