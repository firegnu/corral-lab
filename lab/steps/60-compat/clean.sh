#!/bin/sh
# run.py 自己会清；中途被打断时用这个。协议不兼容的栏位，lab/cleanup.py 也会处理。
. "$(dirname "$0")/../common.sh"
corral stop lab/compat-old --timeout 45 >/dev/null 2>&1 || true
for d in corral-p2 corral-e2; do
  for n in lab/compat-p2 lab/compat-e2; do
    [ -x "$LAB_TMP/$d/bin/corral" ] && "$LAB_TMP/$d/bin/corral" stop "$n" --timeout 45 >/dev/null 2>&1 || true
  done
done
rm -rf "$LAB_TMP/corral-old" "$LAB_TMP/corral-p2" "$LAB_TMP/corral-e2"
"$BIN/need" --absent lab/compat-old lab/compat-p2 lab/compat-e2 || echo "还有残留：运行 lab/cleanup.py"
