#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "10 开工：常驻工作 agent + 观察窗口"
"$BIN/need" --absent lab-a/dev
[ -d "$RUN/lab-a" ] || { echo "  不满足  没有 $RUN/lab-a，先做 01"; exit 1; }
cat <<EOF

窗口 1（看板）：
  cd $LAB && lab/bin/board
窗口 2（分屏，先挂着等）：
  corral attach --wait lab-a/dev
窗口 3（启动）：
  cd $LAB && corral start lab-a/dev --cwd $LAB -- claude --model sonnet --add-dir /tmp/clab --allowedTools 'Bash(corral:*)' 'Bash(lab/bin/handoff:*)'
EOF
