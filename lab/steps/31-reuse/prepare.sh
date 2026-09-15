#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "31 第二轮：复用同一个评审方"
"$BIN/need" lab-a/dev lab-a/review=idle
no_watcher lab-a
"$PY" -c 'import json,sys; s=json.load(open(sys.argv[1])); print("  上一轮：第", s["round"], "轮，评审方实例", s["b_instances"].get("lab-a/review"))' "$RUN/lab-a/state.json"
cat <<EOF

等 dev 按第一轮意见处理完（idle）后，在窗口 2 里说：
  做 TASKS.md 任务 3（金额改 Decimal），测试全过后提交。然后同样写 $RUN/lab-a/request.md（第一行仍只写 LAB-A-TOKEN）请评审任务 3 的提交，运行 lab/bin/handoff lab-a，结束这一轮。
这一轮结束后：
  $STEP_DIR/check.sh
  corral stop lab-a/review          # 看窗口 4 回到等待
EOF
