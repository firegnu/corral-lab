#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "43 评审方正忙时交下一轮（退出码 7 后重试）"
"$BIN/need" lab-a/dev=idle lab-a/review=idle
no_watcher lab-a
use_request lab-a minimal
cat <<EOF

窗口 3，两条连着运行（第一条让评审方忙起来，第二条马上交接）：
  corral send lab-a/review "先不用管评审。逐个读 ledger/ 下每个文件，每个文件用三句话总结给我。"
  cd $LAB && lab/bin/handoff lab-a --a lab-a/dev
handoff 会停在「等评审方这一轮结束」，输出里应先有 send_b_not_idle，之后 send_b_delivered。
（可选）handoff 返回后，马上让 dev 忙起来，看 watcher 叫醒 dev 时也遇到 7：
  corral send lab-a/dev "在等评审的时候，用三句话总结 TASKS.md 里还没做的任务。"
这一轮结束后：
  $STEP_DIR/check.sh
EOF
