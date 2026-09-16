#!/usr/bin/env python3
"""步骤 12 B 段的回归检查（ISSUES 第 2 条，corral 48fb26a）：输入框里留着没提交的草稿时送话。

修复前：送出的话接在草稿后面一起提交，agent 收到了并照做，但 corral 因回读的文字对不上
报 not_delivered（退出码 3），调用方一重试就送第二遍。
修复后：识别出「送出的文字是这条输入的一部分」，判为送达，退 0 并标 merged_with_draft: true。

自己起一个一次性 agent，不打扰 lab-a/dev。草稿用 corral keys 种进去——keys 不算人在打字
（见 ISSUES 第 4 条坑二），所以不会撞上退出码 8。
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lablib as L  # noqa: E402

NAME = "lab/draft"
DRAFT = "这是没提交的草稿"
TEXT = "只回复两个字：收到"


def main():
    checks = L.Checks("12 B 段：输入框有草稿时送话")
    try:
        code, out = L.corral("start", NAME, "--cwd", L.LAB, "--", *L.agent_cmd("claude"), timeout=90)
        if not checks.ok("start", code == 0, out.get("error", "")):
            return checks.done()
        code, w = L.corral("wait", NAME, "--timeout", "120")
        if not checks.ok("起来了", code == 0 and w.get("result") == "idle", f"result={w.get('result')}"):
            return checks.done()

        L.corral("keys", NAME, f"text:{DRAFT}")
        code, st = L.corral("status", NAME)
        checks.ok("种草稿不算人在打字", st.get("last_human_input") is None,
                  f"last_human_input={st.get('last_human_input')} attached={st.get('attached')}")

        code, out = L.corral("send", NAME, TEXT, timeout=120)
        checks.ok("送话判为送达（不是退出码 3）", code == 0, f"退出码 {code} {out.get('error', '')}")
        checks.ok("标出和草稿拼在一起了", out.get("merged_with_draft") is True,
                  f"merged_with_draft={out.get('merged_with_draft')}")

        L.wait_done(NAME, total=120)
        code, r = L.corral("reply", NAME)
        # 有回答就说明拼接后的内容确实被 agent 收到并处理了
        checks.ok("agent 确实收到并回答了", code == 0 and bool(r.get("text")),
                  (r.get("text") or "（空）")[:60].replace("\n", " "))
    finally:
        if L.corral("status", NAME)[0] == 0:
            L.corral("stop", NAME, "--timeout", "120")
    return checks.done()


if __name__ == "__main__":
    sys.exit(main())
