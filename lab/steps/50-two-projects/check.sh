#!/bin/sh
. "$(dirname "$0")/../common.sh"
rc=0
"$BIN/roundcheck" lab-a --expect delivered --contains LAB-A-TOKEN --not-contains LAB-B-TOKEN --wait 900 || rc=1
"$BIN/roundcheck" lab-b --expect delivered --contains LAB-B-TOKEN --not-contains LAB-A-TOKEN --wait 900 || rc=1
"$PY" - "$RUN" <<'EOF' || rc=1
import json, os, sys
run = sys.argv[1]
bad = 0
for prefix in ("lab-a", "lab-b"):
    state = json.load(open(os.path.join(run, prefix, "state.json")))
    ok = state["a"] == f"{prefix}/dev" and state["b"] == f"{prefix}/review"
    print(f"  {'PASS' if ok else 'FAIL'}  {prefix} 这一轮的 A={state['a']} B={state['b']}")
    bad += not ok
sys.exit(1 if bad else 0)
EOF
exit $rc
