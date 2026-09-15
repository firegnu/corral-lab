#!/usr/bin/env python3
"""全部清理：把 corral-lab 之外的测试痕迹去掉，改不了的列出来请人手动处理。

用法：lab/cleanup.py [--purge-transcripts]

按顺序：
1. 停掉 lab 的后台脚本（watch-deliver、wake、board、fanout）
2. stop lab 的 agent：名字以 lab/、lab-*/ 开头，或工作目录在 lab 目录里（skill 起的临时 agent）；
   协议不兼容的（兼容演练留下的）先用演练副本 stop，不行再（白盒）结束栏位进程
3. 删掉这些名字在状态目录里的残留目录，状态目录删空了就删掉它
4. 移除 $LAB_TMP 下的 git worktree，删掉 lab/ 开头的分支
5. 比对全局配置指纹（lab/bin/confhash check）
6. 删掉 $LAB_TMP
7. 列出其他痕迹（lab/bin/traces）：信任记录请手动删；对话记录加 --purge-transcripts 才删
"""
import argparse
import os
import re
import shutil
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lablib as L  # noqa: E402

BIN = os.path.join(L.LAB, "lab", "bin")
SCRIPTS = ("watch-deliver", "wake", "board", "fanout")


def step(title):
    print(f"\n== {title}", flush=True)


def kill_scripts():
    ps = subprocess.run(["ps", "-axo", "pid=,command="], capture_output=True, text=True).stdout
    n = 0
    for line in ps.splitlines():
        pid, _, cmd = line.strip().partition(" ")
        # worktree 里也有一份 lab/bin（第二个项目的 A 在 worktree 里运行 handoff）
        ours = any(f"/lab/bin/{s}" in cmd for s in SCRIPTS) and any(r + "/" in cmd for r in L.lab_roots())
        if pid.isdigit() and int(pid) != os.getpid() and ours:
            try:
                os.kill(int(pid), signal.SIGTERM)
                print(f"  已停 pid {pid}：{cmd[:100]}")
                n += 1
            except OSError:
                pass
    if not n:
        print("  没有在跑的")


def compat_copies():
    if not os.path.isdir(L.TMP):
        return []
    return [os.path.join(L.TMP, d, "bin", "corral") for d in sorted(os.listdir(L.TMP))
            if d.startswith("corral-") and os.path.exists(os.path.join(L.TMP, d, "bin", "corral"))]


def stop_agents():
    names = []
    for item in L.list_agents():
        name = item["name"]
        if not L.is_lab_agent(item):
            if item.get("starting"):
                print(f"  跳过 {name}：还在启动，看不到工作目录（不是 lab 前缀，可能不是 lab 的）")
            continue
        names.append(name)
        code, out = L.corral("stop", name, "--timeout", "45")
        if code == 9:
            for exe in compat_copies():
                code, out = L.corral("stop", name, "--timeout", "45", exe=exe)
                if code == 0:
                    break
        if code == 9:
            try:
                pid = L.pen_meta(name)["pen_pid"]
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                code = 0 if L.corral("status", name)[0] != 0 else code
                print(f"  （白盒）结束了不兼容栏位的进程 pid {pid}")
            except (OSError, KeyError, ValueError):
                pass
        print(f"  stop {name} → 退出码 {code} {out.get('stopped_by') or out.get('error') or ''}")
    if not names:
        print("  没有 lab 的 agent")
    return names


def remove_pen_dirs(stopped):
    home = L.corral_home()
    candidates = set(stopped)
    if os.path.isdir(home):
        for top in os.listdir(home):
            if re.fullmatch(r"lab(-[A-Za-z0-9]+)?", top):
                for root, _, files in os.walk(os.path.join(home, top)):
                    if "meta.json" in files or "exit.json" in files or "lock" in files:
                        candidates.add(os.path.relpath(root, home))
    removed = 0
    for name in sorted(candidates):
        path = os.path.join(home, name)
        if not os.path.isdir(path) or L.corral("status", name)[0] != 2:
            continue
        shutil.rmtree(path, ignore_errors=True)
        removed += 1
        parent = os.path.dirname(path)
        while parent != home and os.path.isdir(parent) and not os.listdir(parent):
            os.rmdir(parent)
            parent = os.path.dirname(parent)
    print(f"  删了 {removed} 个名字目录")
    if os.path.isdir(home) and not os.listdir(home):
        os.rmdir(home)
        print(f"  {home} 已空，删掉")
    elif os.path.isdir(home):
        print(f"  {home} 里还有：{', '.join(sorted(os.listdir(home)))}（不是 lab 的，不动）")


def remove_worktrees():
    git = ["git", "-C", L.LAB]
    out = subprocess.run(git + ["worktree", "list", "--porcelain"], capture_output=True, text=True).stdout
    for line in out.splitlines():
        if line.startswith("worktree "):
            path = line[len("worktree "):]
            if path != L.LAB and L.under_roots(path):
                r = subprocess.run(git + ["worktree", "remove", "--force", path], capture_output=True, text=True)
                print(f"  移除 worktree {path} → {'OK' if r.returncode == 0 else r.stderr.strip()}")
    subprocess.run(git + ["worktree", "prune"])
    branches = subprocess.run(git + ["for-each-ref", "--format=%(refname:short)", "refs/heads/lab/"],
                              capture_output=True, text=True).stdout.split()
    for br in branches:
        subprocess.run(git + ["branch", "-D", br], capture_output=True)
        print(f"  删除分支 {br}")


def main():
    ap = argparse.ArgumentParser(prog="cleanup")
    ap.add_argument("--purge-transcripts", action="store_true")
    args = ap.parse_args()
    if not re.fullmatch(r"/(private/)?tmp/clab[A-Za-z0-9._-]*", L.TMP):
        sys.exit(f"LAB_TMP={L.TMP} 不在 /tmp/clab* 下，拒绝清理")
    print(f"清理：LAB_TMP={L.TMP}  状态目录={L.corral_home()}")

    step("1. 停掉 lab 的后台脚本")
    kill_scripts()
    step("2. stop lab 的 agent")
    stopped = stop_agents()
    step("3. 删状态目录里的残留")
    remove_pen_dirs(stopped)
    step("4. 移除 worktree 和 lab/ 分支")
    remove_worktrees()
    step("5. 全局配置指纹")
    if os.path.exists(os.path.join(L.TMP, "confhash.json")):
        subprocess.run([sys.executable, os.path.join(BIN, "confhash"), "check"])
    else:
        print("  没有基线（没做过准备步骤 00），跳过")
    step(f"6. 删除 {L.TMP}")
    shutil.rmtree(L.TMP, ignore_errors=True)
    print("  已删除" if not os.path.exists(L.TMP) else "  删除失败")
    step("7. 其他痕迹")
    subprocess.run([sys.executable, os.path.join(BIN, "traces")] + (["--purge-transcripts"] if args.purge_transcripts else []))
    print("\n提示：测试中 agent 在 corral-lab 里做的提交还留着；要回到初始状态：git -C "
          f"{L.LAB} reset --hard lab-baseline")
    return 0


if __name__ == "__main__":
    sys.exit(main())
