#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "60 协议兼容"
"$BIN/need" --absent lab/compat-old lab/compat-p2 lab/compat-e2
mkdir -p "$LAB_TMP"
echo "下一步：$STEP_DIR/run.py   （中途会停下来请你另开窗口 attach 一次）"
