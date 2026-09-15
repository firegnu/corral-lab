#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/roundcheck" lab-a --expect delivered --contains LAB-A-TOKEN --wait 600 || true
"$PY" - "$RUN/lab-a" <<'EOF'
import json, os, sys
run = sys.argv[1]
state = json.load(open(os.path.join(run, "state.json")))
ev = [json.loads(l) for l in open(os.path.join(run, "watch.log"))]
names = [e["event"] for e in ev if e.get("round") == state["round"]]
ok = "send_b_not_idle" in names and "send_b_delivered" in names and names.index("send_b_not_idle") < names.index("send_b_delivered")
print(f"  {'PASS' if ok else 'FAIL'}  交给评审方时先 7（not_idle）再送达")
print(f"  记录  叫醒 dev 时是否遇到 7：{'是' if 'wake_a_not_idle' in names else '否'}")
EOF
