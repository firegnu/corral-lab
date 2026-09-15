# corral-lab

corral 的手工测试仓库：按一个小项目的开发过程，逐条测试 corral 在多 agent 协作里的通用使用模式。只在本地，不建远端。

- **CHECKLIST.md**：测试清单和测试记录，从上往下做。
- **TASKS.md**、`ledger/`、`tests/`：给被委派的 agent 做的小代码库（记账小工具，只用标准库，`python3 -m unittest`）。
- `lab/`：测试用的脚本。

## 目录

```
lab/lab.env          真 agent 的启动命令（便宜模型）
lab/lablib.py        脚本共用：调 corral、按契约送话、交付判定
lab/bin/             扮演「调用方」的脚本
  handoff              把 request.md 交给评审方，并拉起后台 watch-deliver
  watch-deliver        等评审方这一轮结束，判断有没有交付，再叫醒请求方
  wake                 叫醒脚本：比对实例编号，idle 才送，忙或有人操作时重试
  board                看板：所有 agent 的状态和正在做什么
  fanout               并发开几个临时 agent，检查回复不串
  roundcheck           检查某个前缀最近一轮交接
  need / strays / unwatch / snapshot   准备和检查用的小工具
  confhash / traces    全局配置指纹、lab 之外的痕迹
lab/requests/        交接请求模板
lab/steps/<编号>/    每个步骤的 prepare.sh、clean.sh，以及 run.py / check.sh
lab/selfcheck/       假 agent 自检（不启动真实 agent）
lab/cleanup.py       全部清理
```

## 用法

```sh
cd ~/Developer/personal_projs/corral-lab
lab/selfcheck/run.py          # 先自检：用假 agent 把脚本跑一遍（约 4 分钟，隔离在 /tmp/clab-self）
# 然后按 CHECKLIST.md 从 00 做到 99
lab/cleanup.py                # 最后清理
```

## 规矩

- 不改任何全局配置文件；只允许真 agent 在新目录点「信任」时由 agent 自己写入信任记录，清理时列出来手动删。
- 只操作名字以 `lab/`、`lab-a/`、`lab-b/` 开头，或工作目录在本仓库、`/tmp/clab` 下的 agent。
- 标了「白盒」的脚本会读或改 corral 的内部文件，只是测试手段；真正的调用方只用 corral 命令和 JSON 输出。
- 权限框里选「Yes」（只允许这一次），不选「不再询问」；不要在 agent 里打开 `/model` 这类会保存设置的菜单。
- 改了 `lab/` 下的脚本要先提交再自检：worktree 从 main 的已提交内容建。
