#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "12 人正在打字时送话被拒（退出码 8）"
"$BIN/need" lab-a/dev=idle
cat <<EOF

A. 在窗口 2（dev 的接入窗口）里敲 abc，再按 3 次退格删掉，不要回车。
   10 秒内在窗口 3 运行：
     cd $LAB && lab/bin/wake lab-a/dev "用一句话告诉我任务 2 改了哪几个文件。" --every 5
   之后别碰窗口 2（鼠标可以划过，但不要点击、滚动）。
B. 输入框里有草稿时送话（回归检查，ISSUES 第 2 条，corral 48fb26a 已修）：
     $STEP_DIR/draftcheck.py
   全自动：自己起一次性 agent、用 corral keys 种草稿，不打扰 lab-a/dev。
   期望：送话退 0、merged_with_draft=true、agent 收到拼接后的内容并回答（修复前这里是退出码 3）。
   想手工看也行：在窗口 2 里敲「草稿」两个字留着不删，等 35 秒后
     lab/bin/wake lab-a/dev "只回复：收到"
   看完手动清掉输入框里剩下的字。
EOF
