#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "42 人按 Esc 打断评审方"
"$BIN/need" lab-a/dev=idle lab-a/review=idle
"$BIN/need" --absent lab-a/review-cc
no_watcher lab-a
use_request lab-a slow
cat <<EOF

A. Claude Code 评审方（打断没有事件，靠 wait --quiet）
  窗口 4：corral attach --wait lab-a/review-cc
  窗口 3：cd $LAB && lab/bin/handoff lab-a --a lab-a/dev --b lab-a/review-cc --b-kind claude --quiet 20
  它开始逐个读文件后，在窗口 4 里按一次 Esc，之后什么都别按。约 20 秒后：
    $STEP_DIR/check.sh a
  然后：corral stop lab-a/review-cc

B. Codex 评审方（打断有 Interrupt 事件）
  窗口 4：Ctrl-C 退出等待，改挂 corral attach --wait lab-a/review
  窗口 3：$STEP_DIR/prepare.sh 不用重跑；直接 lab/bin/handoff lab-a --a lab-a/dev --quiet 20
  它开始干活后，在窗口 4 里按一次 Esc。之后：
    $STEP_DIR/check.sh b
EOF
