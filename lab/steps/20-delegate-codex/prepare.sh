#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "20 临时委派：Claude Code → Codex"
"$BIN/need" lab-a/dev=idle
"$BIN/strays"
cat <<'EOF'

在窗口 2（dev）里说：
  开一个 Codex 看一下这个想法：TASKS.md 任务 3 打算把金额从 float 改成 Decimal，会影响哪些文件、测试要怎么改？给 Codex 用 gpt-5.6-luna 模型、low 推理强度省钱。
EOF
