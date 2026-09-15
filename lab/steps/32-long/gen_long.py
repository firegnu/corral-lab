#!/usr/bin/env python3
"""生成约 60KB 的背景材料 long-context.md，最后一行放暗号；暗号另存 long-token.txt 供检查。"""
import os
import secrets
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import lablib as L  # noqa: E402

ACCOUNTS = ("cash", "bank", "rent", "salary", "food:groceries", "food:dining", "travel", "utilities")


def main():
    run = L.run_dir("lab-a")
    os.makedirs(run, exist_ok=True)
    token = "TAIL-" + secrets.token_hex(4).upper()
    lines = ["# 背景材料：历史记账说明（生成的长文件）", ""]
    i = 0
    while sum(len(line.encode()) + 1 for line in lines) < 60000:
        i += 1
        acct = ACCOUNTS[i % len(ACCOUNTS)]
        lines.append(f"- 第 {i} 条：2025-{i % 12 + 1:02d}-{i % 28 + 1:02d} 账户 {acct} 调整 {i * 7 % 1000}.{i % 100:02d} 元，"
                     f"原因是第 {i % 17} 号规则；这条说明只是填充材料，评审时不需要逐条回应。")
    lines += ["", f"长文件暗号：{token}"]
    path = os.path.join(run, "long-context.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(run, "long-token.txt"), "w") as f:
        f.write(token)
    print(f"已生成 {path}（{os.path.getsize(path)} 字节，{len(lines)} 行），暗号 {token}")


if __name__ == "__main__":
    main()
