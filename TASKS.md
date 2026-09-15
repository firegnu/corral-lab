# 开发任务

给被委派的 agent 做的真实小任务。约定：只用标准库；测试用 `python3 -m unittest`；每个任务（或任务里的每一步）单独提交。

1. **修 bug**：CSV 里有空行或只有空白的行时，`parse_file` 会崩溃。要求跳过这些行，并补测试。
2. **按月汇总**：新增 `python3 -m ledger month <文件> <YYYY-MM>`，输出该月各账户合计。分两步：
   - 第一步只补测试（新测试先失败），不改实现；
   - 第二步改实现，让测试全部通过。
3. **金额改用 Decimal**：parse、balance、report 全链路不再用 float，报表里不再出现 `-0.00`、`0.30000000000000004` 这类问题，补测试。
4. **按账户前缀过滤**：`report` 支持 `--account-prefix <前缀>`，只统计以该前缀开头的账户（例如 `food:`）。
5. **最大几笔**：新增 `python3 -m ledger top <文件> <N>`，列出金额绝对值最大的 N 笔交易。

## 第二个项目专用

- **B1 导出**：新增 `python3 -m ledger export <文件> --format csv`，把各账户余额导出为 CSV（表头 `account,amount`）。
