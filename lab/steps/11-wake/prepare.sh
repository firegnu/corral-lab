#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "11 叫醒脚本"
"$BIN/need" lab-a/dev=idle
cat <<EOF

窗口 3：
  cd $LAB && lab/bin/wake lab-a/dev "读 TASKS.md，做任务 2 的第一步：只补测试（新测试先失败），不改实现，提交。"
等上一条送达、dev 开始干活后，马上再运行：
  lab/bin/wake lab-a/dev "做任务 2 的第二步：改实现让测试全部通过，提交。"
EOF
