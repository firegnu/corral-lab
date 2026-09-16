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

### 2. 输入框里有没提交的草稿时，`send` 被误报成没送到

**现象**
人在接入窗口的输入框里留了一段没提交的文字，这时 `corral send`，送进去的文字**接在草稿后面一起提交**。agent 实际收到了拼接后的内容并照做了，但 corral 因为回读的文字和送出的对不上，报 `not_delivered`（**退出码 3**）。

**后果**
调用方以为没送到，重试一次就送了第二遍。

**复现**（步骤 12 B 段）
在接入窗口里打几个字**不要提交**，静置 30 秒（躲开 human_active 的静默窗口），然后 `corral send`。

**可选的处理方向**（都没定，需要讨论）
- 文档写明这是退出码 3 的常见原因，提示调用方接入去看，不要盲目重试；
- 或者送之前清空输入框——但这会毁掉人正在写的草稿，代价不小。

---

## 二、要观察，也可能只是文档

### 3. Codex 正常退出的收尾时间波动大

`corral stop` 对 Codex 是连按两次 Ctrl-C，等它自己退出，超时才升级到 SIGTERM。实测：

| 场合 | 用时 |
|---|---|
| M8 冒烟 | 7.6 秒 |
| 步骤 03 | 13.1 秒，正常退出 |
| 步骤 02（跑过三轮之后） | 超过 20 秒，被升级到 SIGTERM（`exit_code: -15`） |

会话跑得越久似乎收尾越慢。可以考虑把 Codex 的等待从 20 秒放宽，或者先发一次 Ctrl-C 看反应再决定。

### 4. `corral keys` 之后不能马上 `send`

`corral keys` 打进去的按键会被钩子记成「人在打字」，紧接着的 `corral send` 被退回 **8（human_active）**，要等静默窗口过去才能送。

**大概率是设计如此**——步骤 42 正是靠这一点用 `corral keys <名字> esc` 模拟人手按 Esc，走的确实是同一条路，说明检测是对的。但写脚本的人会踩：`keys` 之后要按 8 重试，不能假设马上能 `send`。建议文档里写一句。

---

## 三、不归 corral 管（记在这里只为完整）

### 5. lab 脚本：`confhash check` 误报　——　**已修**
去掉 Codex 信任段时连段前的空行一起删了，导致「只多了信任记录」被报成「变了」。

### 6. lab 脚本：confhash 基线放在 `/tmp/clab` 里，被 cleanup 自己删掉　——　**待改**
`cleanup.py` 第 6 步删 `/tmp/clab`，而基线就存在 `/tmp/clab/confhash.json`，于是第 2 步「手动删信任记录」之后没法再用 confhash 复验。
改法：基线存到 `/tmp/clab` 外面，或者把「删信任记录」挪到删 `/tmp/clab` 之前。

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
