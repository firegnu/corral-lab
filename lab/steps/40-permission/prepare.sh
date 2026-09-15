#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "40 评审方弹权限框（会触发权限框，人亲手点）"
"$BIN/need" lab-a/dev=idle
"$BIN/need" --absent lab-a/review-cc
no_watcher lab-a
use_request lab-a review
cat <<EOF

窗口 4（分屏）：
  corral attach --wait lab-a/review-cc
窗口 3：
  cd $LAB && lab/bin/handoff lab-a --a lab-a/dev --b lab-a/review-cc --b-kind claude-ask
弹框后先别点，看 30 秒：看板和 watch.log 应是 blocked。然后在窗口 4 里选「Yes」（只允许这一次，
不要选「不再询问」，那会在 worktree 里写项目设置）。可能连续弹好几次，每次都一样处理。
这一轮结束后：
  $STEP_DIR/check.sh
EOF
