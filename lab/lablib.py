"""lab 脚本共用：读 lab.env、调 corral、写日志、按契约送话、判定交付。只用标准库，兼容 Python 3.9。

lab 脚本扮演「调用方」，只用 corral 命令和它的 JSON 输出。标了「白盒」的函数会读 corral 的内部文件，
只给故障演练用，真正的调用方不许这么做。
"""
import json
import os
import re
import shlex
import subprocess
import sys
import time

LAB = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.environ.get("LAB_TMP", "/tmp/clab")
RUN = os.path.join(TMP, "run")
# 全局配置指纹的基线：放在仓库里，不能放 TMP——cleanup 会删掉整个 TMP，
# 而删完之后还要用它复验「手动删掉信任记录后配置是否回到原样」。
CONFHASH = os.path.join(LAB, "lab", ".confhash.json")
LAB_NAME_RE = re.compile(r"^lab(-[A-Za-z0-9]+)?/")
VERDICTS = ("delivered", "undelivered", "interrupted", "b_gone", "b_instance_changed", "wait_unknown")


# ---- 配置

def env_file():
    values = {}
    with open(os.path.join(LAB, "lab", "lab.env"), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip()
    return values


def agent_cmd(kind):
    """kind：claude / claude-ask / claude-dev / codex → 启动命令（列表）。"""
    key = "LAB_" + kind.upper().replace("-", "_")
    raw = os.environ.get(key) or env_file().get(key)
    if not raw:
        sys.exit(f"lab.env 里没有 {key}")
    return shlex.split(raw)


def token_of(prefix):
    return prefix.upper() + "-TOKEN"


# ---- corral

def corral(*args, timeout=None, exe=None):
    """运行 corral，返回 (退出码, JSON)。exe 或环境变量 LAB_CORRAL 可换成别的 corral（兼容演练用副本）。"""
    argv = shlex.split(exe or os.environ.get("LAB_CORRAL", "corral")) + [str(a) for a in args]
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return 124, {"ok": False, "error": "lab_timeout"}
    try:
        out = json.loads(p.stdout)
    except ValueError:
        out = {"ok": False, "raw": p.stdout, "stderr": p.stderr}
    return p.returncode, out


def wait_done(name, total=600.0, quiet=None, step=60, exe=None):
    """反复 corral wait（每次最多 step 秒），直到不是超时或总时间用完。返回最后一次的 (退出码, 输出)。"""
    deadline = time.time() + total
    while True:
        args = ["wait", name, "--timeout", str(step)] + (["--quiet", str(quiet)] if quiet else [])
        code, out = corral(*args, exe=exe)
        if code != 4 or time.time() >= deadline:
            return code, out


def list_agents():
    code, out = corral("ls")
    return out.get("agents", []) if code == 0 else []


def corral_home():
    return os.environ.get("CORRAL_HOME") or os.path.expanduser("~/.corral")


def pen_file(name, filename):
    """白盒：栏位内部文件的路径。"""
    return os.path.join(corral_home(), name, filename)


def pen_meta(name):
    """白盒：读 meta.json（pen_pid、agent_pid 等）。"""
    with open(pen_file(name, "meta.json"), encoding="utf-8") as f:
        return json.load(f)


def proc_command(pid):
    p = subprocess.run(["ps", "-p", str(pid), "-o", "command="], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else ""


def pid_alive(pid, marker):
    return bool(pid) and marker in proc_command(pid)


# ---- lab 目录

def lab_roots():
    return sorted({LAB, TMP, os.path.realpath(TMP)})


def under_roots(path):
    return bool(path) and any(path == r or path.startswith(r + "/") for r in lab_roots())


def is_lab_agent(item):
    return bool(LAB_NAME_RE.match(item.get("name", ""))) or under_roots(item.get("cwd"))


def run_dir(prefix):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", prefix):
        sys.exit(f"前缀不合法：{prefix!r}")
    return os.path.join(RUN, prefix)


def load_json(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {} if default is None else default


def save_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = f"{path}.{os.getpid()}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def read_jsonl(path):
    out = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def findings_state(path, sent_at):
    """交付判定：文件存在、是这一轮写的（修改时间不早于送出时间）、最后一个非空行是 DONE。返回 (是否交付, 说明)。"""
    if not os.path.exists(path):
        return False, "findings.md 不存在"
    if os.path.getmtime(path) < sent_at - 1:
        return False, "findings.md 是这一轮之前的旧文件"
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = [line.strip() for line in f.read().splitlines() if line.strip()]
    if not lines:
        return False, "findings.md 是空的"
    if lines[-1] != "DONE":
        return False, f"最后一行不是 DONE（是 {lines[-1][:40]!r}）"
    return True, "最后一行是 DONE"


# ---- 输出

def clock(t=None):
    return time.strftime("%H:%M:%S", time.localtime(t or time.time()))


class Log:
    """同时写标准输出和一个 JSONL 文件（可选）。"""

    def __init__(self, path=None, **base):
        self.path, self.base = path, base

    def __call__(self, event, **fields):
        t = time.time()
        extra = " ".join(f"{k}={v}" for k, v in fields.items() if v is not None)
        print(f"[{clock(t)}] {event} {extra}".rstrip(), flush=True)
        if self.path:
            rec = dict(self.base)
            rec.update(fields)
            rec.update(t=round(t, 3), event=event)
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")


class Checks:
    """逐条打印 PASS / FAIL / 记录，最后给出退出码。"""

    def __init__(self, title):
        self.failed = []
        print(f"== {title}", flush=True)

    def ok(self, label, cond, detail=""):
        cond = bool(cond)
        if not cond:
            self.failed.append(label)
        print(f"  {'PASS' if cond else 'FAIL'}  {label}" + (f"  —— {detail}" if detail else ""), flush=True)
        return cond

    def note(self, label, detail=""):
        print(f"  记录  {label}" + (f"  —— {detail}" if detail else ""), flush=True)

    def done(self):
        if self.failed:
            print(f"== 不通过：{len(self.failed)} 项：{'；'.join(self.failed)}", flush=True)
            return 1
        print("== 全部通过", flush=True)
        return 0


# ---- 按契约送话

def deliver(name, text, instance=None, every=5.0, give_up=1800.0, log=None, tag=""):
    """送一段话：每次先比对实例编号；7（不是 idle）等这一轮结束再试；8（人刚在窗口操作）过一会儿再试；
    3（没确认送达）不重试。返回 (结果, 输出)，结果是 delivered / instance_changed / gone / not_delivered /
    gave_up / error。

    已知限制：status 和 send 之间实例仍可能被换掉——corral send 没有「只送给某个实例」的参数。
    """
    log = log or Log()
    deadline = time.time() + give_up
    last = {}

    def note(event, **fields):
        key = (event, fields.get("state"))
        if key != last.get("key"):
            log(tag + event, name=name, **fields)
            last["key"] = key

    while True:
        code, st = corral("status", name)
        if code == 2:
            note("gone")
            return "gone", st
        if code != 0:
            note("error", code=code, error=st.get("error"))
            return "error", st
        if instance and st["instance"] != instance:
            note("instance_changed", expected=instance, actual=st["instance"])
            return "instance_changed", st
        code, out = corral("send", name, text, timeout=60)
        if code == 0:
            note("delivered", instance=out.get("instance"), latency=out.get("latency"))
            return "delivered", out
        if code == 3:
            note("not_delivered")
            return "not_delivered", out
        if code not in (7, 8):
            note("error", code=code, error=out.get("error"))
            return "error", out
        if time.time() >= deadline:
            note("gave_up")
            return "gave_up", out
        if code == 7:
            note("not_idle", state=out.get("state"))
            wcode, w = corral("wait", name, "--timeout", "60")
            if wcode == 0 and w.get("result") == "blocked":
                time.sleep(every)
        else:
            note("human_active", last_human_input=out.get("last_human_input"))
            time.sleep(every)
