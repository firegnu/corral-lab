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
| 71 | 过夜 | g | 真 | 跨夜 | 早晚各 10′ | 70 |
| 99 | 清理与核对 | — | — | 5′ | 在场 | — |

覆盖：a 临时委派；b 长期驻留的工作 agent；c 文件交接的请求 / 交付循环；d 异常路径；e 观察；f 多项目并存；g 生命周期与故障；h 内容。

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
- 日期：
- corral 提交：
- Claude Code 版本：　　　Codex 版本：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
| lab/probe-cc-main | 仓库 | | | |
| lab/probe-cx-main | 仓库 | | | |
| lab/probe-cc-a-review | wt-lab-a-review | | | |
| lab/probe-cx-a-review | wt-lab-a-review | | | |
| lab/probe-cc-b | wt-lab-b | | | |
| lab/probe-cx-b-review | wt-lab-b-review | | | |

- 新增信任记录：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- Claude Code：首句 ☐ 送达　代码块 ☐ 送达（latency　）　问号开头 ☐ 送达；复述差异：
- Codex：首句 ☐ 送达　代码块 ☐ 送达（latency　）　问号开头 ☐ 送达；复述差异：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
  - Codex stop 以 `keys` 结束、退出码 0，用时 10 秒左右。
  - 「记录」行写明栏位被杀后 agent 进程有没有残留。
- **要记录什么**：Codex stop 用时和 `stopped_by`；栏位被杀后 agent 是否成了孤儿进程；Claude 被杀后的 `exited`。
- **通过标准**：全部 PASS。孤儿进程只记录，不算不通过；脚本会结束掉它。
- **清理**：`run.py` 自己清；中途打断时 `clean.sh`。【白盒】从 meta.json 取栏位进程号。

**记录**
- Codex stop：用时　　　stopped_by　　　exit_code
- 栏位被杀后 agent：☐ 也退出了　☐ 残留
- Claude 被杀后 exited：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 真沙箱 message：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 自动接上用时：
- 看板状态变化：
- 任务 1 提交：
- 只读窗口 ☐ 打不了字　尺寸 ☐ 跟随能打字的窗口
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 第一条：delivered ☐　latency
- 第二条：not_idle ☐ → delivered ☐　等了
- 结果：☐ 通过　☐ 不通过
- 备注：

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
  - B：没有预设结果。可能是草稿和送的话拼成一句被提交，corral 对不上文字，报「没确认送达」（wake 退出码 4）。
- **要记录什么**：A 从按键到送达的秒数；B 的 wake 输出、dev 实际收到的话、dev 输入框里的样子。
- **通过标准**：A 满足期望。B 只记录，不影响通过；如果确认是设计缺口，记到最后的「发现的问题」里。
- **清理**：确认 dev 输入框里没有残留的字。

**记录**
- A：按键到送达　秒；鼠标划过是否推迟：
- B：wake 输出　　　dev 收到　　　输入框
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 实例编号：　　→
- 可选变体：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 临时名字：　　　模型参数：☐ 传了　☐ 没传
- wait 次数：　　总用时：　　权限框：
- 转述 ☐ 与原文一致
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 名字 / 实例：
- 第二问命令：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- A 名字：　　　是否同时 working：　　　意见是否串：
- B：☐ 全部通过
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 临时名字：　　　模型参数：　　　wait 次数：　　　转述一致：
- stop 后窗口 4 ☐ 回到等待
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- handoff：　　B 交付：　　A 被叫醒：
- B 实例：　　　findings 第一行：
- 窗口 4 ☐ 自动接上
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- B 实例：30 的　　　31 的
- 归档：　　　窗口 4 ☐ 回到等待
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 新 B 实例：　　　暗号行：
- 窗口 4 ☐ 自动再接上
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 弹框次数：　　　blocked 延迟 / 持续：
- 有无误判：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 判定 / 原因：
- B 是否写了文件：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- Claude：Esc → interrupted　秒；dev 被叫醒：☐ 否
- Codex：Esc → undelivered　秒；last_event：　　dev 被叫醒：☐ 是
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 交给 B：not_idle → delivered 等了　秒
- 叫醒 A 时遇到 7：☐ 是　☐ 否（没做可选）
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 看到的框：
- start_incomplete：送出后　秒
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- lab-a：第　轮　判定　　　lab-b：第　轮　判定
- 串扰：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- B 的 message：
- C 的 message：
- attach 旧栏位：
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 基线　ms；追加后第一次　ms；稳定　ms；重算　ms
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- 快照比对：☐ 全部通过
- dev 的回答：
- 结果：☐ 通过　☐ 不通过
- 备注：

## 71 过夜

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
- 结果：☐ 通过　☐ 不通过
- 备注：

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
- confhash：
- 手动删除：
- 对话记录：☐ 删了　☐ 保留
- 结果：☐ 通过　☐ 不通过
- 备注：

---

# 发现的问题

| 步骤 | 现象 | 复现方式 | 属于 corral / lab 脚本 / agent | 处理 |
|---|---|---|---|---|
| | | | | |
