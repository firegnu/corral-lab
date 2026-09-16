# corral 手工测试清单

按一个小项目（`ledger`，任务见 TASKS.md）的开发过程，从上往下测 corral 在多 agent 协作里的通用使用模式。测试记录直接填在每一步末尾的「记录」里。

## 怎么用

- **顺序**：按编号往下做，前面的步骤是后面的基础（每步的「依赖」写明）。
- **目录**：所有命令都在 corral-lab 目录下运行：`cd ~/Developer/personal_projs/corral-lab`。
- **每一步怎么做**：
  1. 运行 `prepare.sh`：它检查前提、准备文件，并打印这一步要用的命令。
  2. 按「操作步骤」做。
  3. 对照「期望看到什么」和「通过标准」判断结果。
  4. 把结果填进「记录」。
  5. 需要时运行 `clean.sh`：大多数步骤的 agent 要留给后面用，只有单独重跑时才清。
- **标记**：
  - 【自动】脚本自己判 PASS / FAIL。
  - 【人看】需要人眼判断。
  - 【白盒】脚本读或改了 corral 的内部文件，只是测试手段。
  - 【权限框】这一步会弹权限框。
  - 【故障演练】故意制造的故障。
- **开始前**：先跑一遍自检 `lab/selfcheck/run.py`，确认脚本本身没问题（结果见 `lab/selfcheck/RESULT.md`）。

## 约定

- **名字**：
  - `lab/…`：一次性的 agent。
  - `lab-a/…`：第一个项目，工作 agent 是 `lab-a/dev`，评审方是 `lab-a/review`。
  - `lab-b/…`：第二个项目。
- **目录**：
  - 工作 agent 的工作目录是本仓库。
  - 评审方的工作目录是 worktree：`/tmp/clab/wt-lab-a-review`、`/tmp/clab/wt-lab-b`、`/tmp/clab/wt-lab-b-review`。
  - 交接目录是 `/tmp/clab/run/<前缀>/`。
- **模型**：启动命令见 `lab/lab.env`。
  - 工作 agent：Claude Code sonnet（M8 里 haiku 不会自己选用 skill）。
  - 评审方、被委派的 agent：Claude Code haiku、Codex gpt-5.6-luna（low）。
- **全局配置**：
  - 00 记下指纹。每个阶段结束运行一次 `lab/bin/confhash check`。
  - 只允许多出 Codex 的信任记录（01 里人点「信任」产生的），最后手动删。
- **注意**：
  - 权限框里选「Yes」（只允许这一次），不选「不再询问」。
  - 不要在 agent 里打开 `/model` 这类会保存设置的菜单。
  - skill 起的临时 agent 由 agent 自己起名，用 `lab/bin/strays` 查看。
- **已知限制**：`corral send` 没有「只送给某个实例」的参数，脚本只能先 `status` 比对实例编号再 `send`，两步之间有极小的竞态窗口。

## 窗口布局建议

| 窗口 | 用途 |
|---|---|
| 1 | 看板 `lab/bin/board` |
| 2 | `lab-a/dev` 的接入窗口（`corral attach --wait lab-a/dev`） |
| 3 | 敲命令 |
| 4 | 评审方的接入窗口（`corral attach --wait lab-a/review` 等） |
| 5 | `tail -f /tmp/clab/run/lab-a/watch.log` |
| 6、7 | 第二个项目（步骤 50） |

## 总览

| 编号 | 场景 | 覆盖 | agent | 时长 | 人在场 | 依赖 |
|---|---|---|---|---|---|---|
| 00 | 环境基线 | — | 无 | 5′ | 跑脚本 | 自检 |
| 01 | 工作目录与信任预热 | — | 真，不送话 | 10′ | 在场 | 00 |
| 02 | 送话逐字送达 | h | 真 | 10′ | 人看 | 01 |
| 03 | 生命周期与故障【故障演练】 | g | 真 | 8′ | 跑脚本 | 01 |
| 04 | 沙箱里被拒【故障演练】 | g | 无会话 | 3′ | 跑脚本 | 00 |
| 10 | 开工：常驻工作 agent + 观察窗口 | b e | 真 | 15′ | 人看 | 01 |
| 11 | 叫醒脚本 | b | 真 | 5′ | 在场 | 10 |
| 12 | 人正在打字时送话被拒 | b | 真 | 10′ | 在场 | 10 |
| 13 | 实例编号变了不送 | b | 真，不送话 | 3′ | 跑脚本 | 01 |
| 20 | 临时委派 Claude Code → Codex | a | 真 | 10′ | 人看 | 10 |
| 21 | 追问一轮 | a | 真 | 5′ | 人看 | 10 |
| 22 | 同时开三个临时 agent | a | 真 | 10′ | 部分自动 | 10 |
| 23 | 临时委派 Codex → Claude Code | a e | 真 | 10′ | 人看 | 01 |
| 30 | 交给另一个 agent 评审：第一轮 | c e | 真 | 15′ | 在场 | 10 |
| 31 | 第二轮复用同一个评审方 | c e | 真 | 15′ | 在场 | 30 |
| 32 | 长内容走文件 | h c e | 真 | 10′ | 在场 | 31 |
| 40 | 评审方弹权限框【权限框】 | d | 真 | 10′ | 亲手点 | 30 |
| 41 | 评审方停下但没交付 | d | 真 | 8′ | 在场 | 32 |
| 42 | 人按 Esc 打断评审方 | d | 真 | 10′ | 亲手按 | 41 |
| 43 | 评审方正忙时交下一轮 | d | 真 | 8′ | 在场 | 42 |
| 44 | 评审方卡在信任框【故障演练】 | d | 真 | 5′ | 在场 | 30 |
| 50 | 第二个项目并行 | f e | 真，4 个 | 25′ | 人看 | 01 10 30 |
| 60 | 协议兼容【故障演练】【白盒】 | g | 真 | 8′ | 中途接入一次 | 01 |
| 61 | 事件文件长期增长【故障演练】【白盒】 | g | 真 | 5′ | 跑脚本 | 01 |
| 70 | 退出整个终端软件 | g | 真 | 10′ | 在场 | 30 |
| 71 | 过夜【暂缓】 | g | 真 | 跨夜 | 早晚各 10′ | 70 |
| 99 | 清理与核对 | — | — | 5′ | 在场 | — |

覆盖：a 临时委派；b 长期驻留的工作 agent；c 文件交接的请求 / 交付循环；d 异常路径；e 观察；f 多项目并存；g 生命周期与故障；h 内容。

2026-09-16 决定：71（过夜）暂缓——要真过一夜。70（退终端软件）当天补跑通过。
同日 99 清理之后又重建最小环境补跑了 44、60、61（这三条能全自动，人工「看一眼」的地方用 `corral read` 读屏代替），全部通过。

---

# 阶段 0：准备

## 00 环境基线

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 无 agent（只查版本） | 5 分钟 | 跑脚本 | 自检通过 |

- **目的**：确认 corral、两家 agent、全局 skill、测试仓库都就绪；记下全局配置指纹，最后核对。
- **准备**：无。
- **操作步骤**：
  1. `lab/steps/00-baseline/prepare.sh`
- **期望看到什么**【自动】：每行 PASS；最后「已记下基线」和 5 个文件的指纹。
- **要记录什么**：corral 提交号；Claude Code、Codex 版本；两个 skill 文件的状态。
- **通过标准**：全部 PASS（没有 `lab-baseline` 标签、工作区不干净只是警告）。
- **清理**：无。基线要重记：`lab/bin/confhash save --force`。

**记录**
- 日期：2026-09-16
- corral 提交：7eca959
- Claude Code 版本：2.1.273　　　Codex 版本：0.154.0
- 结果：☑ 通过　☐ 不通过
- 备注：全部 PASS。基线指纹记在 /tmp/clab/confhash.json：settings.json 98348bb0bbe0、config.toml 90cf47c6f6a0、hooks.json 5deaab7cb308、两处 SKILL.md 均 bdefc57587fe。（M8 时 Claude Code 是 2.1.272，现在 2.1.273）

## 01 工作目录与信任预热

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent，不送话、不花额度（6 个探针） | 10 分钟 | 在场 | 00 |

- **目的**：
  - 建好后面要用的交接目录和 3 个 worktree。
  - 在之后要用的每个「目录 × agent」组合上先把信任框处理掉，后面的场景不会意外卡在启动。
  - 记下哪些目录弹了框、新增了哪些信任记录。
- **准备**：`lab/steps/01-workdirs/prepare.sh`（建 `/tmp/clab/run/lab-a`、`lab-b` 和 3 个 worktree，分支 `lab/wt-*`）。
- **操作步骤**：
  1. `lab/steps/01-workdirs/probe.py start`：起 6 个探针，5 秒后列出状态和每个探针的用途。
  2. 对状态是 `starting` 的 Claude 探针和**所有** Codex 探针，逐个 `corral attach <名字>`：
     - 看有没有信任框，有就选「信任」；
     - 按 Ctrl-] 退出接入。
  3. `lab/steps/01-workdirs/probe.py status`：再看一次。
  4. `lab/bin/confhash check`
  5. `lab/steps/01-workdirs/clean.sh`：停掉探针，worktree 留着。
- **期望看到什么**：
  - Claude Code 在 git worktree 里可能弹信任框，Codex 在没信任过的目录弹信任框；点了信任后，Claude 探针变成 `idle`。
  - Codex 探针接入后看到输入框。Codex 在第一次提交之前一直是 `starting`，这是正常的。
  - `confhash check` 显示 `~/.codex/config.toml`「只多了信任记录」，其他文件未变。
- **要记录什么**：每个探针有没有弹框、选了什么、之后的状态；`confhash` 列出的新增信任目录。
- **通过标准**：
  - 处理完后 Claude 探针都是 `idle`，Codex 探针接入后是输入框；
  - 全局配置除信任记录外未变；
  - `clean.sh` 后 `corral ls` 里没有探针。
- **清理**：`clean.sh`（已在步骤里）。

**记录**

| 探针 | 目录 | 弹框？ | 选了什么 | 之后状态 |
|---|---|---|---|---|
| lab/probe-cc-main | 仓库 | 是 | 信任 | idle |
| lab/probe-cx-main | 仓库 | 是 | continue | starting（正常）|
| lab/probe-cc-a-review | wt-lab-a-review | 是 | 信任 | idle |
| lab/probe-cx-a-review | wt-lab-a-review | 是 | continue | starting（正常）|
| lab/probe-cc-b | wt-lab-b | 是 | 信任 | idle |
| lab/probe-cx-b-review | wt-lab-b-review | 是 | continue | starting（正常）|

- 新增信任记录：只有 Codex 的 `[projects."/Users/firegnu/Developer/personal_projs/corral-lab"]`（trust_level = "trusted"）。三个 worktree 没有各自的记录。
- 结果：☑ 通过　☐ 不通过
- 备注：
  - Codex 的信任按主仓库根目录算：停掉 wt-lab-a-review 的 Codex 探针再重开，不再弹框。后面在 worktree 里起 Codex 不会卡在信任框。
  - 在 lab/probe-cx-main 里误输入了 `/exit`，agent 自己退出；`corral status` 报退出码 2，`exited` 是 `{"code": 0, "stop_step": null}`，符合设计。重开后不再弹信任框，说明「continue」已经把信任记下了。
  - `confhash check` 一开始报「变了」而不是「只多了信任记录」：是 lab/bin/confhash 去掉信任段时多删了一个空行（已修）。修后报「只多了信任记录」，退出码 0。
  - 6 个探针 clean.sh 全部 stop 成功（Claude 走 SIGHUP，Codex 走 keys），`corral ls` 为空。

## 02 送话逐字送达

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（Claude haiku、Codex luna，各三小轮） | 10 分钟 | 人看差异 | 01 |

- **目的**：多行、代码块、问号开头、反引号、中文、引号、制表符、`$HOME` 这类内容，经 `start --prompt` 和 `send` 都逐字送到，回复原样取回。
- **准备**：`lab/steps/02-verbatim/prepare.sh`
- **操作步骤**：
  1. `lab/steps/02-verbatim/run.py`（只测一家：`run.py claude` 或 `run.py codex`）。
  2. 打开 `/tmp/clab/run/02-verbatim/` 下的 `*.diff.txt` 看差异。
- **期望看到什么**：
  - 【自动】每段都确认送达（`confirmed: true`），每轮都 `idle`，最后 stop 成功。
  - 【人看】复述差异：最好没有；有差异时，判断是 agent 复述有出入（例如自己加了代码块、吃掉行首制表符），还是送进去就错了。`confirmed: true` 已说明 agent 收到的原文和送出的一致。
- **要记录什么**：每家三段的送达确认和 `latency`；复述差异概述；问号开头那一行的回复。
- **通过标准**：全部 PASS；复述差异只来自 agent 复述，不来自送达。
- **清理**：`run.py` 自己 stop；中途打断时 `clean.sh`。

**记录**
- Claude Code（haiku）：首句 ☑ 送达　代码块 ☑ 送达（latency 0.404）　问号开头 ☑ 送达；复述差异：无，diff 文件 0 字节
- Codex（luna low）：首句 ☑ 送达　代码块 ☑ 送达（latency 0.512）　问号开头 ☑ 送达；复述差异：无，diff 文件 0 字节
- 结果：☑ 通过　☐ 不通过
- 备注：
  - 三轮的 `last_input_source` 都是 `send`；问号开头那一行两家都回「收到问号」，没有被界面当成快捷键。
  - 观察：Codex 这次 `stop` 落到 SIGTERM（`exit_code: -15`），不是 M8 的正常退出（`keys`，7.6 秒收尾）。01 里没提交过话的 Codex 探针 stop 走的是 `keys`。跑过几轮之后是不是就退不动，见 03。

## 03 生命周期与故障【故障演练】

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（Codex 一句话，Claude 不送话） | 8 分钟 | 跑脚本 | 01 |

- **目的**：
  - 同名重复 start 被拒（退出码 5）。
  - stop 后立刻同名 start 不撞锁。
  - 栏位被 kill -9 后，`ls` 清掉残留、能重新 start。
  - agent 被 kill -9 后，`status` 带退出信息。
- **准备**：`lab/steps/03-lifecycle/prepare.sh`
- **操作步骤**：`lab/steps/03-lifecycle/run.py`
- **期望看到什么**【自动】：
  - 全部 PASS。
  - **回归检查（ISSUES 第 3 条）**：Codex 会先跑三轮再 stop，必须是 `stopped_by=keys`、`exit_code=0`、用时 60 秒以内——旧的 20 秒上限会把收尾截断成 SIGTERM（`exit_code: -15`）。corral `48fb26a` 放宽到 60 秒。
  - Codex stop 以 `keys` 结束、退出码 0，用时 10 秒左右。
  - 「记录」行写明栏位被杀后 agent 进程有没有残留。
- **要记录什么**：Codex stop 用时和 `stopped_by`；栏位被杀后 agent 是否成了孤儿进程；Claude 被杀后的 `exited`。
- **通过标准**：全部 PASS。孤儿进程只记录，不算不通过；脚本会结束掉它。
- **清理**：`run.py` 自己清；中途打断时 `clean.sh`。【白盒】从 meta.json 取栏位进程号。

**记录**
- Codex stop：用时 13.1s　　　stopped_by=keys　　　exit_code=0
- 栏位被杀后 agent：☑ 也退出了　☐ 残留
- Claude 被杀后 exited：`{"instance": "219de3eeb694", "code": -9, "stop_step": null}`
- 结果：☑ 通过　☐ 不通过
- 备注：
  - 同名重复 start 得到 5；stop 后立刻同名 start 不撞锁；kill -9 栏位后 `ls` 清残留、能重新 start；两次 Codex stop 都是 `keys` 正常退出。
  - Claude stop `stopped_by=SIGHUP`、`exit_code=-1`，符合设计。
  - Codex 收尾 13.1 秒，比 M8 实测的 7.6 秒长；02 那次更是超过 20 秒落到 SIGTERM。corral 等 20 秒升级信号，余量偏紧，见「发现的问题」。
  - **2026-09-16 补跑（corral `48fb26a` 把等待放宽到 60 秒之后）**：这一步的 Codex 改成先跑三轮再 stop，实测 **25.6 秒、`stopped_by=keys`、`exit_code=0`**——正常收尾，不再被截断。16 项全 PASS。上面那条 13.1 秒是「只跑过一句」的会话，两者对得上：收尾时间随会话内容增长。

## 04 沙箱里被拒【故障演练】

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 无 agent 会话（`codex sandbox` 只跑命令，不调模型） | 3 分钟 | 跑脚本 | 00 |

- **目的**：所有命令在 Codex 沙箱里以退出码 6 拒绝，`guide` 和 `--version` 照常可用；真沙箱里也一样。
- **准备**：`lab/steps/04-sandbox/prepare.sh`
- **操作步骤**：`lab/steps/04-sandbox/run.py`
- **期望看到什么**【自动】：12 个命令都得到 6，guide、`--version` 得到 0；真沙箱里 `corral ls` 得到 6，并说明原因。
- **要记录什么**：真沙箱里输出的 `message`。
- **通过标准**：全部 PASS。
- **说明**：不以沙箱模式启动真 Codex（试验 Codex 一律 `--yolo`），所以 skill 遇到退出码 6 时怎么跟用户说，这里不测。
- **清理**：无。

**记录**
- 真沙箱 message：`running inside a Codex sandbox: agents started here would be sandboxed too, and running agents cannot be reached; start the caller without the sandbox (e.g. codex --yolo)`
- 结果：☑ 通过　☐ 不通过
- 备注：12 个命令都得到退出码 6，`guide` 和 `--version` 得到 0；`codex sandbox -P :workspace` 里 `corral ls` 也得到 6。

---

# 阶段 1：开工

## 10 开工：常驻工作 agent + 观察窗口

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（`lab-a/dev`：Claude sonnet，之后一直用） | 15 分钟 | 人看 | 01 |

- **目的**：
  - 人用 `corral start` 开一个工作 agent，接入进去干活。
  - 预先挂着的 `attach --wait` 在它启动时自动接上。
  - 看板能显示状态和正在做什么。
  - 多个窗口接同一个 agent 时只有一个能打字。
- **准备**：`lab/steps/10-resident/prepare.sh`（打印 3 个窗口的命令）。
- **操作步骤**：
  1. 窗口 1 运行 `lab/bin/board`；窗口 2 运行 `corral attach --wait lab-a/dev`，显示 `waiting for lab-a/dev`。
  2. 窗口 3 运行 prepare 打印的 `corral start lab-a/dev …`。
  3. 看窗口 2 自动接上，看板出现 `lab-a/dev`。
  4. 在窗口 2 里说：「读 TASKS.md，做任务 1。改完跑测试，全部通过后提交。」
  5. 做的过程中看看板，结束后再看一次。
  6. 另开窗口 8 运行 `corral attach lab-a/dev`：
     - 在窗口 8 里打字，应没有反应；
     - 改变窗口 2 的大小，agent 界面跟着重排；
     - 改变窗口 8 的大小，不影响 agent；
     - 窗口 8 按 Ctrl-] 退出。
- **期望看到什么**【人看】：
  - 窗口 2 在 start 后几秒内自动接上。
  - 看板：干活时是 `working`，「正在做」显示工具名和这一轮已跑的时长；结束后是 `idle`，最近输入是 `human`，接入数是 1（窗口 8 开着时是 2）。
  - 任务 1 完成：`git log` 有新提交，测试通过。
- **要记录什么**：从 start 到窗口 2 接上用了多久；看板上看到的状态变化；任务 1 的提交号；多窗口的表现。
- **通过标准**：
  - 自动接上；
  - 看板状态和实际一致；
  - 只读窗口打不了字；
  - 尺寸跟着能打字的窗口走；
  - Ctrl-] 退出后 agent 照常在跑。
- **清理**：不清理（后面一直用）；单独重跑时 `clean.sh`。

**记录**
- 自动接上用时：几秒内，窗口 2 从 waiting 直接进 Claude Code 界面，没有信任框（01 已信任）
- 看板状态变化：idle → working（last_tool=Bash，显示这一轮时长）→ idle；最近输入 `human`；标题变成「✳ TASKS.md 任务 1」
- 任务 1 提交：`e5c07a9 fix: parse_file 跳过 CSV 中的空行/空白行`（parse.py 跳过空行和只有空白的行，test_parse.py 补测试）
- 只读窗口 ☑ 打不了字　尺寸 ☑ 跟随能打字的窗口
- 结果：☑ 通过　☐ 不通过
- 备注：中途往窗口 2 的输入框里误粘了一段聊天文字，没有提交（事件里只有任务那一条输入，来源 human），清掉后继续。

## 11 叫醒脚本

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（接 10） | 5 分钟 | 在场 | 10 |

- **目的**：脚本在工作 agent idle 时给它送「去做 X」。工作 agent 正忙时，脚本先得到退出码 7，等这一轮结束再送。
- **准备**：`lab/steps/11-wake/prepare.sh`（打印两条 wake 命令）。
- **操作步骤**：
  1. 窗口 3 运行第一条 wake（任务 2 第一步）。
  2. 看 dev 开始干活后，马上运行第二条 wake（任务 2 第二步）。
- **期望看到什么**：
  - 第一条：`armed … instance=…` → `delivered`。
  - 第二条：`armed` → `not_idle state=working` → dev 做完第一步后 → `delivered`。
  - 窗口 2 里能看到送进去的话；看板最近输入是 `send`。
  - `git log` 里任务 2 两步各一个提交。
- **要记录什么**：两条的实例编号和 `latency`；第二条从 `not_idle` 到 `delivered` 用了多久。
- **通过标准**：两条都 delivered；第二条先 `not_idle`；dev 按顺序完成两步。
- **清理**：无。

**记录**
- 第一条：delivered ☑　latency 0.406（09:35:23 armed → 同秒 delivered）
- 第二条：not_idle ☑ → delivered ☑　等了约 79 秒（09:35:29 not_idle state=working → 09:36:48 delivered，latency 0.405）
- 结果：☑ 通过　☐ 不通过
- 备注：任务 2 两步各一个提交（`986dd36` 先补失败测试、`505e4cc` 再实现），16 个测试全过；看板最近输入是 `send`。

## 12 人正在打字时送话被拒

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（接 10） | 10 分钟 | 在场 | 10 |

- **目的**：人在接入窗口里按过键后 30 秒内，脚本送话被拒（退出码 8），之后自动送达；只移动鼠标不算按键。另外记录「输入框里留着草稿时送话」的实际表现。
- **准备**：`lab/steps/12-typing/prepare.sh`
- **操作步骤**：
  1. **A**：在窗口 2 里敲 `abc`，按 3 次退格删掉，不回车。10 秒内在窗口 3 运行 prepare 打印的 wake。之后不要碰窗口 2：鼠标可以划过，但不要点击或滚动。
  2. **B（只记录）**：在窗口 2 里敲「草稿」两个字，留着不删，等 35 秒后运行 `lab/bin/wake lab-a/dev "只回复：收到"`。看完结果后手动清掉输入框里剩下的字。
- **期望看到什么**：
  - A：
    - wake 输出 `human_active`，带 `last_human_input`；
    - 每 5 秒重试一次，不重复打印；
    - 最后一次按键约 30 秒后 `delivered`；
    - 鼠标划过窗口不会推迟送达。
  - B：**已经不是记录项了**。corral `48fb26a` 修了这个缺口：识别出「送出的文字是这条输入的一部分」，判为送达，退 0 并标 `merged_with_draft: true`，不再让调用方重送。
    现在跑 `lab/steps/12-typing/draftcheck.py` 自动验（它自己起一次性 agent，用 `corral keys` 种草稿，不打扰 `lab-a/dev`）。
- **要记录什么**：A 从按键到送达的秒数；B 的 `draftcheck.py` 结果。
- **通过标准**：A 满足期望【人看】；B 的 `draftcheck.py` 全部 PASS【自动】。
- **清理**：确认 dev 输入框里没有残留的字。

**记录**
- A：按键到送达 33 秒（最后一次按键 09:38:43 → 09:39:16 delivered）；鼠标划过是否推迟：没有（只划过不算人工操作）
- B：wake 输出 `not_delivered`（退出码 4）　　　dev 收到「草稿只回复：收到」并回答了「收到」　　　输入框：草稿被连同送出的话一起提交
- 结果：☑ 通过（A 段）　☐ 不通过；B 段是记录项
- 备注：
  - A 段：第一次尝试就被 `human_active` 拒绝，带最后一次按键时间；每 5 秒重试，重复的不刷屏。
  - B 段确认了设计缺口：人留着没提交的草稿时，send 的文字接在草稿后面一起提交，corral 因文字对不上报 `not_delivered`，但 agent 其实已经收到并执行了——调用方看到的是「假阴性」，若重试会送第二遍。见「发现的问题」。
  - **2026-09-16 已修**（corral `48fb26a`）：新增 `lab/steps/12-typing/draftcheck.py`，实测六项全 PASS——草稿种进去不算人在打字、送话退 0、`merged_with_draft=True`、agent 回了「收到」。同样的场景修复前是退出码 3。

## 13 实例编号变了不送

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（一次性 Claude Code，不送话） | 3 分钟 | 跑脚本 | 01 |

- **目的**：脚本记着的实例编号和现在的不一样（agent 被别人重启过），就不送，免得把话塞给一个毫不知情的新对话。
- **准备**：`lab/steps/13-instance/prepare.sh`
- **操作步骤**：
  1. `lab/steps/13-instance/run.py`
  2. 可选【人看】：
     - 起一个 `lab/w2`，接入并在里面按键；
     - 在另一个窗口运行 `lab/bin/wake lab/w2 "只回复：好"`，它会因为 `human_active` 反复重试；
     - 趁这时 `corral stop lab/w2` 再同名 start；
     - 应看到 wake 输出 `instance_changed` 并退出（退出码 3）。
- **期望看到什么**【自动】：实例编号变化；wake 退出码 3、输出 `instance_changed`；新实例的 `last_input_at` 为空。
- **要记录什么**：新旧实例编号；可选变体的结果。
- **通过标准**：全部 PASS。
- **清理**：`run.py` 自己 stop；中途打断时 `clean.sh`。

**记录**
- 实例编号：b0fdbed1d2ff　　→　c54c0057b931
- 可选变体：没做（自动那部分已经覆盖判断逻辑）
- 结果：☑ 通过　☐ 不通过
- 备注：wake 记下旧编号后立刻发现不一致，报 `instance_changed`、退出码 3；新实例 `last_input_at=None`，没送出任何话。

---

# 阶段 2：拿不准时临时委派

## 20 临时委派：Claude Code → Codex

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（外层 `lab-a/dev` sonnet；内层 Codex luna，由 skill 起） | 10 分钟 | 人看 | 10 |

- **目的**：人对工作 agent 说「开一个 Codex 看一下这个想法」。工作 agent 自动用全局 corral skill 走完下面几步，把回复原样转述：
  1. 自检 corral 在不在；
  2. `start --unique --prompt`；
  3. `wait --timeout 90 --quiet 120`，退出码 4 就再等；
  4. `reply`；
  5. `stop`。
- **准备**：`lab/steps/20-delegate-codex/prepare.sh`（要求 dev 是 idle，列出现有的临时 agent）。
- **操作步骤**：
  1. 在窗口 2 里说 prepare 打印的那句话。
  2. 看 dev 跑的命令；看板上临时 agent 出现又消失。
  3. 结束后 `lab/bin/strays`。
- **期望看到什么**【人看】：
  - dev 加载 corral skill；
  - 命令带 `--unique` 和 `--prompt`，agent 命令是 `codex --yolo -m gpt-5.6-luna …`；
  - wait 返回 `idle` 后 reply，最后 stop；
  - dev 汇报的内容和 reply 的 `text` 对得上；
  - `strays` 显示「没有」。
- **要记录什么**：临时名字；有没有传模型参数；wait 调了几次；总用时；有没有弹权限框；转述和原文是否一致。
- **通过标准**：几步齐全、最后 stop 了；dev 的汇报基于 reply 原文，不是自己作答或用内置子代理。
- **清理**：`clean.sh`（停掉没 stop 的临时 agent）。

**记录**
- 临时名字：`ask-task3-decimal-1`（dev 自己起的前缀 + `--unique` 后缀）　　　模型参数：☑ 传了（`--model gpt-5.6-luna -c model_reasoning_effort=low`）　☐ 没传
- wait 次数：1（约 50 秒返回 idle）　　总用时：约 1 分半　　权限框：没有
- 转述 ☑ 与原文一致
- 结果：☑ 通过　☐ 不通过
- 备注：
  - dev 自动加载 corral skill，依次做了 `command -v corral` → `start --unique --prompt` → `wait --timeout 90 --quiet 120` → `reply` → `stop`（`stopped_by=keys`，退出码 0）。
  - 看板上看到临时 agent 从 starting → working → idle，stop 后消失；`lab/bin/strays` 输出「没有」。
  - 观察：名字由调用方决定，dev 起的是单段名字 `ask-task3-decimal`，不带 `/` 也不是 lab 前缀。清理靠工作目录匹配能兜住，但上层要自己约定前缀。

## 21 追问一轮

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（接 10） | 5 分钟 | 人看 | 10 |

- **目的**：临时 agent 答完不关，追问一轮：send 给同一个名字，再 wait、reply，最后 stop。
- **准备**：`lab/steps/21-followup/prepare.sh`
- **操作步骤**：在窗口 2 里说 prepare 打印的第一句；dev 转述完后说第二句。
- **期望看到什么**【人看】：
  - 第一问后临时 agent 没有被 stop（看板上还在）；
  - 第二问用 `corral send <同一个名字>`，没有新的 start；
  - 看板上实例编号不变；
  - 问完 stop。
- **要记录什么**：名字和实例编号；第二问用的命令；两次回答的要点。
- **通过标准**：同名、同实例追问成功，最后 stop。
- **清理**：`clean.sh`

**记录**
- 名字 / 实例：`ask-parse-blank-1` / `ff9f1baf7e4f`（两问之间没变）
- 第二问命令：`corral send ask-parse-blank-1 "补充一个问题：…BOM…"` → `confirmed: true`，latency 0.51；没有新的 `corral start`
- 结果：☑ 通过　☐ 不通过
- 备注：第一问答完后临时 agent 保持 idle 没被 stop；追问后 `wait` → `reply` → `stop`，全程同一个实例。dev 窗口里显示的 stop 输出带 `kind`、`type: codex_session` 字段，但 corral 的 stop 只输出 `ok/name/instance/exit_code/stopped_by`，仓库里也搜不到 `codex_session`——那段是 Claude Code 折叠显示的，不是 corral 的输出。已在 22 确认：窗口 3 里 stop Codex 的原始输出只有契约的 5 个字段，那两行是 Claude Code 的显示。

## 22 同时开三个临时 agent

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（3 个 Codex luna，两种方式各一次） | 10 分钟 | A 人看、B 自动 | 10 |

- **目的**：同时开几个临时 agent，互不串。
- **准备**：`lab/steps/22-parallel/prepare.sh`
- **操作步骤**：
  1. A：在窗口 2 里说 prepare 打印的那句话。
  2. B：窗口 3 运行 `lab/bin/fanout 3 --kind codex`。
- **期望看到什么**：
  - A【人看】：看板上同时出现三个不同名字；汇总里每个文件的意见没有张冠李戴；三个都 stop 了。
  - B【自动】：三个名字互不相同，每份回复只含自己的暗号，全部 stop，全部 PASS。
- **要记录什么**：A 的三个名字、是否并发（看板上同时在 `working`）；B 的结果。
- **通过标准**：A 没有串、都 stop；B 全部 PASS。
- **清理**：`clean.sh`

**记录**
- A 名字：`review-parse-1`、`review-balance-1`、`review-report-1`　　　是否同时 working：是（三轮时间区间重叠：983 / 992 / 1004 结束）　　　意见是否串：没有，每份回复只讲自己那个文件，dev 的汇总也分得清
- B：☑ 全部通过（`lab/fan-1/2/3`，每份回复只含自己的暗号，三个都 stop）
- 结果：☑ 通过　☐ 不通过
- 备注：
  - A 段三个都 `stop` 成功（`keys`、退出码 0）；这次看到的原始 stop 输出就是契约里的 5 个字段，确认 21 里那个 `codex_session` 是 Claude Code 窗口的显示，不是 corral 的输出。
  - dev 是分三次 `start` 的（它自己也说应该并行发），但三个仍然并发在跑。

## 23 临时委派：Codex → Claude Code

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（外层 `lab-a/dev-cx` Codex luna；内层 Claude haiku） | 10 分钟 | 人看 | 01 |

- **目的**：反方向委派：Codex 从 `~/.agents/skills` 加载 corral skill，开 Claude Code 看问题。另外看 `attach --wait` 在 agent 退出后回到等待。
- **准备**：`lab/steps/23-delegate-claude/prepare.sh`（打印窗口 4 和启动命令）。
- **操作步骤**：
  1. 窗口 4 挂 `corral attach --wait lab-a/dev-cx`；窗口 3 start。
  2. 窗口 4 接上后说 prepare 打印的那句话。
  3. 结束后 `corral stop lab-a/dev-cx`，看窗口 4 回到 `waiting for lab-a/dev-cx`，然后在窗口 4 按 Ctrl-C 退出等待。
- **期望看到什么**【人看】：
  - Codex 用了 corral skill，agent 命令是 `claude --model haiku`（或类似写法）；
  - 几步齐全，转述和原文一致；
  - stop 后窗口 4 回到等待。
- **要记录什么**：同 20；stop 后窗口 4 的表现。
- **通过标准**：同 20；窗口 4 回到等待。
- **清理**：`clean.sh`

**记录**
- 临时名字：`ledger-report-format-1`　　　模型参数：haiku（按要求传了）　　　wait 次数：2（第二次立即返回 idle）　　　转述一致：是
- stop 后窗口 4 ☑ 回到等待（`waiting for lab-a/dev-cx ...`，Ctrl-C 退出）
- 结果：☑ 通过　☐ 不通过
- 备注：
  - 外层 Codex 从 `~/.agents/skills` 加载了 corral skill，走完自检 → `start --unique --prompt` → `wait` → `reply` → `stop`。
  - Codex 启动时提示「Skill descriptions were shortened to fit the skills context budget」：本机 skill 多，corral 的描述被截短，但仍然触发。
  - 内层 Claude 被 stop 时 `exit_code: 129`（自己处理 SIGHUP 后退出），03 里同样是 SIGHUP 但记的是 `-1`（直接被信号结束）。两种都正常。
  - 外层 Codex stop：`keys`、退出码 0。

---

# 阶段 3：交给另一个 agent 评审

## 30 第一轮交接

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（A = `lab-a/dev` sonnet；B = `lab-a/review` Codex luna，在 worktree） | 15 分钟 | 在场 | 10 |

- **目的**（文件交接的请求 / 交付循环）：
  1. A 把请求写进 request.md，运行 `lab/bin/handoff`；
  2. 脚本用固定名字 start B，B 的工作目录是同一仓库的 worktree；
  3. 后台脚本用 wait 等 B 结束并检查哨兵行 DONE；
  4. 然后 send 叫醒 A。

  观察：B 被 start 时，预先挂着的接入窗口自动出现。
- **准备**：`lab/steps/30-handoff/prepare.sh`（要求 dev 是 idle、B 不在、没有在跑的 watcher，打印要说的话）。
- **操作步骤**：
  1. 窗口 4 挂 `corral attach --wait lab-a/review`；窗口 5 `tail -f` watch.log。
  2. 在窗口 2 里说 prepare 打印的那句话。
  3. 等 dev 被叫醒并处理评审意见后，运行 `lab/steps/30-handoff/check.sh`。
- **期望看到什么**：
  - dev 写好 request.md，运行 handoff，输出 JSON（`b_action: started`），然后结束这一轮。
  - 窗口 4 自动接上 B。
  - watch.log 依次出现：`b_started` → `watching` → `delivered` → `wake_a_delivered`。
  - 看板：B `working` → `idle`；dev 被叫醒，最近输入是 `send`，读 findings.md 并处理。
- **要记录什么**：handoff 时间、B 交付时间、A 被叫醒时间；B 的实例编号；findings.md 第一行。
- **通过标准**【自动】：`check.sh` 全部 PASS（判定 delivered、和文件一致、叫醒了 dev、findings 含 LAB-A-TOKEN）。
- **清理**：不清理（31 要复用 B）；单独重跑时 `clean.sh`。

**记录**
- handoff：10:13:16　　B 交付：10:14:36（80 秒）　　A 被叫醒：10:14:36（latency 0.408）
- B 实例：`1e79e07881d6`　　　findings 第一行：`LAB-A-TOKEN`
- 窗口 4 ☑ 自动接上
- 结果：☑ 通过　☐ 不通过
- 备注：
  - watch.log 四步齐全：`b_started` → `watching` → `delivered`（最后一行是 DONE）→ `wake_a_delivered`；check.sh 全部 PASS。
  - dev 自己读了 `lab/bin/handoff` 和 lablib 确认约定，再写 request.md、运行 handoff，一轮就结束；`sent_bytes` 128。
  - dev 被叫醒后核对 token、补了两条回归测试并提交 `0f14d3f`，另有两条意见它判断超出任务范围、说明理由后没做。
  - 评审方为验证「测试先行」自己在 /tmp 下建了临时 worktree，结束时自己删干净了，`git worktree list` 没有残留。

## 31 第二轮复用同一个评审方

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（接 30） | 15 分钟 | 在场 | 30 |

- **目的**：同一个 B 跨多轮复用：第二轮能找到活着的 B，实例编号不变，上一轮结果被归档。结束后 stop B，看接入窗口回到等待。
- **准备**：`lab/steps/31-reuse/prepare.sh`（显示上一轮的轮次和 B 的实例编号）。
- **操作步骤**：
  1. 等 dev 处理完第一轮意见（idle），在窗口 2 里说 prepare 打印的那句话（任务 3 + 请评审）。
  2. 这一轮结束后运行 `lab/steps/31-reuse/check.sh`。
  3. `corral stop lab-a/review`，看窗口 4 回到 `waiting for lab-a/review`。
- **期望看到什么**：
  - handoff 输出 `b_action: reused`，`b_instance` 和 30 一样；
  - watch.log 有 `send_b_delivered`，没有新的 `b_started`；
  - 出现 `findings-1.md`；
  - stop 后窗口 4 回到等待。
- **要记录什么**：B 的实例编号（和 30 比）；归档文件名；窗口 4 的表现。
- **通过标准**【自动】：`check.sh` 全部 PASS；窗口 4 回到等待【人看】。
- **清理**：已在步骤里 stop B。

**记录**
- B 实例：30 的 `1e79e07881d6`　　　31 的 `1e79e07881d6`（一样，复用成功）
- 归档：`findings-1.md`（2.9k）　　　窗口 4 ☑ 回到等待
- 结果：☑ 通过　☐ 不通过
- 备注：
  - 第 2 轮走 `send_b_delivered`（不是新 start），交付用时 50 秒；check.sh 两段全部 PASS。
  - 意外收获：watcher 叫醒 dev 时正好赶上人在 dev 窗口里操作过，日志里出现 `wake_a_human_active`，5 秒后重试成功——退出码 8 的重试路径在真实流程里自然触发了一次。
  - dev 按第 2 轮意见改了代码并提交 `443467e`（任务 3 的 Decimal 改造在 `39b9d4f`），30 个测试通过。
  - `corral stop lab-a/review`：`keys`、退出码 0，窗口 4 回到 `waiting for lab-a/review`。

## 32 长内容走文件

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（接 31） | 10 分钟 | 在场 | 31 |

- **目的**：很长的内容（约 60KB）放进文件，send 里只写一句指路的话；B 读完整个文件。另外看 B 重新 start 时接入窗口再次自动接上。
- **准备**：`lab/steps/32-long/prepare.sh`（生成 `long-context.md`，最后一行放暗号）。
- **操作步骤**：
  1. 在窗口 2 里说 prepare 打印的那句话。
  2. 这一轮结束后运行 `lab/steps/32-long/check.sh`。
- **期望看到什么**：
  - B 是这一轮新 start 的（31 结束时 stop 过），窗口 4 自动再接上，实例编号是新的；
  - findings.md 含文件最后一行的暗号；
  - 送出的话不到 300 字节。
- **要记录什么**：新的 B 实例编号；findings 里暗号那一行。
- **通过标准**【自动】：`check.sh` 全部 PASS。
- **清理**：不清理（41 起复用 B）。

**记录**
- 新 B 实例：`5e1c1cde0eca`（第 1、2 轮是 `1e79e07881d6`）　　　暗号行：`TAIL-02EDA1E4`，和 long-context.md 最后一行一致
- 窗口 4 ☑ 自动再接上
- 结果：☑ 通过　☐ 不通过
- 备注：
  - 长文件 60,093 字节、388 行；`send` 只送 128 字节，评审方读完全文并在结果里写出末行暗号，还提到了正确行数。
  - 交付用时 58 秒；check.sh 两段全部 PASS。

---

# 阶段 4：过程中出岔子

## 40 评审方弹权限框【权限框】

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（B = `lab-a/review-cc`：Claude haiku，默认权限模式） | 10 分钟 | **亲手点** | 30 |

- **目的**：B 弹权限框时状态变 `blocked`，watcher 记下「等人处理」，不会误当成交付或没交付；人接入去点，流程继续到交付。
- **准备**：`lab/steps/40-permission/prepare.sh`（写入评审请求模板，打印命令）。
- **操作步骤**：
  1. 窗口 4 挂 `corral attach --wait lab-a/review-cc`。
  2. 窗口 3 运行 prepare 打印的 handoff 命令。
  3. 弹框后**先别点，看 30 秒**：看板、watch.log。
  4. 在窗口 4 里选「Yes」。可能连续弹好几次（读请求、写结果），每次都一样处理。
  5. 这一轮结束后运行 `lab/steps/40-permission/check.sh`。
- **期望看到什么**：
  - 弹框后 1–2 秒内 watch.log 出现 `blocked`，看板状态 `blocked`；
  - 30 秒内一直是 `blocked`，不会变成 `idle`；
  - 点了之后出现 `unblocked` → … → `delivered` → `wake_a_delivered`。
- **要记录什么**：弹框次数；每次 blocked 出现的延迟和持续时间（`check.sh` 会列出）；有没有误判。
- **通过标准**【自动 + 人看】：`check.sh` 全部 PASS（delivered、至少一次 blocked）；框开着期间没有误判。
- **清理**：`clean.sh`（stop `lab-a/review-cc`）。

**记录**
- 弹框次数：2（第一次跑 pytest 的 Bash，第二次写 findings.md 的 Write）　　　blocked 延迟 / 持续：送出后 177.8s 出现、持续 144.3s；送出后 340.7s 出现、持续 4.1s
- 有无误判：没有。框开着 144 秒期间状态一直是 `blocked`，没变 idle，也没被判成没交付
- 结果：☑ 通过　☐ 不通过
- 备注：
  - 时间线：b_started → watching → blocked → unblocked(working) → blocked → unblocked → delivered（最后一行是 DONE）→ wake_a_delivered。
  - 第一次跑这一步时用的 `claude --model haiku --add-dir /tmp/clab --permission-mode default` 没弹框就写完了：加了 `--add-dir` 等于把交接目录算进工作区，默认权限模式对工作区内的写入不询问。已把 `lab.env` 里的 `LAB_CLAUDE_ASK` 去掉 `--add-dir`，以后这一步必定弹框。
  - 本轮实际弹框来自 Bash（pytest）和 Write（findings.md），两种都验证到了。
  - dev 注意到 request.md 被「别人在磁盘上直接改了」（其实是 prepare.sh 覆盖的），它没还原、按现状处理——交接目录是共享的，上层要自己约定谁能写。
  - 评审方 stop：`SIGHUP`、`exit_code 129`。

## 41 评审方停下但没交付

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（B = `lab-a/review`，接 32） | 8 分钟 | 在场 | 32 |

- **目的**：B 这一轮结束了（idle），但 findings.md 没有 DONE。脚本要能分辨，不当成交付，并告诉 A「没交付」。
- **准备**：`lab/steps/41-nodone/prepare.sh`（写入「不要写任何文件」的请求）。
- **操作步骤**：
  1. 窗口 3 运行 prepare 打印的 handoff 命令。
  2. 这一轮结束后运行 `lab/steps/41-nodone/check.sh`。
- **期望看到什么**：
  - 多半是 `undelivered`（原因「findings.md 不存在」），dev 收到「第 N 轮评审没有交付」。
  - B 也可能照交接那句话写了文件：那样判定是 `delivered`，同样算对。
- **要记录什么**：判定和原因；B 听了哪边的话；dev 收到的话。
- **通过标准**【自动】：`check.sh` 全部 PASS（判定和文件实际情况一致，叫醒了 dev）。
- **清理**：无（B 留给 42、43）。

**记录**
- 判定 / 原因：第 5 轮 `delivered`（最后一行是 DONE）；第 6 轮补测同样 `delivered`
- B 是否写了文件：两轮都写了，而且都以 DONE 结尾——两处指令冲突时，Codex 听的是 handoff 那句固定的外层指令，不是 request.md 里的具体要求
- 结果：☑ 通过　☐ 不通过
- 备注：
  - 通过标准是「判定和 findings.md 实际情况一致」，两轮都满足，dev 都被正常叫醒。
  - 第 5 轮请求写的是「不要创建或修改任何文件」，第 6 轮改成「最后一行只写 TODO」，评审方两次都照 handoff 的「最后一行只写 DONE」办。结论：靠请求模板触发不了「没交付」，因为交接那句话本身就要求 DONE。
  - 「没交付」这条分支最终在 42 B 段自然触发（Codex 被 Esc 打断，这一轮没写新文件）。
  - dev 两轮都识破了这是演练，如实报告、没有改代码，也没动评审方会话。

## 42 人按 Esc 打断评审方

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（A 段 Claude haiku `lab-a/review-cc`；B 段 Codex `lab-a/review`） | 10 分钟 | **亲手按 Esc** | 41 |

- **目的**：
  - Claude Code 被 Esc 打断时没有事件，靠 `wait --quiet` 返回 `stopped-quiet`，watcher 判为 `interrupted`，不叫醒 A。
  - Codex 有打断事件：状态回到 idle，没有 DONE，判为 `undelivered`。
- **准备**：`lab/steps/42-esc/prepare.sh`（写入「逐个读文件」的慢请求，打印两段命令）。
- **操作步骤**：按 prepare 打印的 A、B 两段做。每段在评审方开始干活后，在它的接入窗口里按一次 Esc，之后什么都别按。
- **期望看到什么**：
  - A 段：
    - Esc 后约 20 秒 watch.log 出现 `interrupted`；
    - dev 没被叫醒；
    - `check.sh a` 全部 PASS。
  - B 段：
    - Esc 后很快出现 `undelivered`，那一行的 `last_event` 是 `Interrupt`；
    - dev 被叫醒并收到「没有交付」；
    - `check.sh b` 显示判定是 undelivered。
- **要记录什么**：两段从 Esc 到判定的秒数；dev 是否被叫醒。
- **通过标准**：两段都符合期望。
- **清理**：`clean.sh`（stop `lab-a/review-cc`；`lab-a/review` 留给 43）。

**记录**
- Claude（`lab-a/review-cc`）：Esc → interrupted **21.5** 秒；dev 被叫醒：☑ 否
- Codex（`lab-a/review`）：Esc → undelivered **0.9** 秒；last_event：**Interrupt**　dev 被叫醒：☑ 是（Esc 后 1.5 秒）
- 结果：☑ 通过　☐ 不通过
- 备注：2026-09-16 第一次人工跑过并确认通过，但秒数没记；同日环境清掉后由 Claude 全自动重跑一遍取准确数据（Esc 用 `corral keys <名字> esc` 发。**更正**：我当时说「钩子把它记成人在打字，和手按走同一条路」是错的——`keys` 不经过 `last_human_input` 的判定，见问题表第 50 条。等价性成立的真正理由是**同样的字节进同一个伪终端**，agent 侧的反应完全一样，这一步验的判定也只取决于 agent 侧。唯一的差别：真人按 Esc 会额外留下 `last_human_input`，watcher 随后叫醒 A 时可能吃一次 8 再重试；自动重跑这次没有这个环节。)
  - A 段：`idle_for` 20.076 触发判定，`last_event` 仍是 `PostToolUse`——**Claude 被 Esc 打断确实不产生任何事件**，只能靠 `wait --quiet` 的静默超时兜底，所以慢（21.5 秒）。判 `interrupted`，不叫醒 A。
  - B 段：**Codex 有 `Interrupt` 事件**，所以 0.9 秒就判出来了，原因是「findings.md 不存在」，判 `undelivered` 并叫醒 dev 告知没交付。这也正是 41 想验而没验到的那条分支。
  - 两段差 24 倍，是这一步最值得记的结论：**有事件的 agent 能立刻判定，没事件的只能等静默超时。**
  - 顺带撞出一条：B 段第一次 handoff 被拒——`b_changed_refused`，因为那个 Codex 是手工起的、不在 handoff 的实例记录里。13 那个「实例变了不送」的守卫在真实误用场景下挡住了盲送，提示语也指明了处理办法（先 stop 再来）。

## 43 评审方正忙时交下一轮

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（接 42） | 8 分钟 | 在场 | 42 |

- **目的**：交接时 B 正忙，send 得到退出码 7；handoff 等 B 这一轮结束后重试并送达。可选：watcher 叫醒 A 时 A 正忙，同样先 7 再送达。
- **准备**：`lab/steps/43-busy/prepare.sh`
- **操作步骤**：
  1. 窗口 3 连着运行 prepare 打印的两条命令：先 `corral send` 让 B 忙起来，再 handoff。
  2. 可选：handoff 返回后马上 `corral send lab-a/dev …` 让 dev 忙起来。
  3. 这一轮结束后运行 `lab/steps/43-busy/check.sh`。
- **期望看到什么**：handoff 输出先 `send_b_not_idle state=working`，B 答完旁支问题后 `send_b_delivered`；之后正常交付。可选部分出现 `wake_a_not_idle` → `wake_a_delivered`。
- **要记录什么**：从 `not_idle` 到送达等了多久；可选部分的结果。
- **通过标准**【自动】：`check.sh` 全部 PASS。
- **清理**：无。

**记录**
- 交给 B：not_idle → delivered 等了 **36** 秒（13:15:44 → 13:16:20）
- 叫醒 A 时遇到 7：☑ 是　☐ 否（没做可选）——可选段也做了，`wake_a_not_idle` → 19 秒后 `wake_a_delivered`
- 结果：☑ 通过　☐ 不通过
- 备注：2026-09-16 第一次人工跑过并确认通过，秒数没记；同日由 Claude 全自动重跑取准确数据。完整时间线：`send_b_not_idle`(working) → 36s → `send_b_delivered` → `watching` → 18s 后 `delivered`（最后一行是 DONE）→ `wake_a_not_idle`(working) → 19s → `wake_a_delivered`。两处退出码 7 的重试都按预期等到对方空闲才送，没有丢话也没有重复送。B 是复用的（`b_action: reused`）。

## 44 评审方卡在信任框【故障演练】

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（B = `lab-a/review-new`：Codex，在从没信任过的新仓库） | 5 分钟 | 在场 | 30 |

- **目的**：B 启动时卡在信任框，钩子没有事件，状态停在 `starting`。watcher 超时后记下「启动未完成」；人接入看到信任框，不点信任，直接 stop；全局配置不新增信任记录。
- **准备**：`lab/steps/44-trust/prepare.sh`（在 `/tmp/clab/untrusted-<时间>` 建一个新 git 仓库）。
- **操作步骤**：
  1. 窗口 3 运行 prepare 打印的 handoff 命令。
  2. 约 30 秒后 watch.log 出现 `start_incomplete`。
  3. 窗口 4 运行 `corral attach lab-a/review-new`，看到信任框，**什么都别选**，按 Ctrl-] 退出。
  4. `corral stop lab-a/review-new`
  5. `lab/steps/44-trust/check.sh`
- **期望看到什么**：
  - 看板上 B 一直是 `starting`；
  - `start_incomplete` 约在送出 30 秒后出现；
  - stop 后 watch.log 出现 `b_gone`，dev 没被叫醒；
  - Codex 信任记录里没有这个目录。
- **要记录什么**：接入时看到的框；`start_incomplete` 出现的时间；stop 用时。
- **通过标准**：`check.sh` 全部 PASS【自动】；接入确实看到信任框【人看】。
- **清理**：`clean.sh`（删掉未信任目录）。

**记录**
- 看到的框：Codex 的目录信任框——`You are in /private/tmp/clab/untrusted-1789534565 / Do you trust the contents of this directory? › 1. Yes, continue  2. No, quit`。同屏显示 `permissions: YOLO mode`，**证明 `--yolo` 绕不过这个框**（它挡在会话开始之前，钩子还没装上）。用 `corral read` 读屏代替人工 attach，什么都没点。
- start_incomplete：送出后 32 秒（`--start-timeout 30`），提示语「多半卡在对话框里」
- 结果：☑ 通过　☐ 不通过
- 备注：2026-09-16 补跑，由 Claude 全自动驱动。时间线 `b_started` → `watching` → `start_incomplete`(32s) → `b_gone`；状态全程 `starting`、`last_event: None`（一个事件都没有）；**没有任何 wake_a_***；stop 用 keys，退出码 0，用时约 38 秒；Codex 信任记录里没有这个目录。

---

# 阶段 5：第二个项目并行

## 50 第二个项目并行

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（4 个：`lab-a/dev` sonnet、`lab-a/review` luna、`lab-b/dev` haiku、`lab-b/review` luna） | 25 分钟 | 人看看板 | 01、10、30 |

- **目的**：两个不同前缀各跑一套交接循环，互不串扰：
  - 请求、结果、叫醒对象各归各；
  - 看板同时显示两套；
  - 第二个项目的 A 在自己的 worktree 里运行那一份 `lab/bin/handoff`。
- **准备**：`lab/steps/50-two-projects/prepare.sh`（检查 worktree，打印两个项目的命令和要说的话）。
- **操作步骤**：
  1. 窗口 6 挂 `corral attach --wait lab-b/review`；窗口 7 start 并接入 `lab-b/dev`。
  2. 让 `lab-b/dev` 做 B1，同时让 `lab-a/dev` 做任务 4。
  3. 两边都做完后，几乎同时让两边交接（话在 prepare 里）。
  4. 两轮都结束后运行 `lab/steps/50-two-projects/check.sh`。
- **期望看到什么**：
  - 看板上两套 agent 各自 `working` / `idle`；
  - 下方 watcher 记录分别显示 `lab-a`、`lab-b` 的轮次；
  - 窗口 4、6 各自接上自己的评审方；
  - 两个 dev 各自被叫醒。
- **要记录什么**：两套各自的轮次、判定和时间；有没有串（token、叫醒对象）。
- **通过标准**：`check.sh` 全部 PASS【自动】；看板显示正确【人看】。
- **清理**：`clean.sh`（stop `lab-b/*`）。

**记录**
- lab-a：第 10 轮　判定 delivered（送达 12:02:48 → 交付 12:03:45，57 秒）　　　lab-b：第 1、2 轮　判定都是 delivered（第 2 轮 12:07:05 → 12:07:41，36 秒）
- 串扰：无。两边的 findings.md 都只含自己的 token，不含对方的；内容也完全不交叉（lab-a 通篇 `--account-prefix`，lab-b 通篇 B1 导出）；A/B 配对、叫醒对象都对。
- 结果：☑ 通过　☐ 不通过
- 备注：2026-09-16。四个 agent 同时活着（lab-a/dev sonnet、lab-a/review luna、lab-b/dev haiku、lab-b/review luna）。
  - 这一步由 Claude 用 `corral send` 代替人在接入窗口打字驱动，看板显示是否正确【人看】这项没有人工确认，其余全部来自 `check.sh`。
  - lab-b 第 1 轮 `findings.md 含 LAB-B-TOKEN` FAIL：评审方无视了 request.md 里「第一行原样抄写 token」这句（lab-a 的评审方照做了）。第 2 轮把要求写硬（「这是路由校验探针，必须照抄」）后就照做，全部 PASS。和 41 是同一类现象，不是 corral 的路由问题。
  - 第 2 轮自然跑出完整重试链：`wake_a_not_idle`（A 正忙，7）→ `wake_a_human_active`（人在窗口 7 敲字，8）→ 72 秒后 `wake_a_delivered`。

---

# 阶段 6：故障演练

## 60 协议兼容【故障演练】【白盒】

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（Claude haiku，两句短话） | 8 分钟 | 中途接入一次 | 01 |

- **目的**：改动 corral 代码后，新命令操作旧栏位。只用 `git archive` 导出的副本，不改 corral 仓库。
  - A 旧版本（默认提交 c75876e）起的栏位：副本删掉后，当前命令照常能用。
  - B 协议版本 2：当前命令以退出码 9 拒绝，只能用对应版本 stop。
  - C 事件格式 2：当前命令以退出码 9 拒绝，只能用对应版本 stop。
- **准备**：`lab/steps/60-compat/prepare.sh`
- **操作步骤**：
  1. `lab/steps/60-compat/run.py`
  2. 脚本停下来时，另开窗口 `corral attach lab/compat-old`，看到界面后按 Ctrl-]，回来按回车。
- **期望看到什么**【自动】：
  - A 段 status、send、wait、reply、stop 都成功，`proto` 为 1；
  - B 段 status、stop 得到 9，ls 标出 `incompatible`，副本自己的 stop 成功；
  - C 段 status 得到 9，副本自己的 wait、stop 成功。
- **要记录什么**：
  - 9 时的 `message`；
  - attach 旧栏位的表现；
  - C 段最后一行「记录」：副本自己的命令读过事件之后，当前命令再 status 的退出码。自检里是 0：当前命令直接用了副本写下的读取进度，没有再检查事件格式。真 agent 上如果也是 0，记到「发现的问题」。
- **通过标准**：全部 PASS；attach 旧栏位能看到界面、Ctrl-] 正常退出【人看】。
- **清理**：`run.py` 自己清；中途打断时 `clean.sh`。

**记录**
- B 的 message：`lab/compat-p2 runs pen protocol 2, this corral supports [1]; stop it with a matc…`（退出码 9，`ls` 里标 `incompatible: True, proto: 2`）
- C 的 message：`event format version 2 is not supported by this corral (supported: [1]); stop an…`（退出码 9）
- attach 旧栏位：用 `corral read` 代替人工 attach，读到正常的 Claude 界面（agent 回了「收到」），旧栏位可读
- 结果：☑ 通过　☐ 不通过
- 备注：2026-09-16 补跑，由 Claude 全自动驱动（中途那次人工 attach 换成 `corral read`，所以「Ctrl-] 正常退出」这项没验）。当前 corral 7eca959，旧版副本 c75876e。A 段 status/send/wait/reply/stop 全部成功、proto=1。
  **自检时的悬案在真 agent 上复现了**：C 段副本自己的命令读过事件之后，当前命令再 `status` 得到 **0** 而不是 9——直接用了副本写下的读取进度，没再检查事件格式版本。已记进「发现的问题」。

## 61 事件文件长期增长【故障演练】【白盒】

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（Claude haiku，一句短话） | 5 分钟 | 跑脚本 | 01 |

- **目的**：长期运行的 agent 事件文件越来越大（这里直接追加 50MB 别的会话的事件），`status` 仍然快，状态计算仍然正确。
- **准备**：`lab/steps/61-bigevents/prepare.sh`
- **操作步骤**：`lab/steps/61-bigevents/run.py --mb 50`
- **期望看到什么**【自动】：
  - 追加后第一次 status 要读完新增部分，会慢一些，只记录；
  - 之后的中位数和基线差不多；
  - send、wait、reply 正常；
  - 删掉读取进度后从头重算一次，只记录。
- **要记录什么**：基线、追加后第一次、稳定中位数、重算的毫秒数。
- **通过标准**：全部 PASS（稳定中位数不超过基线 + 100ms）。
- **清理**：`run.py` 自己 stop；中途打断时 `clean.sh`。

**记录**
- 基线 34 ms；追加后第一次 644 ms；稳定 35 ms；重算 635 ms
- 结果：☑ 通过　☐ 不通过
- 备注：2026-09-16 补跑，纯脚本。追加 320000 行，事件文件 239 → 52,475,877 字节。追加后第一次要读完新增部分所以 644ms，之后中位数 35ms（基线 34ms，远低于 +100ms 的线）；删掉 cursor 从头重算 635ms，状态仍是 idle，重算后中位数还是 35ms。send / wait / reply 全正常。

---

# 阶段 7：长时间使用

## 70 退出整个终端软件

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（`lab-a/dev`、`lab-a/review` 在跑） | 10 分钟 | 在场 | 30 |

- **目的**：接入窗口、看板都开着时直接退出整个终端软件，agent 都还在；重新打开后能接回去，对话还在，能接着干活。
- **准备**：`lab/steps/70-quit-terminal/prepare.sh`（拍快照）。
- **操作步骤**：
  1. 确认要退出的终端软件里没有别的只在它里面跑的重要东西。也可以把 lab 的窗口开在另一个终端软件里，只退出那个。
  2. Cmd-Q 退出整个终端软件，再重新打开。
  3. `lab/steps/70-quit-terminal/check.sh`
  4. `corral attach lab-a/dev`，看之前的对话；在里面问「我们刚才做到哪了？用两句话说」。
  5. 重新开看板。
- **期望看到什么**：
  - 快照比对全部 PASS，实例编号不变；
  - 接入后能看到之前的对话；
  - dev 答得出之前做到哪；
  - 看板正常。
- **要记录什么**：快照比对结果；dev 的回答。
- **通过标准**：`check.sh` 全部 PASS【自动】；对话还在【人看】。
- **清理**：无（agent 留给 71）。

**记录**
- 快照比对：☑ 全部通过（`lab-a/dev` 1e68cdbbc728 → 1e68cdbbc728；`lab-a/review` 0121399c6583 → 0121399c6583）
- dev 的回答：「我请另一个 agent（Codex，通过 lab-a handoff）评审了任务 1、2 的提交，结果无阻塞问题，只提了两条低风险的可选改进。我按建议补了一条任务 1 的边界测试，并修了任务 2 里 balances_for_month 未补零月份会误匹配的问题，两个提交都已完成，37 个测试全绿。」
- 结果：☑ 通过　☐ 不通过
- 备注：2026-09-16 补跑。
  - 终端软件：Claude（本会话）和 corral-67 都在 Ghostty 里，所以 lab 窗口开在 **Metalterm**、只退 Metalterm，避免把主控会话一起杀掉。退出前用进程树确认：`corral attach lab-a/dev` 和看板都挂在 Metalterm 下，`lab-a/dev` 显示 `attached=1`。
  - 退出后 attach 进程和看板随 Metalterm 一起消失，两个 agent 都还在、**实例编号不变**——同一个进程活了下来，不是被重启。`lab-a/dev` 事件文件多了 254 字节（约一条钩子事件），状态仍 idle，不影响判定。
  - 重开后接入，退出前的对话还在；dev 的回答细节准确，核对属实：两个提交 `8e7e2ba`、`60f9dd5` 确实在，37 个测试全过。看板正常显示两个 agent 都是 idle。
  - **第一次退出作废**：人在环境还没搭完、快照还没拍的时候就退了，没有「退出前」基线，而且没法确认当时开没开 attach 窗口。环境搭完拍好快照后重来一次，并先确认 `attached=1` 再退。教训：要人动手的破坏性步骤，必须等前置确认完才能说「可以开始」，而且要把这句放在最醒目的位置。
  - **清理后 confhash 报 `~/.claude/settings.json` 变了**（今天第一次）。修改时间 16:06:18；16:01 那次检查还是「未变」。
    那一两分钟里启动了两个 Claude Code：搭环境时 corral 起的 `lab-a/dev`，和人在 Metalterm 里开的那个会话，单凭时间分不出是谁写的。
    `lab-a/dev` 的启动参数（`--model`、`--add-dir`、`--allowedTools`）都不会落盘，corral 注入钩子也走命令行参数不写 settings.json，所以**大概率是 Claude Code 运行时自己写的**（文件里有 `feedbackSurveyState` 这类它自己维护的字段）——但这是推测，没有证实。
    confhash 按设计只存哈希不存内容，`~/.claude/backups/` 里也只有 `.claude.json` 的备份，**拿不到改之前的内容，无法确认改了哪个字段**。没有动这个文件，留给人核对。

## 71 过夜【暂缓】

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| 真 agent（`lab-a/dev`、`lab-a/review` 开着过夜） | 跨夜；晚上、早上各 10 分钟 | 在场 | 70 |

- **目的**：agent 开着过夜（电脑可以睡眠，不重启），第二天对话还在，同一个评审方接着用。
- **准备**：晚上运行 `lab/steps/71-overnight/prepare.sh`：叫醒 dev 说明明天做任务 5，并拍快照。
- **操作步骤**：
  1. 晚上：运行 prepare.sh 后放着过夜。
  2. 早上：
     1. `lab/steps/71-overnight/morning.sh`，比对快照；
     2. `corral attach lab-a/dev`，看昨天的对话；
     3. 说 morning.sh 打印的那句话（任务 5 + 请评审）；
     4. 这一轮结束后运行 `lab/steps/71-overnight/check.sh`。
- **期望看到什么**：
  - 快照比对全部 PASS，栏位内存、事件文件大小的变化会列出；
  - 对话还在；
  - 今早这一轮 `send_b_delivered` 的实例编号就是昨晚的评审方；
  - 交付，dev 被叫醒。
- **要记录什么**：过夜时长；电脑有没有睡眠；内存和事件文件的变化；check 结果。
- **通过标准**：快照比对和 `check.sh` 全部 PASS；对话还在【人看】。
- **清理**：`clean.sh`，然后做 99。

**记录**
- 过夜：　点 → 　点；睡眠：☐ 有　☐ 无
- 栏位内存变化：　　　事件文件变化：
- 结果：☐ 通过　☐ 不通过　（暂缓）
- 备注：2026-09-16 暂缓——要真过一夜，不是跳过。70 已经通过，前置满足，随时可以挂。

---

# 收尾

## 99 清理与核对

| 需要 | 时长 | 人在场 | 依赖 |
|---|---|---|---|
| — | 5 分钟 | 在场 | — |

- **目的**：把 corral-lab 之外的测试痕迹去掉，改不了的列出来手动处理；最后核对全局配置。
- **操作步骤**：
  1. `lab/cleanup.py`，它会依次：
     1. 停掉 lab 的后台脚本；
     2. stop lab 的 agent（含 skill 起的临时 agent、兼容演练留下的栏位）；
     3. 删状态目录里的残留；
     4. 移除 worktree 和 `lab/` 分支；
     5. 比对全局配置指纹；
     6. 删 `/tmp/clab`；
     7. 列出其他痕迹。
  2. 按输出手动删：
     - `~/.codex/config.toml` 里列出的 `[projects."…"]` 段；
     - `~/.claude.json` 里 `projects` 下列出的键（先退出所有 Claude Code）。
  3. 可选：删对话记录，运行 `lab/bin/traces --purge-transcripts`（只删 lab 目录对应的 Claude Code 对话记录目录和 Codex 会话文件）。
  4. 可选：`git reset --hard lab-baseline`，把 corral-lab 恢复到初始提交。
  5. 再运行一次 `lab/bin/traces` 确认。
- **期望看到什么**：
  - `corral ls` 里没有 lab 的 agent；
  - `/tmp/clab` 不存在；
  - 全局配置除了你还没删的信任记录外未变；
  - traces 只剩你决定保留的东西。
- **要记录什么**：confhash 结果；手动删了哪些；是否删对话记录。
- **通过标准**：同期望。

**记录**
- confhash：cleanup 第 5 步报「只多了信任记录」——`~/.codex/config.toml` 里 corral-lab 那一段；`~/.claude/settings.json`、`~/.codex/hooks.json`、两份 SKILL.md 都未变。
- 手动删除：已删 `~/.codex/config.toml` 第 223–225 行（corral-lab 的 `[projects…]` + `trust_level` + 空行），删后 TOML 解析正常、其余 68 个 projects 和 mcp_servers 原样。备份在会话 scratchpad 的 `config.toml.bak`。`~/.claude.json` 里 corral-lab 的 projects 键**没删**（corral-lab 是自己的仓库，还要继续用；要删得先退出所有 Claude Code）。
- 对话记录：☐ 删了　☑ 保留
- 结果：☑ 通过　☐ 不通过
- 备注：2026-09-16 12:15 左右。`corral ls` 空、`~/.corral` 已删、`/tmp/clab` 已删、三个 worktree 和 `lab/` 分支都已移除。
  - 没做 `git reset --hard lab-baseline`——那会连这份测试记录一起丢掉。ledger 的提交和 CHECKLIST 记录都留在 main 上。
  - confhash 的基线存在 `/tmp/clab/confhash.json`，被第 6 步连着删了，所以删完信任记录没法再用 confhash 复验，改成直接校验 TOML + diff 备份。**下次应该把基线存到 `/tmp/clab` 外面，或者把「删信任记录」挪到删 `/tmp/clab` 之前。**（已改：基线改存 `lab/.confhash.json`，见 ISSUES 第 6 条）

---

# 发现的问题

| 步骤 | 现象 | 复现方式 | 属于 corral / lab 脚本 / agent | 处理 |
|---|---|---|---|---|
| 01 | `confhash check` 把「只多了 Codex 信任记录」误报成「变了」 | 点信任后运行 `lab/bin/confhash check` | lab 脚本 | 已修：去掉信任段时不再连段前的空行一起删 |
| 12 | 人在输入框里留着没提交的草稿时，`send` 的文字接在草稿后面一起被提交：agent 收到的是拼接后的内容并照做，corral 却因文字对不上报 `not_delivered`（退出码 3）。调用方以为没送到，重试就会送第二遍 | 在接入窗口里打几个字不提交，静置 30 秒后 `corral send` | corral | **已修** corral `48fb26a`：识别「送出的文字是这条输入的一部分」，判送达并标 `merged_with_draft: true`。回归检查 `lab/steps/12-typing/draftcheck.py`，实测全 PASS 
| 50 | ~~`corral keys` 打进去的按键被记成「人在打字」，紧接着的 `send` 被退回 8~~　**这条记错了，已更正**：实测 `attached=0` 时 `keys` 之后 `last_human_input` 仍是 `None`、`send` 退 0。当时那个 8 是真的，但来自窗口 7 里人的实际操作（那个窗口正 attach 着），不是 `keys` 造成的 | 对照实验：起一个不接入的 agent，`corral keys text:hello` 后立刻 `send` | 无（我的误判） | 已在 ISSUES 第 4 条写明更正和教训：两件事挨在一起不等于有因果。真正要注意的是 `keys` 之后 agent 要过一会儿才反应，`send` 可能退 7，先 status/wait 再送 |
| 41 / 50 | 评审方只听 handoff 那句固定的话，request.md 里的额外要求（「findings 第一行照抄 token」「最后一行写 TODO」）会被忽略；把要求写得更硬才照做 | 在 request.md 里写一条和 handoff 那句话无关的要求 | agent | 不是 corral 的问题。lab 脚本这边：要验的东西得写进 handoff 送出的那句话，或者在 request.md 里写明「必须」 |
| 99 | confhash 的基线存在 `/tmp/clab/confhash.json`，而 cleanup 第 6 步就把 `/tmp/clab` 删了，于是第 2 步手动删信任记录之后没法再用 confhash 复验 | 跑完 `lab/cleanup.py` 再 `lab/bin/confhash check` | lab 脚本 | 待改：基线存到 `/tmp/clab` 外面，或者把「删信任记录」放到删 `/tmp/clab` 之前 |
| 60 | 事件格式版本不兼容时，`status` 本该退 9；但只要有别的命令先把读取进度（cursor）写下来，当前命令再 `status` 就返回 0——直接信了 cursor，没再检查事件格式版本。等于版本保护能被绕过 | 60 C 段：副本自己的 `wait` 读一次事件，再用当前命令 `status` | corral | **待修**。自检时就是 0，真 agent 复跑仍是 0，不是偶发。建议读 cursor 之后仍校验一次事件格式版本 |
| 70 | 清理后 confhash 报 `~/.claude/settings.json` 变了，修改时间 16:06:18。同一时段启动了两个 Claude Code（corral 起的 `lab-a/dev`、人在 Metalterm 开的会话），分不出是谁写的 | 无法复现，只观察到一次 | 待查（大概率是 Claude Code 运行时自己写的，非 corral） | **待人工核对**。lab 这边的改进点：confhash 只存整文件哈希，出事时只能说「变了」说不出变在哪。可以改成按顶层键分别存哈希——仍然不存任何值，但能指出是哪个键变了 |
| 02 / 03 | Codex 正常退出（连按两次 Ctrl-C）的收尾时间波动大：03 用了 13.1 秒正常退出，02 跑过三轮后超过 20 秒，被 corral 升级到 SIGTERM（`exit_code: -15`）。M8 实测是 7.6 秒 | 起 Codex，跑几轮后 `corral stop` | corral | **已修** corral `48fb26a`：等待从 20 秒放宽到 60 秒（实测跑过三轮要 27.7 秒），`stop` 默认超时 30→90。2026-09-16 定量：刚起 13–15 秒、跑过三轮 27–28 秒，不是波动是随会话内容增长；「两次 Ctrl-C 间隔太快」的猜想已证伪。回归断言加在 `lab/steps/03-lifecycle/run.py`，2026-09-16 已用真 Codex 验过：25.6 秒、`stopped_by=keys`、`exit_code=0` |
