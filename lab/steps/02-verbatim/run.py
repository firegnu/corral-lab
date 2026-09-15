#!/usr/bin/env python3
"""步骤 02：送话逐字送达。首句（--prompt）和 send 各送一段含特殊字符的内容，再单独送一行问号开头的话。

用法：run.py [claude|codex]…（默认两家都做）   run.py --fake（自检：假 agent 回复 "echo: <原文>"，逐字节比对）
自动判定：start / send 确认送达（confirmed: true）。
人看：让 agent 原样复述，比对差异（大模型复述可能有出入，差异写进记录，不直接算 corral 的问题）。
每段送出的原文、回复、差异存在 $LAB_TMP/run/02-verbatim/。
"""
import difflib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lablib as L  # noqa: E402

BLOCK1 = ("? 问号开头的一行\n"
          "路径 /tmp/x/y，反引号 `code`，三个反引号 ```inline```\n"
          "中文、全角标点！emoji 🐑\n"
          "引号 \"双\" '单'，反斜杠 \\n 不是换行，$HOME 不展开，%s {}\n"
          "\t制表符开头的一行\n"
          "- 短横线开头的一行")
PROMPT1 = ("这是逐字送达测试。请把 <<<BEGIN 和 END>>> 之间的内容原样输出，前后不加任何文字，不要放进代码块。\n"
           "<<<BEGIN\n" + BLOCK1 + "\nEND>>>")
BLOCK2 = "```python\ndef double(x):\n    return x * 2  # 注释\n```\n第二段最后一行"
SEND2 = "第二段，规则同上：只原样输出 <<<BEGIN 和 END>>> 之间的内容。\n<<<BEGIN\n" + BLOCK2 + "\nEND>>>"
SEND3 = "?这一行以问号开头。请只回复：收到问号"


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def one(kind, fake, checks, out_dir):
    name = f"lab/verb-{kind}"
    code, out = L.corral("start", name, "--cwd", L.LAB, "--prompt", PROMPT1, "--", *L.agent_cmd(kind), timeout=90)
    if not checks.ok(f"{kind}：带多行特殊字符的首句 start", code == 0, out.get("error", "")):
        return
    try:
        rounds = [("1-首句", PROMPT1, BLOCK1, None), ("2-send代码块", SEND2, BLOCK2, SEND2),
                  ("3-send问号开头", SEND3, "收到问号", SEND3)]
        for label, sent, expect, send_text in rounds:
            if send_text is not None:
                code, out = L.corral("send", name, send_text, timeout=60)
                checks.ok(f"{kind}：{label} 送达确认", code == 0 and out.get("confirmed"),
                          f"退出码 {code} latency={out.get('latency')} {out.get('error', '')}")
            wcode, w = L.wait_done(name, total=300)
            checks.ok(f"{kind}：{label} 这一轮结束", wcode == 0 and w.get("result") == "idle",
                      f"result={w.get('result')} last_input_source={w.get('last_input_source')}")
            rcode, r = L.corral("reply", name)
            text = r.get("text", "") if rcode == 0 else ""
            base = os.path.join(out_dir, f"{kind}-{label}")
            write(base + ".sent.txt", sent)
            write(base + ".reply.txt", text)
            if fake:
                checks.ok(f"{kind}：{label} 回复逐字节等于 echo: 原文", text == "echo: " + sent)
                continue
            if label.startswith("3"):
                checks.note(f"{kind}：{label} 回复（人看：应含「收到问号」）", text[:80])
                continue
            diff = "".join(difflib.unified_diff(expect.strip().splitlines(True), text.strip().splitlines(True),
                                                "送出的内容", "agent 复述")) if text.strip() != expect.strip() else ""
            write(base + ".diff.txt", diff)
            checks.note(f"{kind}：{label} 复述（人看）", "逐字一致" if not diff else f"有差异，见 {base}.diff.txt")
    finally:
        code, out = L.corral("stop", name, "--timeout", "40")
        checks.ok(f"{kind}：stop", code == 0, f"stopped_by={out.get('stopped_by')}")


def main():
    args = sys.argv[1:]
    fake = "--fake" in args
    kinds = [a for a in args if a in ("claude", "codex")] or ["claude", "codex"]
    out_dir = os.path.join(L.RUN, "02-verbatim")
    os.makedirs(out_dir, exist_ok=True)
    checks = L.Checks("02 送话逐字送达")
    for kind in kinds:
        one(kind, fake, checks, out_dir)
    print(f"  文件：{out_dir}")
    return checks.done()


if __name__ == "__main__":
    sys.exit(main())
