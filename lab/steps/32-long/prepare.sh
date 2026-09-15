#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "32 长内容走文件"
"$BIN/need" lab-a/dev=idle
no_watcher lab-a
"$PY" "$STEP_DIR/gen_long.py"
cat <<EOF

在窗口 2（dev）里说：
  把 $RUN/lab-a/long-context.md 当背景材料交给评审：重写 $RUN/lab-a/request.md（第一行仍只写 LAB-A-TOKEN），在里面引用这个文件的路径，要求评审方读完全部内容，并在评审结果里写出文件最后一行的暗号；然后运行 lab/bin/handoff lab-a，结束这一轮。
这一轮结束后：
  $STEP_DIR/check.sh
EOF
