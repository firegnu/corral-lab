#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "22 同时开几个临时 agent"
"$BIN/need" lab-a/dev=idle
"$BIN/strays"
cat <<EOF

A. 在窗口 2（dev）里说：
  同时开三个 Codex（都用 gpt-5.6-luna、low 推理强度），分别看 ledger/parse.py、ledger/balance.py、ledger/report.py 各有什么问题，三个都答完再汇总告诉我，用完都关掉。
B. 窗口 3：
  cd $LAB && lab/bin/fanout 3 --kind codex
EOF
