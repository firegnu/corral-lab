#!/bin/sh
. "$(dirname "$0")/../common.sh"
TOKEN="$(cat "$RUN/lab-a/long-token.txt")"
"$BIN/roundcheck" lab-a --expect delivered --contains LAB-A-TOKEN --contains "$TOKEN" --wait 900 || true
"$PY" - "$RUN/lab-a" <<'EOF'
import json, os, sys
run = sys.argv[1]
state = json.load(open(os.path.join(run, "state.json")))
n = len(state["text"].encode())
print(f"  {'PASS' if n < 300 else 'FAIL'}  送出的话只有 {n} 字节（长内容在文件里，不在 send 里）")
started = [json.loads(l) for l in open(os.path.join(run, "watch.log"))]
started = [e for e in started if e.get("round") == state["round"] and e["event"] == "b_started"]
print(f"  {'PASS' if started else 'FAIL'}  评审方是这一轮新 start 的（31 结束时 stop 过）")
EOF
