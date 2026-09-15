#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/roundcheck" lab-a --expect delivered --contains LAB-A-TOKEN --wait 900 || true
"$PY" - "$RUN" <<'EOF'
import json, os, sys
run = sys.argv[1]
evening = json.load(open(os.path.join(run, "snapshot-evening.json")))["agents"]
state = json.load(open(os.path.join(run, "lab-a", "state.json")))
ev = [json.loads(l) for l in open(os.path.join(run, "lab-a", "watch.log"))]
sent = [e for e in ev if e.get("round") == state["round"] and e["event"] == "send_b_delivered"]
same = sent and sent[-1].get("instance") == evening.get("lab-a/review", {}).get("instance")
print(f"  {'PASS' if same else 'FAIL'}  今早这一轮送给的评审方就是昨晚那个实例")
EOF
