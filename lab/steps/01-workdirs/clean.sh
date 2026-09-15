#!/bin/sh
# 01 清理：只停探针。worktree 留给后面的步骤，最后由 lab/cleanup.py 移除。
. "$(dirname "$0")/../common.sh"
exec "$PY" "$STEP_DIR/probe.py" stop
