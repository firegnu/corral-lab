#!/usr/bin/env python3
"""自检：用假 agent 把 lab 的调用方脚本和各步骤脚本跑一遍，确认脚本本身没问题。
不启动真实的 Claude Code / Codex，不花额度，不弹信任框，不改全局配置。

隔离：LAB_TMP=/tmp/clab-self、CORRAL_HOME=/tmp/clab-self/home（不碰 ~/.corral 和 /tmp/clab）；
lab.env 里的 agent 命令换成假 agent。结束时运行 lab/cleanup.py 并核对没有残留。
注意：worktree 从 main 的已提交内容建，改了 lab 脚本要先提交再自检。

用法：lab/selfcheck/run.py [--report 文件]
"""
import argparse
import json
import os
import pty
import shutil
import subprocess
import sys
import threading
import time
import traceback

SELF_TMP = "/tmp/clab-self"
LAB = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.update(LAB_TMP=SELF_TMP, CORRAL_HOME=os.path.join(SELF_TMP, "home"), LAB_NO_REAL="1",
                  LAB_NONINTERACTIVE="1")
for key in ("CORRAL_NAME", "CORRAL_INSTANCE", "CODEX_SANDBOX"):
    os.environ.pop(key, None)
sys.path.insert(0, os.path.join(LAB, "lab"))
import lablib as L  # noqa: E402

BIN = os.path.join(LAB, "lab", "bin")
STEPS = os.path.join(LAB, "lab", "steps")
RESULTS = []
FAKES = {}


# ---- 工具

def sh(argv, timeout=300, env=None, quiet=False):
    full = dict(os.environ)
    full.update(env or {})
    try:
        p = subprocess.run([str(a) for a in argv], capture_output=True, text=True, errors="replace", timeout=timeout,
                           env=full)
        code, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as e:
        code, out = 124, f"超时 {timeout}s：{e}"
    if not quiet:
        print(f"  $ {' '.join(os.path.relpath(str(a), LAB) if str(a).startswith(LAB) else str(a) for a in argv)}  → {code}")
        for line in out.rstrip().splitlines():
            print(f"    | {line}")
    return code, out


def step(name, script, *args, **kw):
    return sh([os.path.join(STEPS, name, script), *args], **kw)


def json_line(out):
    for line in reversed(out.strip().splitlines()):
        try:
            return json.loads(line)
        except ValueError:
            continue
    return {}


def fake_mode(prefix, mode):
    d = L.run_dir(prefix)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "fake-mode"), "w") as f:
        f.write(mode)


def write_request(prefix, body):
    d = L.run_dir(prefix)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "request.md"), "w", encoding="utf-8") as f:
        f.write(body)


def wait_for(fn, timeout=30.0, interval=0.5):
    deadline = time.time() + timeout
    while time.time() < deadline:
        value = fn()
        if value:
            return value
        time.sleep(interval)
    return fn()


def log_events(prefix):
    state = L.load_json(os.path.join(L.run_dir(prefix), "state.json"))
    return [e["event"] for e in L.read_jsonl(os.path.join(L.run_dir(prefix), "watch.log"))
            if e.get("round") == state.get("round")]


def start_fake(name, flavor="claude", cwd=None):
    code, out = L.corral("start", name, "--cwd", cwd or L.LAB, "--", FAKES[flavor], timeout=60)
    if code == 0:
        L.wait_done(name, total=20)
    return code, out


def make_fakes(corral_repo):
    for flavor in ("claude", "codex", "codex-nostart"):
        base = flavor.split("-")[0]
        d = os.path.join(SELF_TMP, "fake", flavor)
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, base)
        with open(path, "w") as f:
            f.write(f"#!{sys.executable}\nimport sys\nsys.path.insert(0, {os.path.dirname(os.path.abspath(__file__))!r})\n"
                    f"import labfake\nlabfake.main({corral_repo!r}, {flavor!r})\n")
        os.chmod(path, 0o700)
        FAKES[flavor] = path
    os.environ.update(LAB_CLAUDE=FAKES["claude"], LAB_CLAUDE_ASK=FAKES["claude"], LAB_CLAUDE_DEV=FAKES["claude"],
                      LAB_CODEX=FAKES["codex"])


class Window:
    """伪终端里跑 corral attach，模拟一个接入窗口。"""

    def __init__(self, name):
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.execvp("corral", ["corral", "attach", name])
        threading.Thread(target=self._drain, daemon=True).start()

    def _drain(self):
        while True:
            try:
                if not os.read(self.fd, 65536):
                    return
            except OSError:
                return

    def write(self, data):
        os.write(self.fd, data)

    def close(self):
        try:
            os.write(self.fd, b"\x1d")
        except OSError:
            pass
        for _ in range(50):
            if os.waitpid(self.pid, os.WNOHANG)[0]:
                break
            time.sleep(0.1)
        else:
            os.kill(self.pid, 9)
            os.waitpid(self.pid, 0)
        os.close(self.fd)


def section(title):
    def deco(fn):
        def run():
            print(f"\n######## {title}", flush=True)
            checks = L.Checks(title)
            t0 = time.time()
            try:
                fn(checks)
            except Exception as e:  # noqa: BLE001
                traceback.print_exc()
                checks.ok("没有异常", False, repr(e))
            RESULTS.append((title, list(checks.failed), time.time() - t0))
        return run
    return deco


def no_fail(checks, label, code_out):
    code, out = code_out
    fails = [line.strip() for line in out.splitlines() if line.strip().startswith("FAIL")]
    checks.ok(label, not fails, "；".join(fails)[:200])


# ---- 各部分

@section("00 环境基线（步骤脚本）")
def sec_baseline(c):
    code, _ = step("00-baseline", "prepare.sh")
    c.ok("00 prepare.sh 通过", code == 0)


@section("01 工作目录与探针")
def sec_workdirs(c):
    code, _ = step("01-workdirs", "prepare.sh")
    c.ok("01 prepare.sh", code == 0)
    for wt in ("wt-lab-a-review", "wt-lab-b", "wt-lab-b-review"):
        c.ok(f"worktree {wt} 建好，含 lab/bin", os.path.exists(os.path.join(SELF_TMP, wt, "lab", "bin", "handoff")))
    code, out = step("01-workdirs", "probe.py", "start", timeout=120)
    c.ok("probe.py start", code == 0 and "退出码 0" in out)
    c.ok("假 Claude 探针 idle", L.corral("status", "lab/probe-cc-main")[1].get("state") == "idle")
    c.ok("假 Codex 探针 starting（第一次提交前）", L.corral("status", "lab/probe-cx-main")[1].get("state") == "starting")
    code, _ = step("01-workdirs", "clean.sh", timeout=120)
    c.ok("01 clean.sh 停掉探针", code == 0 and not [i for i in L.list_agents() if "probe" in i["name"]])


@section("02 逐字送达（假 agent 逐字节比对）")
def sec_verbatim(c):
    c.ok("02 prepare.sh", step("02-verbatim", "prepare.sh")[0] == 0)
    c.ok("02 run.py --fake 全部通过", step("02-verbatim", "run.py", "--fake", timeout=300)[0] == 0)


@section("03 生命周期与故障")
def sec_lifecycle(c):
    c.ok("03 prepare.sh", step("03-lifecycle", "prepare.sh")[0] == 0)
    c.ok("03 run.py 全部通过", step("03-lifecycle", "run.py", timeout=300)[0] == 0)


@section("04 沙箱里被拒")
def sec_sandbox(c):
    c.ok("04 run.py 全部通过（跳过真沙箱）", step("04-sandbox", "run.py", timeout=120)[0] == 0)


@section("13 实例编号变了不送")
def sec_instance(c):
    c.ok("13 prepare.sh", step("13-instance", "prepare.sh")[0] == 0)
    c.ok("13 run.py 全部通过", step("13-instance", "run.py", timeout=120)[0] == 0)


@section("11/12 叫醒脚本：idle、忙（7）、人在窗口里操作（8）")
def sec_wake(c):
    name = "lab/sc-w"
    c.ok("start 假 Claude", start_fake(name)[0] == 0)
    code, out = sh([os.path.join(BIN, "wake"), name, "hello-1", "--every", "1", "--give-up", "20"], timeout=60)
    c.ok("idle 时直接送达", code == 0 and "delivered" in out)
    L.corral("send", name, "slow:4")
    code, out = sh([os.path.join(BIN, "wake"), name, "hello-2", "--every", "1", "--give-up", "30"], timeout=60)
    c.ok("忙时先 not_idle，这一轮结束后送达", code == 0 and "not_idle" in out and "delivered" in out)
    L.wait_done(name, total=20)
    w = Window(name)
    try:
        c.ok("接入窗口连上", wait_for(lambda: L.corral("status", name)[1].get("attached") == 1, 10))
        time.sleep(1)
        w.write(b"\x1b[A")   # 方向键：算人工按键，但假 agent 不会把它放进输入框
        t_key = time.time()
        code, out = sh([os.path.join(BIN, "wake"), name, "hello-3", "--every", "2", "--give-up", "90"], timeout=120)
        c.ok("人刚按过键：先 human_active，约 30 秒后送达", code == 0 and "human_active" in out and "delivered" in out,
             f"距按键 {time.time() - t_key:.0f}s")
        c.ok("送达时距最后一次按键至少 29 秒", time.time() - t_key >= 29)
    finally:
        w.close()
    L.wait_done(name, total=20)
    c.ok("回复是 echo: hello-3", L.corral("reply", name)[1].get("text") == "echo: hello-3")
    L.corral("stop", name)


@section("30/31 交接循环：启动、复用、归档、并发拒绝、实例变了拒绝、B 不在了重新 start")
def sec_handoff(c):
    code, _ = start_fake("lab-a/dev")
    c.ok("start 假 A（lab-a/dev）", code == 0)
    a_inst = L.corral("status", "lab-a/dev")[1]["instance"]
    write_request("lab-a", "LAB-A-TOKEN\n请评审。\n")
    fake_mode("lab-a", "done")
    code, out = sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev"], timeout=60)
    first = json_line(out)
    c.ok("第 1 轮：B 不在，start", code == 0 and first.get("b_action") == "started")
    c.ok("第 1 轮 roundcheck", sh([os.path.join(BIN, "roundcheck"), "lab-a", "--expect", "delivered",
                                   "--contains", "LAB-A-TOKEN", "--wait", "60"], timeout=90)[0] == 0)
    L.wait_done("lab-a/dev", total=20)
    c.ok("A 收到「评审结果到了」", "评审结果到了" in (L.corral("reply", "lab-a/dev")[1].get("text") or ""))

    code, out = sh([os.path.join(BIN, "handoff"), "lab-a"], env={"CORRAL_NAME": "lab-a/dev", "CORRAL_INSTANCE": a_inst},
                   timeout=60)
    second = json_line(out)
    c.ok("第 2 轮：用 CORRAL_NAME / CORRAL_INSTANCE 找 A，复用同一个 B",
         code == 0 and second.get("b_action") == "reused" and second.get("b_instance") == first.get("b_instance"))
    c.ok("第 1 轮结果归档为 findings-1.md", os.path.exists(os.path.join(L.run_dir("lab-a"), "findings-1.md")))
    sh([os.path.join(BIN, "roundcheck"), "lab-a", "--wait", "60"], timeout=90, quiet=True)
    no_fail(c, "31 check.sh 没有 FAIL", step("31-reuse", "check.sh", timeout=120))

    fake_mode("lab-a", "slow:5")
    sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev"], timeout=60)
    code, out = sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev"], timeout=60)
    c.ok("上一轮 watcher 还在时拒绝", code != 0 and "round_running" in out)
    c.ok("那一轮照常交付", sh([os.path.join(BIN, "roundcheck"), "lab-a", "--expect", "delivered", "--wait", "60"],
                              timeout=90)[0] == 0)

    L.corral("stop", "lab-a/review")
    L.corral("start", "lab-a/review", "--cwd", os.path.join(SELF_TMP, "wt-lab-a-review"), "--", FAKES["codex"])
    code, out = sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev"], timeout=60)
    c.ok("B 被别人重启过（实例变了）时拒绝", code != 0 and "b_changed" in out)
    L.corral("stop", "lab-a/review")

    fake_mode("lab-a", "done")
    code, out = sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev"], timeout=60)
    third = json_line(out)
    c.ok("B 不在了：重新 start，实例编号是新的",
         code == 0 and third.get("b_action") == "started" and third.get("b_instance") != first.get("b_instance"))
    sh([os.path.join(BIN, "roundcheck"), "lab-a", "--wait", "60"], timeout=90, quiet=True)

    L.corral("stop", "lab-a/review")
    L.wait_done("lab-a/dev", total=20)
    code, _ = step("32-long", "prepare.sh")
    c.ok("32 prepare.sh 生成长文件", code == 0)
    write_request("lab-a", f"LAB-A-TOKEN\n背景材料在 {L.run_dir('lab-a')}/long-context.md，读完后写出它最后一行的暗号。\n")
    code, out = sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev"], timeout=60)
    c.ok("长内容那一轮交接", code == 0)
    no_fail(c, "32 check.sh 没有 FAIL", step("32-long", "check.sh", timeout=120))


@section("40–44 异常路径：未交付、Esc 打断（两家）、权限框、B 忙、A 忙、卡在启动")
def sec_anomalies(c):
    L.wait_done("lab-a/dev", total=20)
    L.wait_done("lab-a/review", total=20)
    c.ok("41 prepare.sh", step("41-nodone", "prepare.sh")[0] == 0)
    fake_mode("lab-a", "nodone")
    sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev"], timeout=60)
    c.ok("41 check.sh 通过", step("41-nodone", "check.sh", timeout=120)[0] == 0)
    c.ok("判定是 undelivered", "undelivered" in log_events("lab-a"))
    L.wait_done("lab-a/dev", total=20)
    c.ok("A 收到「没有交付」", "没有交付" in (L.corral("reply", "lab-a/dev")[1].get("text") or ""))

    c.ok("42 prepare.sh", step("42-esc", "prepare.sh")[0] == 0)
    before = L.corral("status", "lab-a/dev")[1].get("last_input_at")
    fake_mode("lab-a", "hang")
    sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev", "--b", "lab-a/review-cc", "--b-kind", "claude",
        "--quiet", "3"], timeout=60)
    c.ok("42 check.sh a 通过（Claude：interrupted）", step("42-esc", "check.sh", "a", timeout=120)[0] == 0)
    c.ok("没有叫醒 A", L.corral("status", "lab-a/dev")[1].get("last_input_at") == before)
    L.corral("stop", "lab-a/review-cc")

    fake_mode("lab-a", "slow:30")
    sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev", "--quiet", "20"], timeout=60)
    time.sleep(3)
    L.corral("keys", "lab-a/review", "esc")
    code, out = step("42-esc", "check.sh", "b", timeout=120)
    c.ok("42 check.sh b：Codex 打断后判 undelivered", "PASS  判定是 undelivered" in out)
    c.ok("undelivered 那一行的最后事件是 Interrupt", '"last_event": "Interrupt"' in out)

    L.wait_done("lab-a/dev", total=20)
    c.ok("40 prepare.sh", step("40-permission", "prepare.sh")[0] == 0)
    fake_mode("lab-a", "ask")
    sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev", "--b", "lab-a/review-cc", "--b-kind", "claude-ask"],
       timeout=60)
    c.ok("watcher 记下 blocked", wait_for(lambda: "blocked" in log_events("lab-a"), 30))
    time.sleep(3)
    c.ok("框开着时一直是 blocked", L.corral("status", "lab-a/review-cc")[1].get("state") == "blocked")
    L.corral("keys", "lab-a/review-cc", "text:1")
    no_fail(c, "40 check.sh 没有 FAIL", step("40-permission", "check.sh", timeout=120))
    L.corral("stop", "lab-a/review-cc")

    L.wait_done("lab-a/dev", total=20)
    c.ok("43 prepare.sh", step("43-busy", "prepare.sh")[0] == 0)
    fake_mode("lab-a", "done")
    L.corral("send", "lab-a/review", "slow:5")
    sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev"], timeout=90)
    no_fail(c, "43 check.sh 没有 FAIL（B 忙时先 7 再送达）", step("43-busy", "check.sh", timeout=120))

    L.wait_done("lab-a/dev", total=20)
    fake_mode("lab-a", "slow:2")
    sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev"], timeout=60)
    L.corral("send", "lab-a/dev", "slow:6")
    c.ok("A 忙时照样交付", sh([os.path.join(BIN, "roundcheck"), "lab-a", "--expect", "delivered", "--wait", "60"],
                              timeout=90)[0] == 0)
    c.ok("叫醒 A 时先 7 再送达", "wake_a_not_idle" in log_events("lab-a") and "wake_a_delivered" in log_events("lab-a"))

    L.wait_done("lab-a/dev", total=20)
    code, _ = step("44-trust", "prepare.sh")
    c.ok("44 prepare.sh 建未信任目录", code == 0)
    untrusted = open(os.path.join(L.run_dir("lab-a"), "untrusted.txt")).read().strip()
    sh([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev", "--b", "lab-a/review-new", "--b-cwd", untrusted,
        "--start-timeout", "4"], env={"LAB_CODEX": FAKES["codex-nostart"]}, timeout=60)
    c.ok("watcher 记下 start_incomplete", wait_for(lambda: "start_incomplete" in log_events("lab-a"), 40))
    L.corral("stop", "lab-a/review-new")
    no_fail(c, "44 check.sh 没有 FAIL", step("44-trust", "check.sh", timeout=120))
    c.ok("44 clean.sh 删掉未信任目录", step("44-trust", "clean.sh", timeout=60)[0] == 0 and not os.path.exists(untrusted))


@section("50 两个项目并行（第二个项目用 worktree 里那份 handoff）")
def sec_two_projects(c):
    L.wait_done("lab-a/dev", total=20)
    c.ok("50 prepare.sh", step("50-two-projects", "prepare.sh")[0] == 0)
    code, _ = start_fake("lab-b/dev", cwd=os.path.join(SELF_TMP, "wt-lab-b"))
    c.ok("start 假 lab-b/dev", code == 0)
    write_request("lab-a", "LAB-A-TOKEN\n请评审任务 4。\n")
    write_request("lab-b", "LAB-B-TOKEN\n请评审 B1。\n")
    fake_mode("lab-a", "slow:2")
    fake_mode("lab-b", "slow:2")
    procs = [subprocess.Popen([os.path.join(BIN, "handoff"), "lab-a", "--a", "lab-a/dev"],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True),
             subprocess.Popen([os.path.join(SELF_TMP, "wt-lab-b", "lab", "bin", "handoff"), "lab-b", "--a", "lab-b/dev"],
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)]
    outs = [p.communicate(timeout=90)[0] for p in procs]
    for out in outs:
        print("    | " + out.strip())
    c.ok("两个 handoff 同时成功", all(p.returncode == 0 for p in procs))
    c.ok("50 check.sh 通过", step("50-two-projects", "check.sh", timeout=180)[0] == 0)
    c.ok("50 clean.sh", step("50-two-projects", "clean.sh", timeout=120)[0] == 0)


@section("60 协议兼容（旧版副本、协议 2、事件格式 2）")
def sec_compat(c):
    c.ok("60 prepare.sh", step("60-compat", "prepare.sh")[0] == 0)
    c.ok("60 run.py 全部通过", step("60-compat", "run.py", timeout=300)[0] == 0)


@section("61 事件文件增长（自检用 5MB）")
def sec_bigevents(c):
    c.ok("61 prepare.sh", step("61-bigevents", "prepare.sh")[0] == 0)
    c.ok("61 run.py --mb 5 全部通过", step("61-bigevents", "run.py", "--mb", "5", timeout=300)[0] == 0)


@section("工具与长时间步骤的脚本：fanout、board、snapshot、strays、need、70、71、confhash、traces、各 clean.sh")
def sec_tools(c):
    c.ok("fanout 3 全部通过", sh([os.path.join(BIN, "fanout"), "3", "--kind", "codex"], timeout=180)[0] == 0)
    code, out = sh([os.path.join(BIN, "board"), "--once"], timeout=60)
    c.ok("board --once 列出 lab-a/dev 和 watcher 记录", code == 0 and "lab-a/dev" in out and "交接 watcher" in out)
    c.ok("strays", sh([os.path.join(BIN, "strays")])[0] == 0)
    c.ok("need", sh([os.path.join(BIN, "need"), "lab-a/dev=idle"])[0] == 0
         and sh([os.path.join(BIN, "need"), "--absent", "lab/nothing"])[0] == 0
         and sh([os.path.join(BIN, "need"), "lab/nothing"])[0] == 1)
    c.ok("70 prepare.sh", step("70-quit-terminal", "prepare.sh", timeout=120)[0] == 0)
    c.ok("70 check.sh（快照比对）", step("70-quit-terminal", "check.sh", timeout=120)[0] == 0)
    c.ok("71 prepare.sh（晚上）", step("71-overnight", "prepare.sh", timeout=120)[0] == 0)
    code, out = step("71-overnight", "morning.sh", timeout=120)
    c.ok("71 morning.sh（早上）快照比对通过", code == 0 and "全部通过" in out)
    c.ok("confhash check：全局配置没变", sh([os.path.join(BIN, "confhash"), "check"])[0] == 0)
    c.ok("traces 能列出", sh([os.path.join(BIN, "traces")], timeout=120)[0] == 0)
    c.ok("unwatch --all", sh([os.path.join(BIN, "unwatch"), "--all"])[0] == 0)
    for name in sorted(os.listdir(STEPS)):
        if os.path.isdir(os.path.join(STEPS, name)):
            code, _ = step(name, "clean.sh", timeout=180)
            c.ok(f"{name}/clean.sh 能跑", code == 0)


@section("cleanup.py 清理并核对没有残留")
def sec_cleanup(c):
    code, _ = sh([os.path.join(LAB, "lab", "cleanup.py")], timeout=300)
    c.ok("cleanup.py", code == 0)
    c.ok(f"{SELF_TMP} 已删", not os.path.exists(SELF_TMP))
    wt = subprocess.run(["git", "-C", LAB, "worktree", "list"], capture_output=True, text=True).stdout
    c.ok("没有残留 worktree", "clab-self" not in wt, wt.strip())
    br = subprocess.run(["git", "-C", LAB, "branch", "--list", "lab/*"], capture_output=True, text=True).stdout
    c.ok("没有残留 lab/ 分支", not br.strip(), br.strip())
    procs = {}
    for line in subprocess.run(["ps", "-axo", "pid=,ppid=,command="], capture_output=True, text=True).stdout.splitlines():
        pid, ppid, cmd = (line.strip().split(None, 2) + ["", ""])[:3]
        procs[int(pid)] = (int(ppid), cmd)
    ancestors, pid = set(), os.getpid()
    while pid in procs and pid not in ancestors:   # 启动自检的 shell 命令行里也可能含 clab-self，不算残留
        ancestors.add(pid)
        pid = procs[pid][0]
    left = [cmd for pid, (_, cmd) in procs.items() if "clab-self" in cmd and pid not in ancestors]
    c.ok("没有残留进程", not left, "；".join(left)[:200])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report")
    args = ap.parse_args()
    t0 = time.time()
    if os.path.exists(SELF_TMP):
        print(f"发现上次自检残留 {SELF_TMP}，先清理")
        subprocess.run([sys.executable, os.path.join(LAB, "lab", "cleanup.py")], capture_output=True)
        shutil.rmtree(SELF_TMP, ignore_errors=True)
    corral_repo = os.path.dirname(os.path.dirname(os.path.realpath(shutil.which("corral") or "")))
    make_fakes(corral_repo)
    head = subprocess.run(["git", "-C", corral_repo, "log", "-1", "--format=%h"], capture_output=True, text=True).stdout.strip()
    lab_head = subprocess.run(["git", "-C", LAB, "log", "-1", "--format=%h"], capture_output=True, text=True).stdout.strip()
    try:
        for sec in (sec_baseline, sec_workdirs, sec_verbatim, sec_lifecycle, sec_sandbox, sec_instance, sec_wake,
                    sec_handoff, sec_anomalies, sec_two_projects, sec_compat, sec_bigevents, sec_tools):
            sec()
    finally:
        sec_cleanup()

    total_failed = sum(len(f) for _, f, _ in RESULTS)
    lines = ["# 自检结果", "",
             f"- 时间：{time.strftime('%Y-%m-%d %H:%M')}，用时 {(time.time() - t0) / 60:.1f} 分钟",
             f"- corral 提交：{head}；corral-lab 提交：{lab_head}",
             "- 方式：假 agent（不启动真实 Claude Code / Codex），隔离在 /tmp/clab-self",
             f"- 结论：{'全部通过' if not total_failed else f'{total_failed} 项不通过'}", "",
             "| 部分 | 结果 | 用时 |", "|---|---|---|"]
    for title, failed, dt in RESULTS:
        lines.append(f"| {title} | {'通过' if not failed else '不通过：' + '；'.join(failed)} | {dt:.0f}s |")
    report = "\n".join(lines) + "\n"
    print("\n" + report)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(report)
    return 1 if total_failed else 0


if __name__ == "__main__":
    sys.exit(main())
