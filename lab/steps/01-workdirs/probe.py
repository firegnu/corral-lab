#!/usr/bin/env python3
"""步骤 01：在之后要用的每个「目录 × agent」组合上各起一个不带首句的探针 agent（不送话，不花额度），
看哪些会弹信任框。

用法：probe.py start | status | stop
- Claude Code：启动后很快进入 idle；一直 starting 多半是弹了信任框
- Codex：第一次提交之前一直是 starting，状态分不出有没有弹框，要 corral attach 进去看
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lablib as L  # noqa: E402


def probes():
    return [
        ("lab/probe-cc-main", "claude", L.LAB, "常驻工作 agent、逐字、生命周期、兼容、事件文件"),
        ("lab/probe-cx-main", "codex", L.LAB, "临时委派的 Codex、反方向委派的外层 Codex"),
        ("lab/probe-cc-a-review", "claude", os.path.join(L.TMP, "wt-lab-a-review"), "权限框、Esc 打断用的 Claude 评审方"),
        ("lab/probe-cx-a-review", "codex", os.path.join(L.TMP, "wt-lab-a-review"), "第一个项目的评审方"),
        ("lab/probe-cc-b", "claude", os.path.join(L.TMP, "wt-lab-b"), "第二个项目的工作 agent"),
        ("lab/probe-cx-b-review", "codex", os.path.join(L.TMP, "wt-lab-b-review"), "第二个项目的评审方"),
    ]


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "start":
        for name, kind, cwd, use in probes():
            code, out = L.corral("start", name, "--cwd", cwd, "--", *L.agent_cmd(kind), timeout=90)
            print(f"  start {name}（{kind}，{cwd}）→ 退出码 {code} {out.get('instance') or out.get('error')}")
        time.sleep(5)
        cmd = "status"
    if cmd == "status":
        for name, kind, cwd, use in probes():
            code, st = L.corral("status", name)
            state = st.get("state") if code == 0 else f"不在（退出码 {code}）"
            hint = ""
            if code == 0 and kind == "claude" and state == "starting":
                hint = "  ← 多半在信任框，attach 去看"
            if code == 0 and kind == "codex":
                hint = "  ← Codex 状态看不出，attach 去看"
            print(f"  {name:24} {kind:6} {state:9} {cwd}{hint}\n      用途：{use}")
        return 0
    if cmd == "stop":
        for name, _, _, _ in probes():
            code, out = L.corral("stop", name, "--timeout", "40")
            print(f"  stop {name} → 退出码 {code} {out.get('stopped_by') or out.get('error') or ''}")
        return 0
    sys.exit(__doc__)


if __name__ == "__main__":
    sys.exit(main())
