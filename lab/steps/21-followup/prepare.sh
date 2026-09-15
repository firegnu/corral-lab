#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "21 追问一轮"
"$BIN/need" lab-a/dev=idle
"$BIN/strays"
cat <<'EOF'

在窗口 2（dev）里说：
  再开一个 Codex（同样用 gpt-5.6-luna、low 推理强度）问它：ledger/parse.py 遇到空行和只有空白的行会怎样？答完先别关，我还要追问。
等 dev 转述完回答后，再说：
  追问它：那 CSV 文件开头带 BOM 呢？问完就关掉它。
EOF
