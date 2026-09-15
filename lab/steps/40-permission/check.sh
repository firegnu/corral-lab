#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/roundcheck" lab-a --expect delivered --contains LAB-A-TOKEN --wait 900 || true
"$PY" - "$RUN/lab-a" <<'EOF'
import json, os, sys
run = sys.argv[1]
state = json.load(open(os.path.join(run, "state.json")))
log = [json.loads(l) for l in open(os.path.join(run, "watch.log"))]
ev = [e for e in log if e.get("round") == state["round"]]
blocked = [e for e in ev if e["event"] == "blocked"]
unblocked = [e for e in ev if e["event"] == "unblocked"]
print(f"  {'PASS' if blocked else 'FAIL'}  watcher 记到 {len(blocked)} 次 blocked、{len(unblocked)} 次 unblocked")
for b, u in zip(blocked, unblocked):
    print(f"        blocked {b['t'] - state['sent_at']:.1f}s 后出现，持续 {u['t'] - b['t']:.1f}s")
EOF
