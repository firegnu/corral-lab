#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "04 沙箱里被拒"
command -v codex >/dev/null && echo "  OK   codex 在 PATH 上" || echo "  不满足  没有 codex（真沙箱那一项会失败）"
echo "下一步：$STEP_DIR/run.py"
