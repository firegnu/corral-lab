#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "03 生命周期与故障"
"$BIN/need" --absent lab/life-cx lab/life-cc
echo "下一步：$STEP_DIR/run.py"
