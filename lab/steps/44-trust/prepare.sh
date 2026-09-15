#!/bin/sh
. "$(dirname "$0")/../common.sh"
title "44 评审方卡在信任框（starting 超时）"
"$BIN/need" lab-a/dev=idle
"$BIN/need" --absent lab-a/review-new
no_watcher lab-a
use_request lab-a minimal
DIR="$LAB_TMP/untrusted-$(date +%s)"
mkdir -p "$DIR"
git -C "$DIR" init -q
printf '# 没被信任过的新仓库\n' > "$DIR/README.md"
git -C "$DIR" add README.md
git -C "$DIR" -c user.name=lab -c user.email=lab@localhost commit -q -m init
echo "$DIR" > "$RUN/lab-a/untrusted.txt"
echo "  新建 ${DIR}（git 仓库，从没被信任过）"
cat <<EOF

窗口 3：
  cd $LAB && lab/bin/handoff lab-a --a lab-a/dev --b lab-a/review-new --b-cwd $DIR --start-timeout 30
约 30 秒后 watch.log 应出现 start_incomplete。然后：
  窗口 4：corral attach lab-a/review-new     看到信任框，什么都别选，按 Ctrl-] 退出接入
  窗口 3：corral stop lab-a/review-new
然后：
  $STEP_DIR/check.sh
EOF
