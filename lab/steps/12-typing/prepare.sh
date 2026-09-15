#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "12 人正在打字时送话被拒（退出码 8）"
"$BIN/need" lab-a/dev=idle
cat <<EOF

A. 在窗口 2（dev 的接入窗口）里敲 abc，再按 3 次退格删掉，不要回车。
   10 秒内在窗口 3 运行：
     cd $LAB && lab/bin/wake lab-a/dev "用一句话告诉我任务 2 改了哪几个文件。" --every 5
   之后别碰窗口 2（鼠标可以划过，但不要点击、滚动）。
B. （记录实际表现）在窗口 2 里敲「草稿」两个字，留着不删。等 35 秒后运行：
     lab/bin/wake lab-a/dev "只回复：收到"
   看完结果后手动清掉输入框里剩下的字。
EOF
