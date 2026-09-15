#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "02 送话逐字送达"
"$BIN/need" --absent lab/verb-claude lab/verb-codex
echo "下一步：$STEP_DIR/run.py"
