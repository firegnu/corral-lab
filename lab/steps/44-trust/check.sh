#!/bin/sh
. "$(dirname "$0")/../common.sh"
DIR="$(cat "$RUN/lab-a/untrusted.txt")"
"$BIN/roundcheck" lab-a --expect b_gone --wait 120 || true
"$PY" - "$RUN/lab-a" "$DIR" <<'EOF'
import json, os, sys
run, d = sys.argv[1], sys.argv[2]
state = json.load(open(os.path.join(run, "state.json")))
ev = [json.loads(l) for l in open(os.path.join(run, "watch.log"))]
ev = [e for e in ev if e.get("round") == state["round"]]
si = [e for e in ev if e["event"] == "start_incomplete"]
print(f"  {'PASS' if si else 'FAIL'}  watcher 记下 start_incomplete" + (f"（送出后 {si[0]['t'] - state['sent_at']:.0f}s）" if si else ""))
toml = open(os.path.expanduser("~/.codex/config.toml"), encoding="utf-8").read()
real = os.path.realpath(d)
print(f"  {'PASS' if d not in toml and real not in toml else 'FAIL'}  Codex 信任记录里没有 {real}")
EOF
