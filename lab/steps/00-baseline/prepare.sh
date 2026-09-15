#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "00 环境基线"
exec "$PY" "$STEP_DIR/check.py"
