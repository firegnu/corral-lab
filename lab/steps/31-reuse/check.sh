#!/bin/sh
. "$(dirname "$0")/../common.sh"
"$BIN/roundcheck" lab-a --expect delivered --contains LAB-A-TOKEN --wait 900 || true
"$PY" - "$RUN/lab-a" <<'EOF'
import glob, json, os, sys
run = sys.argv[1]
log = [json.loads(l) for l in open(os.path.join(run, "watch.log"))]
state = json.load(open(os.path.join(run, "state.json")))
rnd = state["round"]
started = [e for e in log if e["event"] == "b_started" and e.get("name") == "lab-a/review"]
reused = [e for e in log if e.get("round") == rnd and e["event"] == "send_b_delivered"]
print(f"  {'PASS' if rnd >= 2 else 'FAIL'}  这是第 {rnd} 轮（至少第 2 轮）")
print(f"  {'PASS' if reused else 'FAIL'}  这一轮是 send 给已有的评审方，不是新 start")
print(f"  {'PASS' if reused and reused[-1].get('instance') == started[-1].get('instance') else 'FAIL'}  实例编号和启动时一样："
      f"{started[-1].get('instance') if started else None} / {reused[-1].get('instance') if reused else None}")
print(f"  {'PASS' if glob.glob(os.path.join(run, f'findings-{rnd - 1}*.md')) else 'FAIL'}  上一轮结果已归档为 findings-{rnd - 1}.md")
EOF
