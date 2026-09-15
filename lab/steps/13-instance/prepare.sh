#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "13 实例编号变了不送"
"$BIN/need" --absent lab/w2
echo "下一步：$STEP_DIR/run.py"
