#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "30 交给另一个 agent 评审：第一轮"
"$BIN/need" lab-a/dev=idle
"$BIN/need" --absent lab-a/review
no_watcher lab-a
[ -d "$LAB_TMP/wt-lab-a-review" ] || { echo "  不满足  没有 worktree $LAB_TMP/wt-lab-a-review，先做 01"; exit 1; }
rm -f "$RUN/lab-a/request.md"
cat <<EOF

窗口 4（分屏，先挂着等评审方）：
  corral attach --wait lab-a/review
窗口 5（看 watcher 记录）：
  touch $RUN/lab-a/watch.log && tail -f $RUN/lab-a/watch.log
在窗口 2（dev）里说：
  请另一个 agent 评审你任务 1 和任务 2 的提交。把评审请求写进 $RUN/lab-a/request.md：第一行只写 LAB-A-TOKEN；然后写清楚要评审哪几个提交（给出提交号；评审方的工作目录是本仓库的 worktree，能用 git show 看到）、重点看什么，并要求评审结果的第一行抄写 LAB-A-TOKEN。写好后运行 lab/bin/handoff lab-a，运行完这一轮就结束，等脚本叫你。
EOF
