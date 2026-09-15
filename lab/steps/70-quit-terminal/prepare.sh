#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "70 退出整个终端软件"
"$BIN/need" lab-a/dev lab-a/review
"$BIN/snapshot" save before-quit
cat <<EOF

1. 确认要退出的终端软件里没有别的只在它里面跑的重要东西。
2. 接入窗口、看板都开着，直接 Cmd-Q 退出整个终端软件。
3. 重新打开终端软件，运行：
     $STEP_DIR/check.sh
     corral attach lab-a/dev
EOF
