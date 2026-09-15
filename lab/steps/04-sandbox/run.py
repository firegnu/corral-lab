#!/usr/bin/env python3
"""步骤 04（故障演练）：在 Codex 沙箱里运行 corral 被拒（退出码 6）。

1. 带 CODEX_SANDBOX 环境变量跑各个命令 → 6；guide、--version → 0
2. 真沙箱：codex sandbox -P :workspace -C <corral-lab> -- corral ls → 6（只跑命令，不调模型；LAB_NO_REAL=1 时跳过）
"""
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lablib as L  # noqa: E402

COMMANDS = (["ls"], ["status", "lab/sbx"], ["start", "lab/sbx", "--", "sh"], ["send", "lab/sbx", "hi"],
            ["keys", "lab/sbx", "esc"], ["wait", "lab/sbx"], ["reply", "lab/sbx"], ["where", "lab/sbx"],
            ["read", "lab/sbx"], ["attach", "lab/sbx"], ["stop", "lab/sbx"], ["install-skills", "--dry-run"])


def run(argv, env):
    p = subprocess.run(argv, capture_output=True, text=True, env=env, timeout=60)
    try:
        out = json.loads(p.stdout)
    except ValueError:
        out = {"raw": (p.stdout + p.stderr)[:200]}
    return p.returncode, out


def main():
    checks = L.Checks("04 沙箱里被拒")
    env = dict(os.environ, CODEX_SANDBOX="seatbelt")
    for args in COMMANDS:
        code, out = run(["corral", *args], env)
        checks.ok(f"CODEX_SANDBOX 下 corral {args[0]} → 6", code == 6 and out.get("error") == "sandbox", f"退出码 {code}")
    code, _ = run(["corral", "guide"], env)
    checks.ok("CODEX_SANDBOX 下 corral guide → 0", code == 0)
    code, _ = run(["corral", "--version"], env)
    checks.ok("CODEX_SANDBOX 下 corral --version → 0", code == 0)
    if os.environ.get("LAB_NO_REAL") == "1":
        checks.note("跳过真沙箱（LAB_NO_REAL=1）")
    else:
        code, out = run(["codex", "sandbox", "-P", ":workspace", "-C", L.LAB, "--", "corral", "ls"], dict(os.environ))
        checks.ok("真 Codex 沙箱里 corral ls → 6", code == 6, f"退出码 {code} message={out.get('message', out)}")
    return checks.done()


if __name__ == "__main__":
    sys.exit(main())
