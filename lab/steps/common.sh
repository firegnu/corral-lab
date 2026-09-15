# 各步骤的 prepare.sh / clean.sh 共用。用法：. "$(dirname "$0")/../common.sh"
set -eu
STEP_DIR="$(cd "$(dirname "$0")" && pwd)"
LAB="$(cd "$STEP_DIR/../../.." && pwd)"
LAB_TMP="${LAB_TMP:-/tmp/clab}"
RUN="$LAB_TMP/run"
BIN="$LAB/lab/bin"
PY="${LAB_PYTHON:-python3}"
export LAB_TMP

title() { printf '\n== %s\n' "$*"; }

# token_of lab-a → LAB-A-TOKEN
token_of() { printf '%s-TOKEN' "$(printf '%s' "$1" | tr '[:lower:]' '[:upper:]')"; }

# use_request <前缀> <模板名>：把 lab/requests/<模板名>.md 写成交接目录里的 request.md
use_request() {
  mkdir -p "$RUN/$1"
  sed "s/{TOKEN}/$(token_of "$1")/g" "$LAB/lab/requests/$2.md" > "$RUN/$1/request.md"
  echo "已写 $RUN/$1/request.md（模板 $2）"
}

# no_watcher <前缀>：要求上一轮 watcher 已结束
no_watcher() {
  "$PY" - "$1" <<'EOF'
import os, sys
sys.path.insert(0, os.path.join(os.environ["LAB"], "lab"))
import lablib as L
state = L.load_json(os.path.join(L.run_dir(sys.argv[1]), "state.json"))
if L.pid_alive(state.get("watcher_pid"), "watch-deliver"):
    sys.exit(f"  不满足  {sys.argv[1]} 第 {state.get('round')} 轮的 watcher 还在跑（lab/bin/unwatch {sys.argv[1]} 可停掉）")
print(f"  OK   {sys.argv[1]} 没有在跑的 watcher")
EOF
}
export LAB
