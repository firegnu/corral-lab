#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "41 评审方停下但没交付"
"$BIN/need" lab-a/dev=idle lab-a/review=idle
no_watcher lab-a
use_request lab-a nodone
cat <<EOF

窗口 3：
  cd $LAB && lab/bin/handoff lab-a --a lab-a/dev
这一轮结束后：
  $STEP_DIR/check.sh
EOF
