# corral 手工测试发现的问题

2026-09-16 按 `CHECKLIST.md` 手工跑完 25 条（只跳过 70 退终端软件、71 过夜，这两条没法自动化）。
下面是跑出来的问题，按「该不该动 corral」分档。每条都注明是哪一步跑出来的，详细时间线在 `CHECKLIST.md` 对应小节的「记录」里。

测试环境：corral `7eca959`，Claude Code 2.1.273，codex-cli 0.154.0。

---

## 一、要改 corral

### 1. 事件格式版本保护能被绕过（最该查的一条）　——　**已修：corral `f2409de`**

**现象**
事件格式版本不兼容时，命令本该以退出码 9 拒绝。但只要**有别的命令先把读取进度（cursor）写下来**，当前命令再 `status` 就返回 **0**，直接按正常栏位处理——等于版本保护被绕过了。

**复现**（`lab/steps/60-compat/run.py` C 段，全自动）
1. `git archive` 导出一份 corral 副本，把它的事件格式改成版本 2；
2. 用副本起一个栏位 `lab/compat-e2`；
3. 当前 corral `status lab/compat-e2` → **退出码 9**，`message` 是
   `event format version 2 is not supported by this corral (supported: [1]); stop an…`　← 正确；
4. 让副本自己的 `corral wait` 读一次事件（这一步会写下 cursor）→ `result=idle`；
5. 当前 corral 再 `status lab/compat-e2` → **退出码 0**　← 问题在这里。

**证据**
假 agent 自检时就是 0，2026-09-16 用真 agent 重跑仍是 0，不是偶发。
`run.py` 里这一行本来就是作为「记录项」留的，两次都复现：
`记录  C 副本读过之后，当前命令再 status  —— 退出码 0（0 表示直接用了副本写下的读取进度，没有再检查事件格式）`

**期望**
读到 cursor 之后仍然校验一次事件格式版本，不能因为「有进度可用」就跳过检查。

**诊断结论**（2026-09-16，另一个会话查完，只诊断没改代码）

根因在 `src/corral/events.py`：**事件格式版本检查只做在「本次新读到的行」上，cursor 本身不记格式版本，也不做校验。**

- `_consume_line` 逐行检查 `e["v"]`（events.py:140-159），只有这次从 offset 读到末尾的行才经过它；
- `_load_cursor`（events.py:99-108）只校验 cursor 结构版本、实例编号、offset 不超过文件大小，**不记录也不校验「这份快照是按哪个事件格式算出来的」**；
- 所以第 3 步报 9 时 `read()` 在 `_save_cursor` 之前就抛了，没写 cursor；第 4 步副本把 offset 推到文件末尾并写下它算的快照；第 5 步当前 corral 读到这个 cursor，新增字节为 0，**一行都不消费**，直接把副本算的快照当结果返回，退 0。

**修正我上面的判断**：不是「彻底绕过」，而是**随读取进度来回抖动**——之后钩子再追加一条 v2 事件，当前 corral 又退 9；再被副本读走，又退 0。退出码由「上一次是谁读的」决定。

**影响面比原先写的大**：所有走 `events.read` 的命令都一样——`status`、`wait`、`send`（送达确认和 idle 判断）、`reply`。返回 0 时的 state / last_event / inputs / reply 全是另一个版本按它自己的规则算出来的快照，当前版本直接信了。

**那两个「顺便想确认的」有答案了**：
- `ls` **不受影响**：`registry.list_agents` 只发 status 请求，走协议版本检查，不读事件文件。反过来说，事件格式不兼容的栏位在 `ls` 里不会被标 `incompatible`——这是设计如此，`ls` 只看协议。
- proto=2 那条路径（`src/corral/client.py` 的 `request`）**没有**同样的洞：每次请求都重新读 `meta.json` 的 proto 和应答里的 proto，两处都过 `check_proto`，没有可被别的版本写坏的缓存。补做「副本先读一次」的对照实验结果也会是 9。

**建议修法**（二选一，倾向第一个）
1. **cursor 里记事件格式版本**：`fresh()` 加一个字段（如 `"fmt"`），`_load_cursor` 发现 cursor 记的格式不在本版本 `EVENT_FORMATS` 里就直接抛 9——不要退回 fresh，退回 fresh 会从头重读，最终也会在第一行抛 9，但 50MB 的文件要白读一遍（见第 61 步的实测：重算一次 635ms）。改动集中在 events.py 两处，补一条单元测试「先落一份 `EVENT_FORMATS=(2,)` 的 cursor，再 read 应退 9」。
   **注意**：不能只靠 `CURSOR_VERSION` 顶替——副本改事件格式时 `CURSOR_VERSION` 没变，这次就是这么漏的。
2. 更保守：`read()` 在 offset 已到文件末尾（一行都没读）时，回头读最后一行校验 `v`。多一次 seek，但能覆盖「cursor 是谁写的」不可知的情况；缺点是事件文件可能正被写到一半，要处理不完整的尾行。

**值得记进 DESIGN / SPIKE 的一句话**：cursor 是**跨版本共享的状态文件**，任何「按版本拒绝」的检查都得在 cursor 上也做一遍，不能只做在事件流上。

**修复结果**（corral `f2409de`，2026-09-16，`src/corral/events.py`、`tests/test_events.py`、`docs/DESIGN.md`）
按修法 1 做的：cursor 里记 `fmt`，`_load_cursor` 认不出就直接抛 9。复审时改过一处语义——第一版记的是 `max(EVENT_FORMATS)`（写 cursor 那个 corral 的能力上限），会导致**事件全是 v1 的栏位被支持 (1,2) 的命令读过之后，只认 (1,) 的命令被误拒**，报错还指向文件里根本不存在的版本；改成记「**已消费事件里 `v` 的最大值**」，即这份快照到底是从哪个格式的事件算出来的。另外第一版 `fmt` 只在 `fresh()` 里写，老 cursor 读过写回仍然没有这个字段，也一并补成「缺字段按 1 补上，随下次写回落盘」。

复验（三项独立构造，不依赖它自己的测试）：原绕过链现在退 9；v1-only 栏位旧命令照常可用；老 cursor 读过一次后带上 `fmt=1`。全量 `tests/` 186 passed + 134 subtests。
DESIGN 5.4 补了那句跨版本 cursor 的规则。

---

### 2. 输入框里有没提交的草稿时，`send` 被误报成没送到　——　**已修：corral `48fb26a`**

**现象**
人在接入窗口的输入框里留了一段没提交的文字，这时 `corral send`，送进去的文字**接在草稿后面一起提交**。agent 实际收到了拼接后的内容并照做了，但 corral 因为回读的文字和送出的对不上，报 `not_delivered`（**退出码 3**）。

**后果**
调用方以为没送到，重试一次就送了第二遍。

**复现**（步骤 12 B 段）
在接入窗口里打几个字**不要提交**，静置 30 秒（躲开 human_active 的静默窗口），然后 `corral send`。

**修复**（corral `48fb26a`）：两条候选都没选，走了第三条路——快照多留最近一条输入的原文，
送出之后的最近一条输入事件里**包含**送出的文字就算送达，退 0 并输出新字段 `merged_with_draft`
（`true` 表示和草稿拼在一起了，正常送达为 `false`）。既不丢人的草稿，也不让调用方重送。
CONTRACT、AGENT_USAGE、DESIGN 5.2 都写了「不要重送」。

**复验**（2026-09-16，真 agent）：`lab/steps/12-typing/draftcheck.py` 六项全 PASS——
草稿种进去、送话退 0、`merged_with_draft=True`、agent 回了「收到」。同样场景修复前是退出码 3。

---

## 二、要观察，也可能只是文档

### 3. Codex 的退出等待（20 秒）对用过的会话不够　——　**已修：corral `48fb26a`**

**不是「波动」。** 原先那么写是因为三个数据点来自不同状态的会话。2026-09-16 采样后结论变了：同一状态下几乎没有波动，差别在「会话有没有跑过内容」，是系统性的。

`corral stop` 对 Codex 的步骤写在 `src/corral/agents/codex.py:29`：

```python
quit_steps = ({"keys": CTRL_C, "wait": 0.3}, {"keys": CTRL_C, "wait": 20}, {"signal": "TERM", "wait": 3})
```

发 Ctrl-C → 隔 0.3 秒 → 再发 Ctrl-C → **最多等 20 秒** → 还活着就 SIGTERM → 3 秒 → SIGKILL。
（对照 Claude：`SIGHUP` 等 5 秒 → `SIGTERM` 等 3 秒，所以 Claude 那边从不出问题。）

**实测**（2026-09-16，gpt-5.6-luna low，每次都是新会话）

| 会话状态 | n | 用时 | 结果 |
|---|---|---|---|
| 刚起（只提交过一句） | 5 | 13.2 / 13.6 / 13.5 / 14.2 / 15.4 秒 | 全部 `keys` 正常退出，**0/5** 升级 |
| 跑过三轮，走 `corral stop` | 5 | 20.4 秒 ×5 | 全部 SIGTERM（`exit_code: -15`），**5/5** 升级 |
| 跑过三轮，绕开 corral 自己发 Ctrl-C | 2 | **27.7 / 27.3 秒** | 自己正常退出 |

第二行的「20.4 秒 ×5」不是收尾时间，是**上限本身**——测量被截断了。第三行才是真值：**跑过内容的会话要 27–28 秒**，比 20 秒的上限多出约 40%，所以必然被 SIGTERM。

**顺带证伪一个猜想**：怀疑过「两次 Ctrl-C 只隔 0.3 秒太快、第二次被吞掉」。把间隔拉到 1.5 秒重测，仍然要 27 秒才退——间隔不是原因，Codex 就是要花这么久。

**建议**：把第二步的 `wait` 从 20 秒放宽，已知最大 27.7 秒，至少给到 45 秒才有余量。
但注意**退出耗时随会话内容增长**（13–15 秒 → 27–28 秒，才跑了三轮），跑一整天的会话可能更久，固定阈值天生脆弱。更稳的做法是轮询进程还在不在、只在长时间毫无动静时才升级——具体怎么改要看 corral 的实现来定。

**样本量**：真值那一行只有 n=2，「跑过内容」也只到三轮。要更硬的数字得再采，但「20 秒不够」这个结论已经很确定。

**修复**（corral `48fb26a`）：选了 (a)，第二步的 `wait` 从 20 秒改成 60 秒（栏位允许的单步上限，观测值 27.7 的两倍），
`stop` 命令默认 `--timeout` 从 30 改成 90，盖住 0.3 + 60 + 3 的整条序列。
没选 (b) 轮询：收尾期间 Codex 没有任何输出，栏位手里没有能区分「还在收尾」和「挂死」的信号，
轮询「毫无动静」只会更早升级而不是更晚。要做 (b) 得先验证收尾期间钩子事件文件是否还在增长（SPIKE 记过
Codex 的记忆子 agent 会在收尾时改 `~/.codex/memories`，那段若走钩子就有信号），需要真 Codex 实验，暂时搁置。

**回归检查**：`lab/steps/03-lifecycle/run.py` 里 Codex 改成先跑三轮再 stop，断言 `stopped_by=keys`、
`exit_code=0`、用时 60 秒以内。
**2026-09-16 已用真 Codex 验过**：跑过三轮的会话 stop 用时 **25.6 秒**，`stopped_by=keys`、`exit_code=0`，正常收尾；
同一场景在旧的 20 秒上限下必然被 SIGTERM 截断（`exit_code: -15`）。03 的 16 项全 PASS。新阈值留了约 2.3 倍余量。

### 4. 写脚本必踩的两个坑　——　**已写进 `AGENT_USAGE.md`（corral `48fb26a`）**

**坑一：`corral read` 返回的是累积的屏幕内容，不是当前画面。**
拿整屏做子串匹配一定会被历史内容骗到——2026-09-16 实测踩过：启动横幅里出现过「Ask Codex to do anything」，于是在信任框还开着的时候被误判成「输入框已就绪」，字打在框上被吞掉，紧接着那个回车正好点掉了信任框，结果什么都没提交、栏位永远停在 `starting`，排查时还一度被我误判成额度问题。
判断当前画面只能看**屏幕尾部**（实测取最后 300 字符够用）。

**坑二：`keys` 之后别立刻 `send`，但原因不是「人在打字」。**
这条我原先写错了，已更正。原文写的是「`corral keys` 打进去的按键会被记成人在打字，紧接着的 `send` 被退回 8（human_active）」——**不成立**。

2026-09-16 实测（Claude haiku，`attached=0`，纯脚本操作，没有任何人碰键盘）：
```
起来了：attached=0  last_human_input=None
corral keys text:hello   →  last_human_input 仍然是 None
紧接着 corral send       →  退出码 0
```
`keys` 走的是栏位的 `write_chunks`，不经过 `last_human_input` 的判定。

那步骤 50 里那个真实的退出码 8 是哪来的？当时窗口 7 正 `attach` 着 `lab-b/dev`，最可能是人在那个窗口里的实际操作被记下了。我把「我刚发过 keys」和「随后出现 8」这两件同时发生的事当成了因果，没做对照实验。**教训：两个事件挨在一起不等于有因果，手上有 `attached` 字段却没看。**

真正要注意的是：`keys` 之后 agent 要过一会儿才反应，紧接着 `send` 可能因为状态还没变而退 **7（not_idle）**，应该先 `status` / `wait` 再送。

---

## 三、不归 corral 管（记在这里只为完整）

### 5. lab 脚本：`confhash check` 误报　——　**已修**
去掉 Codex 信任段时连段前的空行一起删了，导致「只多了信任记录」被报成「变了」。

### 6. lab 脚本：confhash 基线放在 `/tmp/clab` 里，被 cleanup 自己删掉　——　**已修**
`cleanup.py` 第 6 步删 `/tmp/clab`，而基线就存在 `/tmp/clab/confhash.json`，于是第 2 步「手动删信任记录」之后没法再用 confhash 复验。
改法：基线挪出 `/tmp/clab`，改存 `lab/.confhash.json`（仓库里，已加进 `.gitignore`），路径集中定义在 `lablib.CONFHASH`，`confhash` 和 `cleanup.py` 都引它。
复验跑的就是当初失败的那个场景：`save` → 删掉 `/tmp/clab` → 再 `check`，五项全部「未变」，退出码 0；`git status` 不会带上基线文件。

### 7. agent 行为：评审方只听 handoff 那句固定的话
`request.md` 里的额外要求（「findings 第一行照抄 token」「最后一行写 TODO」）会被忽略，把要求写硬了才照做。
不是 corral 的问题。lab 这边的教训：要验的东西得写进 handoff 送出的那句话里。

---

## 附：这轮测试确认没问题的部分

送话逐字送达（含多行、代码块、特殊字符、60KB 走文件）；常驻 agent + 叫醒脚本；人正在打字时送话被拒（8）；实例编号变了不送（`b_changed_refused`，真实误用场景下挡住了盲送）；双向临时委派；三个临时 agent 并发无串扰；三轮文件交接与复用；权限框 → blocked/unblocked；未交付判定；Esc 打断；忙时重试（7）；两个项目并行零串扰；沙箱拒绝（6）；重复启动（5）；协议不兼容（9）；50MB 事件文件后 `status` 中位数仍是 35ms（基线 34ms）。

一个值得记的对比（步骤 42）：同样按 Esc，

| | 判定 | Esc → 判定 | last_event |
|---|---|---|---|
| Claude Code | interrupted | **21.5 秒**（靠 20 秒静默超时兜底） | PostToolUse（Esc 不产生事件） |
| Codex | undelivered | **0.9 秒** | **Interrupt** |

有事件的 agent 能立刻判定，没有事件的只能等静默超时——差 24 倍。
