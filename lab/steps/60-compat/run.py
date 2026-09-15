#!/usr/bin/env python3
"""步骤 60（故障演练）：改动 corral 代码后，新命令操作旧栏位。不改 corral 仓库，只用 git archive 导出的副本。

A. 旧版本：用旧提交（默认 c75876e，M0–M7；可用环境变量 LAB_COMPAT_OLD 换）的副本起一个 Claude Code，
   删掉副本，再用当前 corral 做 status / send / wait / reply / attach（人）/ stop
B. 协议版本不认识：副本里把栏位协议改成 2 → 当前命令 status / ls / stop 应以退出码 9 拒绝；用副本自己的 corral stop
C. 事件格式不认识：副本里把钩子事件格式改成 2 → 当前命令 status 应以退出码 9 拒绝；用副本自己的 corral stop
改副本里的版本号是测试手段（白盒）。设了 LAB_NONINTERACTIVE=1 时跳过人工 attach 那一步。
"""
import os
import shutil
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lablib as L  # noqa: E402


def corral_repo():
    return os.path.dirname(os.path.dirname(os.path.realpath(shutil.which("corral") or "")))


def export(ref, name):
    dest = os.path.join(L.TMP, name)
    shutil.rmtree(dest, ignore_errors=True)
    os.makedirs(dest)
    archive = subprocess.Popen(["git", "-C", corral_repo(), "archive", ref], stdout=subprocess.PIPE)
    subprocess.run(["tar", "-x", "-C", dest], stdin=archive.stdout, check=True)
    archive.wait()
    return dest


def patch(path, old, new):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    if text.count(old) != 1:
        sys.exit(f"{path} 里找不到唯一的 {old!r}，corral 代码变了，要更新这个演练脚本")
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.replace(old, new))


def start(name, exe):
    return L.corral("start", name, "--cwd", L.LAB, "--", *L.agent_cmd("claude"), timeout=90, exe=exe)


def main():
    checks = L.Checks("60 协议兼容")
    old_ref = os.environ.get("LAB_COMPAT_OLD", "c75876e")
    head = subprocess.run(["git", "-C", corral_repo(), "log", "-1", "--format=%h"], capture_output=True, text=True).stdout.strip()
    checks.note("版本", f"当前 corral {head}，旧版副本 {old_ref}")
    leftovers = []
    try:
        # A
        old = export(old_ref, "corral-old")
        code, out = start("lab/compat-old", os.path.join(old, "bin", "corral"))
        if checks.ok("A 旧版副本 start", code == 0, out.get("error", "")):
            leftovers.append(("lab/compat-old", None))
            L.wait_done("lab/compat-old", total=60)
            shutil.rmtree(old)
            checks.ok("A 旧版副本已删掉", not os.path.exists(old))
            code, st = L.corral("status", "lab/compat-old")
            checks.ok("A 当前命令 status", code == 0 and st.get("proto") == 1 and st.get("state") == "idle",
                      f"退出码 {code} proto={st.get('proto')} state={st.get('state')}")
            code, out = L.corral("send", "lab/compat-old", "只回复：收到", timeout=60)
            checks.ok("A 当前命令 send 确认送达", code == 0 and out.get("confirmed"), f"退出码 {code}")
            code, w = L.wait_done("lab/compat-old", total=180)
            checks.ok("A 当前命令 wait", code == 0 and w.get("result") == "idle", f"result={w.get('result')}")
            code, r = L.corral("reply", "lab/compat-old")
            checks.ok("A 当前命令 reply", code == 0 and r.get("text"), (r.get("text") or "")[:40])
            if os.environ.get("LAB_NONINTERACTIVE") != "1":
                input("  人工：另开一个窗口运行 corral attach lab/compat-old，看到界面后按 Ctrl-] 退出，然后回到这里按回车… ")
                checks.note("A attach 由人确认，结果记在 CHECKLIST")
            code, out = L.corral("stop", "lab/compat-old", "--timeout", "45")
            checks.ok("A 当前命令 stop", code == 0, f"stopped_by={out.get('stopped_by')}")

        # B
        p2 = export("HEAD", "corral-p2")
        patch(os.path.join(p2, "src", "corral", "protocol.py"), "PROTOCOL_VERSION = 1", "PROTOCOL_VERSION = 2")
        patch(os.path.join(p2, "src", "corral", "protocol.py"), "SUPPORTED_PROTOCOLS = (1,)", "SUPPORTED_PROTOCOLS = (2,)")
        p2_exe = os.path.join(p2, "bin", "corral")
        code, out = start("lab/compat-p2", p2_exe)
        if checks.ok("B 协议 2 的副本 start", code == 0, out.get("error", "")):
            leftovers.append(("lab/compat-p2", p2_exe))
            code, st = L.corral("status", "lab/compat-p2")
            checks.ok("B 当前命令 status → 9", code == 9, f"退出码 {code} {st.get('error')} {st.get('message', '')[:80]}")
            item = [i for i in L.list_agents() if i["name"] == "lab/compat-p2"]
            checks.ok("B 当前命令 ls 标出 incompatible", item and item[0].get("incompatible"), str(item))
            code, out = L.corral("stop", "lab/compat-p2")
            checks.ok("B 当前命令 stop → 9", code == 9, f"退出码 {code}")
            code, out = L.corral("stop", "lab/compat-p2", "--timeout", "45", exe=p2_exe)
            checks.ok("B 副本自己的 corral stop", code == 0, f"退出码 {code}")

        # C
        e2 = export("HEAD", "corral-e2")
        patch(os.path.join(e2, "src", "corral", "hook.py"), "FORMAT = 1", "FORMAT = 2")
        patch(os.path.join(e2, "src", "corral", "events.py"), "EVENT_FORMATS = (1,)", "EVENT_FORMATS = (2,)")
        e2_exe = os.path.join(e2, "bin", "corral")
        code, out = start("lab/compat-e2", e2_exe)
        if checks.ok("C 事件格式 2 的副本 start", code == 0, out.get("error", "")):
            leftovers.append(("lab/compat-e2", e2_exe))
            # 先等钩子写出第一行事件（白盒：看事件文件大小），再让当前命令第一个去读
            events = L.pen_file("lab/compat-e2", "events")
            deadline = time.time() + 30
            while time.time() < deadline and not (os.path.exists(events) and os.path.getsize(events) > 0):
                time.sleep(0.5)
            code, st = L.corral("status", "lab/compat-e2")
            checks.ok("C 当前命令 status → 9", code == 9, f"退出码 {code} {st.get('error')} {st.get('message', '')[:80]}")
            code, w = L.wait_done("lab/compat-e2", total=60, exe=e2_exe)
            checks.ok("C 副本自己的 corral wait 能读", code == 0, f"result={w.get('result')}")
            code, st = L.corral("status", "lab/compat-e2")
            checks.note("C 副本读过之后，当前命令再 status", f"退出码 {code}（0 表示直接用了副本写下的读取进度，没有再检查事件格式）")
            code, out = L.corral("stop", "lab/compat-e2", "--timeout", "45", exe=e2_exe)
            checks.ok("C 副本自己的 corral stop", code == 0, f"退出码 {code}")
    finally:
        for name, exe in leftovers:
            if L.corral("status", name, exe=exe)[0] == 0:
                L.corral("stop", name, "--timeout", "45", exe=exe)
        for d in ("corral-old", "corral-p2", "corral-e2"):
            shutil.rmtree(os.path.join(L.TMP, d), ignore_errors=True)
    return checks.done()


if __name__ == "__main__":
    sys.exit(main())
