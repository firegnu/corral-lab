#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "61 事件文件长期增长"
"$BIN/need" --absent lab/big
echo "下一步：$STEP_DIR/run.py --mb 50"
