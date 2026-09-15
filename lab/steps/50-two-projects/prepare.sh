#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "50 第二个项目并行"
"$BIN/need" lab-a/dev=idle
"$BIN/need" --absent lab-b/dev lab-b/review
no_watcher lab-a
no_watcher lab-b
for wt in wt-lab-b wt-lab-b-review; do
  [ -d "$LAB_TMP/$wt" ] || { echo "  不满足  没有 worktree ${LAB_TMP}/${wt}，先做 01"; exit 1; }
done
mkdir -p "$RUN/lab-b"
rm -f "$RUN/lab-a/request.md" "$RUN/lab-b/request.md"
cat <<EOF

窗口 6（分屏，第二个项目的评审方）：
  corral attach --wait lab-b/review
窗口 7（启动第二个项目的工作 agent 并接入）：
  corral start lab-b/dev --cwd $LAB_TMP/wt-lab-b -- claude --model haiku --add-dir /tmp/clab --allowedTools 'Bash(corral:*)' 'Bash(lab/bin/handoff:*)'
  corral attach lab-b/dev
在窗口 7（lab-b/dev）里说：
  读 TASKS.md，做「第二个项目专用」的 B1，测试通过后提交。
同时在窗口 2（lab-a/dev）里说：
  做 TASKS.md 任务 4，测试通过后提交。
两边都做完后，几乎同时让它们交接：
  窗口 2：写 $RUN/lab-a/request.md（第一行只写 LAB-A-TOKEN，要求评审结果第一行抄写它）请评审任务 4 的提交，运行 lab/bin/handoff lab-a，结束这一轮。
  窗口 7：写 $RUN/lab-b/request.md（第一行只写 LAB-B-TOKEN，要求评审结果第一行抄写它）请评审 B1 的提交，运行 lab/bin/handoff lab-b，结束这一轮。
两轮都结束后：
  $STEP_DIR/check.sh
EOF
