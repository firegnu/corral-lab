#!/usr/bin/env python3
"""步骤 03（故障演练）：同名重复 start、stop 后立刻同名 start、kill -9 栏位、kill -9 agent。

Codex 只送一句「只回复：好」（为了让 stop 走真正的收尾），其余不送话。
kill -9 栏位要知道栏位进程号，这里读 meta.json（白盒，调用方不许这么做）。
"""
import os
import signal
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lablib as L  # noqa: E402


def start(name, kind, prompt=None):
    extra = ["--prompt", prompt] if prompt else []
    return L.corral("start", name, "--cwd", L.LAB, *extra, "--", *L.agent_cmd(kind), timeout=90)


def until_gone(name, total=15):
    deadline = time.time() + total
    while time.time() < deadline:
        code, out = L.corral("status", name)
        if code == 2:
            return out
        time.sleep(0.5)
    return None


def main():
    checks = L.Checks("03 生命周期与故障")
    cx, cc = "lab/life-cx", "lab/life-cc"
    try:
        # 同名重复 start
        code, out = start(cx, "codex", "只回复：好")
        if not checks.ok("Codex start", code == 0, out.get("error", "")):
            return checks.done()
        wcode, w = L.wait_done(cx, total=180)
        checks.ok("Codex 答完第一句", wcode == 0 and w.get("result") == "idle", f"result={w.get('result')}")
        code, out = start(cx, "codex")
        checks.ok("同名再 start → 退出码 5", code == 5, f"退出码 {code} {out.get('error')}")

        # 再跑两轮，让这是一个「用过的」会话：Codex 的收尾时间随会话内容增长
        # （实测刚起 13–15 秒，跑过三轮 27.7 秒），ISSUES 第 3 条就是这么撞上旧的 20 秒上限的
        for n in (2, 3):
            L.corral("send", cx, f"只回复：第 {n} 句")
            L.wait_done(cx, total=180)

        # stop 后立刻同名 start
        t0 = time.time()
        code, out = L.corral("stop", cx, "--timeout", "120")
        took = time.time() - t0
        detail = f"用时 {took:.1f}s stopped_by={out.get('stopped_by')} exit_code={out.get('exit_code')}"
        checks.ok("Codex stop", code == 0, detail)
        # 回归检查（ISSUES 第 3 条，corral 48fb26a 把等待从 20 秒放宽到 60 秒）：
        # 跑过几轮的 Codex 必须是自己正常退出，不能是等不及被 SIGTERM 杀掉
        checks.ok("Codex stop 是正常收尾，不是被 SIGTERM 截断",
                  out.get("stopped_by") == "keys" and out.get("exit_code") == 0, detail)
        checks.ok("收尾用时在放宽后的 60 秒以内", took < 60, f"{took:.1f}s")
        code, out = start(cx, "codex")
        checks.ok("stop 后立刻同名 start（不撞锁）", code == 0, out.get("error", ""))

        # kill -9 栏位
        meta = L.pen_meta(cx)
        os.kill(meta["pen_pid"], signal.SIGKILL)
        time.sleep(1)
        names = [i["name"] for i in L.list_agents()]
        checks.ok("kill -9 栏位后 ls 不再列出", cx not in names)
        checks.ok("status → 退出码 2", L.corral("status", cx)[0] == 2)
        time.sleep(3)
        agent_cmd = L.proc_command(meta["agent_pid"])
        if agent_cmd:
            checks.note("栏位被杀 3 秒后 agent 进程还在（孤儿）", f"pid {meta['agent_pid']}：{agent_cmd[:80]}；已 SIGTERM")
            os.kill(meta["agent_pid"], signal.SIGTERM)
        else:
            checks.note("栏位被杀后 agent 进程也退出了")
        code, out = start(cx, "codex")
        checks.ok("kill -9 栏位后同名重新 start", code == 0, out.get("error", ""))
        code, out = L.corral("stop", cx, "--timeout", "120")
        checks.ok("再 stop", code == 0, f"stopped_by={out.get('stopped_by')}")

        # kill -9 agent
        code, out = start(cc, "claude")
        if checks.ok("Claude Code start", code == 0, out.get("error", "")):
            wcode, w = L.wait_done(cc, total=60)
            checks.ok("Claude Code 进入 idle", wcode == 0 and w.get("result") == "idle", f"result={w.get('result')}")
            _, where = L.corral("where", cc)
            os.kill(where["agent_pid"], signal.SIGKILL)
            gone = until_gone(cc)
            exited = (gone or {}).get("exited") or {}
            checks.ok("kill -9 agent 后 status → 2，exited 记下退出码", gone is not None and exited.get("code") == -9,
                      str(exited))
            code, out = start(cc, "claude")
            checks.ok("同名重新 start", code == 0, out.get("error", ""))
            code, out = L.corral("stop", cc, "--timeout", "120")
            checks.ok("Claude Code stop", code == 0, f"stopped_by={out.get('stopped_by')} exit_code={out.get('exit_code')}")
    finally:
        for name in (cx, cc):
            if L.corral("status", name)[0] == 0:
                L.corral("stop", name, "--timeout", "120")
    return checks.done()


if __name__ == "__main__":
    sys.exit(main())
