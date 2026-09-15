#!/usr/bin/env python3
"""步骤 61（故障演练）：事件文件长期增长后 status 仍然快。

1. 起一个 Claude Code（lab/big，不带首句），量 status 耗时的中位数（基线）
2. （白盒）往它的事件文件追加约 --mb 兆的「别的会话」事件（模拟内部子会话长期写进来的噪声）
3. 量追加后第一次 status（要读完新增部分）和之后稳定的耗时
4. 送一句话、wait、reply，确认状态计算仍然正确
5. （白盒）删掉读取进度文件 cursor，量从头重算一次的耗时（只记录）
通过标准：稳定耗时中位数不超过基线 + 100ms；送话、等待、回复正常。
"""
import argparse
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lablib as L  # noqa: E402

NAME = "lab/big"


def timed_status():
    t0 = time.time()
    code, st = L.corral("status", NAME)
    return (time.time() - t0) * 1000, code, st


def median_ms(n=7):
    return round(statistics.median(timed_status()[0] for _ in range(n)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mb", type=int, default=50)
    args = ap.parse_args()
    checks = L.Checks(f"61 事件文件增长 {args.mb}MB")
    try:
        code, out = L.corral("start", NAME, "--cwd", L.LAB, "--", *L.agent_cmd("claude"), timeout=90)
        if not checks.ok("start", code == 0, out.get("error", "")):
            return checks.done()
        inst = out["instance"]
        L.wait_done(NAME, total=60)
        base = median_ms()
        checks.note("基线 status 中位数", f"{base}ms")

        events = L.pen_file(NAME, "events")
        size0 = os.path.getsize(events)
        template = {"v": 1, "ev": "PreToolUse", "inst": inst, "has_transcript": False, "cwd": "/tmp", "tool_name": "Bash"}
        target = args.mb * 1024 * 1024
        n = 0
        with open(events, "a", encoding="utf-8") as f:
            while os.path.getsize(events) - size0 < target:
                chunk = []
                for _ in range(5000):
                    n += 1
                    chunk.append(json.dumps(dict(template, t=time.time(), session_id=f"noise-{n % 50}"),
                                            ensure_ascii=False))
                f.write("\n".join(chunk) + "\n")
                f.flush()
        checks.note("追加", f"{n} 行，事件文件 {size0} → {os.path.getsize(events)} 字节")

        first, code, st = timed_status()
        checks.ok("追加后第一次 status 正常", code == 0 and st.get("state") == "idle", f"{first:.0f}ms state={st.get('state')}")
        steady = median_ms()
        checks.ok("之后 status 中位数不超过基线 + 100ms", steady <= base + 100, f"{steady}ms（基线 {base}ms）")

        code, out = L.corral("send", NAME, "只回复：收到", timeout=60)
        checks.ok("send 确认送达", code == 0 and out.get("confirmed"), f"退出码 {code}")
        code, w = L.wait_done(NAME, total=180)
        checks.ok("wait 返回 idle", code == 0 and w.get("result") == "idle", f"result={w.get('result')}")
        code, r = L.corral("reply", NAME)
        checks.ok("reply 有内容", code == 0 and r.get("text"), (r.get("text") or "")[:40])

        os.remove(L.pen_file(NAME, "cursor"))
        recompute, code, st = timed_status()
        checks.note("删掉 cursor 后从头重算一次", f"{recompute:.0f}ms state={st.get('state')}")
        checks.ok("重算后状态仍是 idle", code == 0 and st.get("state") == "idle")
        checks.note("重算后再量中位数", f"{median_ms()}ms")
    finally:
        L.corral("stop", NAME, "--timeout", "45")
    return checks.done()


if __name__ == "__main__":
    sys.exit(main())
