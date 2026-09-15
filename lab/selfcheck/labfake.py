"""自检用的假 agent：在 corral 仓库的 tests/fake_agents/fake_agent.py 上加「交接模式」。

收到的话里有 <目录>/request.md 时，读同目录的 fake-mode 文件决定这一轮怎么表现（没有这个文件就是 done）：
  done       1 秒后写 findings.md（抄 request.md 里带 TOKEN 的行、request.md 引用的 .md 文件的最后一行），最后一行 DONE
  nodone     同上，但最后一行是 TODO
  slow:<秒>  这么多秒后才写（DONE）
  ask        先弹「权限框」（等人按 1），按了之后写（DONE）
  hang       进入 working 后既不输出也不结束，不写
其他话照 corral 假 agent 的剧本（reply:…、slow:…、echo 等）。被 Esc / Ctrl-C 打断时不写。
"""
import importlib.util
import os
import re
import time

REQUEST_RE = re.compile(r"(/[^\s，。]+/request\.md)")
FINDINGS_RE = re.compile(r"(/[^\s，。]+/findings\.md)")
MD_RE = re.compile(r"(/[^\s，。`'\"]+\.md)")


def load_fake(corral_repo, flavor):
    path = os.path.join(corral_repo, "tests", "fake_agents", "fake_agent.py")
    spec = importlib.util.spec_from_file_location("fake_agent", path)
    mod = importlib.util.module_from_spec(spec)
    mod.FAKE_FLAVOR = flavor
    spec.loader.exec_module(mod)
    return mod


def findings_text(request, done):
    lines = ["# 假评审结果"]
    try:
        text = open(request, encoding="utf-8").read()
    except OSError:
        text = ""
    lines += [line for line in text.splitlines() if "TOKEN" in line]
    for ref in MD_RE.findall(text):
        if ref.endswith(("/request.md", "/findings.md")) or not os.path.exists(ref):
            continue
        tail = [line for line in open(ref, encoding="utf-8").read().splitlines() if line.strip()]
        if tail:
            lines.append(f"引用文件最后一行：{tail[-1]}")
    lines.append("DONE" if done else "TODO")
    return "\n".join(lines) + "\n"


def make_agent(base):
    class LabAgent(base.Agent):
        pending = None

        def submit(self, text):
            super().submit(text)
            req, out = REQUEST_RE.search(text), FINDINGS_RE.search(text)
            if not (req and out):
                return
            try:
                mode = open(os.path.join(os.path.dirname(req.group(1)), "fake-mode")).read().strip() or "done"
            except OSError:
                mode = "done"
            now = time.time()
            self.pending = (out.group(1), findings_text(req.group(1), mode != "nodone"))
            if mode in ("done", "nodone"):
                self.job = [(now + 1.0, ("stop", "findings 已写"))]
            elif mode.startswith("slow:"):
                self.job = [(now + float(mode[5:]), ("stop", "findings 已写"))]
            elif mode == "ask":
                self.job = [(now, ("fire", "PreToolUse", {"tool_name": "Write"})),
                            (now, ("fire", "PermissionRequest", {"tool_name": "Write"})),
                            (now, ("ask",))]
            elif mode == "hang":
                self.pending, self.job, self.spinning = None, [], False

        def run_job(self):
            now = time.time()
            if self.pending and any(t <= now and a[0] == "stop" for t, a in self.job):
                path, content = self.pending
                self.pending = None
                with open(path, "w", encoding="utf-8") as f:
                    f.write(content)
            super().run_job()

        def interrupt(self):
            self.pending = None
            super().interrupt()

        def ctrl_c(self):
            self.pending = None
            super().ctrl_c()

    return LabAgent


def main(corral_repo, flavor):
    if flavor.endswith("-nostart"):
        os.environ["FAKE_IGNORE_PROMPT"] = "1"
        flavor = flavor[:-len("-nostart")]
    base = load_fake(corral_repo, flavor)
    make_agent(base)().main()
