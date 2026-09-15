#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "23 临时委派：Codex → Claude Code"
"$BIN/need" --absent lab-a/dev-cx
"$BIN/strays"
cat <<EOF

窗口 4（分屏，先挂着等）：
  corral attach --wait lab-a/dev-cx
窗口 3（启动外层 Codex，不带首句）：
  corral start lab-a/dev-cx --cwd $LAB -- codex --yolo -m gpt-5.6-luna -c 'model_reasoning_effort="low"'
窗口 4 接上后，在里面说：
  开一个 Claude Code 看一下 ledger/report.py 的输出格式有没有问题，给它用 haiku 模型。
EOF
