#!/usr/bin/env python3
"""步骤 00：环境基线。只读检查，最后记下全局配置指纹。"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lablib as L  # noqa: E402


def run(argv, cwd=None):
    try:
        p = subprocess.run(argv, capture_output=True, text=True, cwd=cwd, timeout=120)
        return p.returncode, (p.stdout + p.stderr).strip()
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, str(e)


def main():
    checks = L.Checks("00 环境基线")
    corral_path = shutil.which("corral")
    if not checks.ok("corral 在 PATH 上", corral_path, str(corral_path)):
        return checks.done()
    repo = os.path.dirname(os.path.dirname(os.path.realpath(corral_path)))
    code, ver = L.corral("--version")
    checks.ok("corral --version，契约版本 1", code == 0 and ver.get("contract") == "1", str(ver))
    code, head = run(["git", "-C", repo, "log", "-1", "--format=%h %s"])
    checks.note("corral 仓库和提交", f"{repo}  {head}")
    code, out = run(["/usr/bin/python3", "-c", "import json,os,sys,time"])
    checks.ok("/usr/bin/python3 可用（钩子要用）", code == 0, out)
    for tool in ("claude", "codex"):
        code, out = run([tool, "--version"])
        checks.ok(f"{tool} 可用", code == 0, out.splitlines()[0] if out else "")
    code, out = L.corral("install-skills", "--dry-run")
    items = out.get("items", [])
    checks.ok("两家的全局 skill 已装且和 corral 仓库一致", code == 0 and items and all(i["status"] == "same" for i in items),
              "；".join(f"{i['agent']} {i['status']} {i['path']}" for i in items))
    lab_agents = [i["name"] for i in L.list_agents() if L.is_lab_agent(i)]
    checks.ok("没有 lab 的 agent 在跑", not lab_agents, " ".join(lab_agents))
    code, out = run([sys.executable, "-m", "unittest"], cwd=L.LAB)
    checks.ok("corral-lab 的单元测试通过", code == 0, out.splitlines()[-1] if out else "")
    code, _ = run(["git", "-C", L.LAB, "rev-parse", "-q", "--verify", "refs/tags/lab-baseline"])
    if code != 0:
        checks.note("警告：没有 lab-baseline 标签", "清理时无法提示回到初始提交")
    code, out = run(["git", "-C", L.LAB, "status", "--porcelain"])
    if out:
        checks.note("警告：corral-lab 工作区不干净", out.replace("\n", "；")[:200])
    subprocess.run([sys.executable, os.path.join(L.LAB, "lab", "bin", "confhash"), "save"])
    return checks.done()


if __name__ == "__main__":
    sys.exit(main())
