#!/usr/bin/env python3
"""步骤 13：实例编号变了，叫醒脚本不送。用一个一次性的 Claude Code（lab/w2，不带首句，不花额度）。

1. start lab/w2，记下实例编号 X
2. stop，再同名 start，得到新编号 Y
3. lab/bin/wake lab/w2 "只回复：好" --instance X → 退出码 3（instance_changed），什么都没送
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lablib as L  # noqa: E402

NAME = "lab/w2"


def start():
    return L.corral("start", NAME, "--cwd", L.LAB, "--", *L.agent_cmd("claude"), timeout=90)


def main():
    checks = L.Checks("13 实例编号变了不送")
    try:
        code, out = start()
        if not checks.ok("start lab/w2", code == 0, out.get("error", "")):
            return checks.done()
        old = out["instance"]
        L.wait_done(NAME, total=60)
        code, out = L.corral("stop", NAME, "--timeout", "45")
        checks.ok("stop", code == 0)
        code, out = start()
        new = out.get("instance")
        checks.ok("同名重新 start，实例编号变了", code == 0 and new and new != old, f"{old} → {new}")
        L.wait_done(NAME, total=60)
        p = subprocess.run([sys.executable, os.path.join(L.LAB, "lab", "bin", "wake"), NAME, "只回复：好",
                            "--instance", old, "--every", "1", "--give-up", "10"],
                           capture_output=True, text=True, timeout=60)
        print("  wake 输出：\n    " + p.stdout.strip().replace("\n", "\n    "))
        checks.ok("wake 发现编号变了，退出码 3", p.returncode == 3 and "instance_changed" in p.stdout, f"退出码 {p.returncode}")
        code, st = L.corral("status", NAME)
        checks.ok("新实例什么都没收到", code == 0 and st.get("last_input_at") is None, f"last_input_at={st.get('last_input_at')}")
    finally:
        L.corral("stop", NAME, "--timeout", "45")
    return checks.done()


if __name__ == "__main__":
    sys.exit(main())
