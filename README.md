<div align="center">

<img src="https://aka.doubaocdn.com/s/eopsS0yVb4" alt="Ultimate Security Audit" width="100%" />

# 🛡️ Ultimate Security Audit

**工业级代码 & 架构安全审计 AI Agent 技能（V2.3.0）**

[![CI](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v2.0-blue?logo=github&style=flat-square)](https://github.com/Trace520/ultimate-security-audit/releases/tag/v2.0)
[![License](https://img.shields.io/badge/license-MIT%20%2B%20Security%20Terms-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&style=flat-square)](api/openai_compatible.py)
[![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker&style=flat-square)](Dockerfile)
[![stars](https://img.shields.io/github/stars/Trace520/ultimate-security-audit?style=flat-square)](https://github.com/Trace520/ultimate-security-audit/stargazers)
[![forks](https://img.shields.io/github/forks/Trace520/ultimate-security-audit?style=flat-square)](https://github.com/Trace520/ultimate-security-audit/network/members)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

**[English](#-english) · [简体中文](#-中文)**

</div>

---

<a id="-中文"></a>

> [!NOTE]
> 它不是自动化扫描器（不是 Semgrep/CodeQL），也不是漏洞利用生成器。它是一套**工业级流程规范**——强制 AI 按三阶漏斗推进、把授权门控与证据链落盘到本地文件、下结论前先做证据自检，并在 CI 流水线里以审批编号 + 目标清单做无人值守授权。输出从"一段话说"变成"一份可复盘、可审计的六段式报告"。

## 🎯 它到底做什么

你把一段代码、一个 URL、或一个二进制样本丢给 AI，普通做法是它直接给结论，你分不清它是真看懂了还是在编。这个技能强制 AI 按**三阶漏斗**推进，每步留证据：

```
  🔍 ① 静态发现
  扫描入口 · 提取 API 路径 · 识别可疑模式
        │
        ▼
  🔬 ② 中间层降维
  反混淆 · 反编译 · 流量拦截 · 还原关键函数
        │
        ▼
  🧠 ③ 深度推演
  数据流追踪 · 构造 PoC · 输出标准报告
```

## 🔬 三步工作流（Agent 实际在做什么）

| 阶段 | AI 实际动作 | 产出落点 |
| :--- | :--- | :--- |
| **① 静态发现** | 读源码/抓包，列入口点（路由、导出函数、事件监听）、外部调用（fetch/XHR/socket）、可疑模式（eval、atob、硬编码密钥） | `audit_notes.md` 的"发现清单"段 |
| **② 中间层降维** | 对混淆代码反混淆（webcrack）、对二进制反编译（jadx/Ghidra）、对前端流量用 Playwright MCP 拦截，还原关键函数真实逻辑 | `audit_notes.md` 的"还原"段 |
| **③ 深度推演** | 从入口追数据流到 sink，判断可达性，构造最简 PoC，按严重度分级 | 六段式审计报告 |

**铁律：**
- 每个结论必须引用具体文件 + 行号；找不到证据就写 `[证据缺失] 需进一步侦察`，不准编。
- 中间发现按时间追加到 `audit_notes.md`（模板见 `skill/assets/audit_notes.template.md`），多轮对话不丢上下文。
- 需要工具时（抓包、反编译）必须显式调用，不准凭想象猜；引擎缺失时退化为纯静态并标注降级原因。

## 🔐 V2.0 新增：双授权模式

| 模式 | 触发条件 | 授权依据 | 行为 |
| :--- | :--- | :--- | :--- |
| **交互模式**（默认） | 对话中直接发起审计 | 当前会话声明 / 审批编号 / 书面授权 | 门控确认后走三阶漏斗 |
| **CI 流水线模式** | `AUTHORIZATION_MODE=CI_PIPELINE` | `AUDIT_APPROVAL_ID` + `AUDIT_TARGETS` + CI 上下文交叉核对 | 三态判定：**EXECUTE** 静默执行 / **BLOCKED** 缺字段即停 / **DEGRADED** 仅静态侦察 |

> **模式开关本身不是授权**。任何进程都能设置环境变量，技能只认审批编号与目标清单两个可核对字段，缺一项即中止。详见 [`skill/references/ci-pipeline-mode.md`](skill/references/ci-pipeline-mode.md)。

## 📥 输入 / 输出契约

**你给它什么：**
- 一段代码片段（直接贴）
- 一个本地文件路径或目录
- 一个 URL（引导你用 Playwright MCP 抓）
- 一个样本二进制（引导 jadx / Ghidra）

**它给你什么（六段式报告）：**
1. 📌 审计结论（一句话定性 + 最高风险等级）
2. 🗺️ 逻辑流图（Mermaid 状态机）
3. 🔗 证据溯源（`[STATIC]` / `[DYNAMIC]` / `[REVERSE]` / `[HTTP]`，每条带位置）
4. 缺陷清单（严重度 / 触发条件 / 影响面 / 置信度）
5. 🛠️ 最小验证脚本（PoC，不含破坏性载荷，凭据走环境变量）
6. 修复建议与复测（方向 + 验收标准）

**LLM/Agent 目标才加合规映射**：仅当目标本身是 LLM 应用（prompt / tool schema / 向量库 / openai·langchain·mcp 依赖）时，缺陷表加「合规项」列，标签从 OWASP LLM Top 10 2025 固定表取（LLM01 注入 / LLM02 敏感泄露 / LLM06 过度代理 / LLM07 系统提示词泄露 等），编号钉死年份，每个标签必须能指回一条证据。非 LLM 目标写 `[compliance: N/A — 非 LLM 目标]`，不硬套。

## ✨ 核心能力

| 能力 | 说明 |
| :--- | :--- |
| 🪣 **三阶漏斗模型** | 静态 → 降维 → 推演，不跳步、不越级下结论 |
| 🚦 **双授权模式** | 交互确认 + CI 流水线审批绑定，缺字段 fail-closed |
| 🔍 **证据自检（强制）** | 下结论前先读 `audit_notes.md`，无证据标 `[证据缺失]` |
| 📋 **六段式报告** | 结论 / 流图 / 证据 / 缺陷 / PoC / 修复，评审友好 |
| 🛠 **工具链路由** | webcrack / Playwright MCP / Ghidra / jadx / leanrea，按目标特征触发 |
| ⚖️ **条件式合规映射** | 仅 LLM 目标加 OWASP LLM Top 10 2025 标签，编号不混用 |
| 🌐 **全平台兼容** | Claude Code / Cursor / ChatGPT / Kimi / 豆包 / OpenAI API |

> 一页速查（三个相关产物能干什么）见 [`docs/CAPABILITIES.md`](docs/CAPABILITIES.md)。

## 🚀 全平台支持矩阵

| 平台类型 | 使用方式 | 对应文件 |
| :--- | :--- | :--- |
| **Claude Code / Cursor 等 Agent** | 原生技能加载（放入 skills 目录） | [`skill/SKILL.md`](skill/SKILL.md) + [`skill/references/`](skill/references/) + [`skill/assets/`](skill/assets/) |
| **ChatGPT / Kimi / 豆包 网页版** | 复制粘贴作为系统提示词 | `prompt/system_prompt.txt` |
| **Python / 自动化脚本** | 作为 System Message 注入 | `api/openai_compatible.py` |

## 🚦 快速开始

> [!TIP]
> **前置要求**：Python 3.10+；Agent 技能加载需要客户端支持本地技能目录（Claude Code / Cursor）。

**方式 A：作为 Agent 技能**
```bash
git clone https://github.com/Trace520/ultimate-security-audit.git ~/.claude/skills/ultimate-security-audit
```
然后在对话里直接说："审计这个文件 xxx.js"，AI 会自动走三步流程并先确认授权。

**方式 B：Python 直跑**
```bash
git clone https://github.com/Trace520/ultimate-security-audit.git
cd ultimate-security-audit
pip install openai
export OPENAI_API_KEY=sk-xxxx        # Windows: set OPENAI_API_KEY=sk-xxxx
python api/openai_compatible.py
```

**方式 C：Docker（自带 Playwright 运行时）**
```bash
docker build -t ultimate-security-audit .
docker run --rm -it ultimate-security-audit
```

**方式 D：CI 流水线无人值守**
```yaml
env:
  AUTHORIZATION_MODE: CI_PIPELINE
  AUDIT_APPROVAL_ID: ${{ vars.AUDIT_APPROVAL_ID }}
  AUDIT_TARGETS: "src/;dist/app.asar"
run: python scripts/run_audit.py --targets "$AUDIT_TARGETS"
```

## 🧰 技术栈

<p align="center">
  <img src="https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-OpenAI%20API-412991?logo=openai&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-Playwright-2EAD33?logo=playwright&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-Ghidra-2C2D72?logo=gnu%20emacs&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-jadx-FF6B00?style=flat-square" />
  <img src="https://img.shields.io/badge/-OWASP%20LLM%20Top%2010%202025-123?style=flat-square" />
</p>

## 🔌 外部工具依赖（按需安装）

技能本身不强制装这些，但 AI 会在需要时引导调用：

- **Playwright MCP** — 前端抓包 / 动态分析
- **webcrack** — JS 反混淆（`npm i -g webcrack`）
- **jadx** — Android APK 反编译
- **Ghidra** — 原生二进制逆向

详见 [`docs/toolchain.md`](docs/toolchain.md)。

## ❓ 常见问题

<details>
<summary><b>Q：这和直接把代码丢给 ChatGPT 有什么区别？</b></summary>

<br/>

直接丢给 ChatGPT，它会跳过扫描和降维，根据表面特征直接给结论。这个技能强制 AI 先走三阶漏斗、先确认授权、每步写证据笔记——你能看到它"怎么想的"，而不只是"想出来什么"。
</details>

<details>
<summary><b>Q：CI 模式怎么授权？我设了 AUTHORIZATION_MODE 为什么还被 BLOCKED？</b></summary>

<br/>

`AUTHORIZATION_MODE=CI_PIPELINE` 只说明运行形态，不是授权。必须同时注入 `AUDIT_APPROVAL_ID`（审批编号）和 `AUDIT_TARGETS`（允许审计的路径前缀），且待审计对象必须全部落在目标清单内。缺任一项即 BLOCKED；有审批但无 CI 上下文（非 GitHub/GitLab/Jenkins 环境）则降为 DEGRADED，只做静态侦察。
</details>

<details>
<summary><b>Q：支持哪些大模型？</b></summary>

<br/>

任何兼容 OpenAI Chat Completions 接口的模型：GPT-4o、DeepSeek、通义千问、Kimi、豆包、本地 vLLM 部署等。通过 `OPENAI_BASE_URL` 环境变量切换端点。
</details>

<details>
<summary><b>Q：能用来审计我客户的系统吗？</b></summary>

<br/>

可以，但**必须**先获得客户的书面授权。详见 [DISCLAIMER.md](DISCLAIMER.md) 和 [LICENSE](LICENSE) 中的安全工具附加条款。未经授权的测试属于违法行为。
</details>

## 📂 仓库结构

```text
ultimate-security-audit/
├── README.md
├── LICENSE                  # MIT + 安全工具附加条款
├── Dockerfile
├── skill/
│   ├── SKILL.md             # 主控指令（V2.3.0，渐进披露）
│   ├── references/          # 按需加载的执行细则
│   │   ├── audit-workflow.md
│   │   ├── audit-report.md
│   │   ├── authorization-and-handling.md
│   │   └── ci-pipeline-mode.md
│   └── assets/
│       └── audit_notes.template.md
├── prompt/
│   └── system_prompt.txt    # 网页端系统提示词（V2.0 对齐）
├── api/
│   └── openai_compatible.py # OpenAI 兼容 Python 客户端
├── docs/
│   ├── toolchain.md         # Playwright / webcrack / Ghidra / jadx
│   └── CAPABILITIES.md      # 一页速查：三个相关产物的能力边界
├── examples/
│   ├── sample_code.js       # 演示样本
│   ├── audit_notes.md       # 证据链笔记示例（已填好）
│   └── audit_report.md      # 六段式审计报告示例
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/ci.yml
```

## 🗺 路线图

- [x] **v1.0.0** — 初始发布：三阶漏斗、全平台支持、CI、Docker、社区健康文件
- [x] **v1.1** — README 升级为实用规格（工作流表 + 输入/输出契约）、CI 跨平台矩阵、pathlib 重构
- [x] **v2.0** — 工业级升级：双授权模式（交互 + CI 流水线）、强制证据自检、六段式报告、OWASP LLM Top 10 2025 条件映射、references/ + assets/ 渐进披露结构
- [ ] **v2.1** — iOS / Android 客户端样本专项流程
- [ ] **v2.2** — Markdown / HTML 双格式报告导出

## ⚠️ 免责声明

> [!WARNING]
> 本项目**仅用于**合法的企业级软件安全审计、自有资产测试、开源项目分析及已授权的安全研究。使用者需确保对审查目标拥有合法授权；**严禁**用于任何未授权的逆向、破解或攻击行为。详见 [DISCLAIMER.md](DISCLAIMER.md)。

## 📚 更多文档

- [技能主控指令（V2.3.0）](skill/SKILL.md)
- [CI 流水线模式契约](skill/references/ci-pipeline-mode.md)
- [授权边界与数据处理](skill/references/authorization-and-handling.md)
- [审计报告规范](skill/references/audit-report.md)
- [一页速查：三个产物能力边界](docs/CAPABILITIES.md)
- [底层工具链配置指南](docs/toolchain.md)
- [安全策略（漏洞披露）](SECURITY.md)
- [贡献指南](CONTRIBUTING.md)

---

<a id="-english"></a>

## 🌐 English

> [!NOTE]
> This is not an automated scanner (not Semgrep/CodeQL) and not an exploit generator. It's an **industrial-grade process spec**: forces the LLM through three fixed stages, gates every engagement on explicit authorization, persists an evidence chain to local files, self-checks evidence before drawing conclusions, and supports unattended CI-pipeline runs bound to an approval ID + explicit target list. Output is an auditable six-section report.

## What it actually does

Instead of jumping straight to a conclusion, the skill forces the LLM through a **three-stage funnel** with a paper trail at each step:

```
  🔍 ① Static discovery
     Scan entry points · Extract API paths · Flag suspicious patterns
        │
        ▼
  🔬 ② Intermediate deobfuscation
     Deobfuscate · Reverse · Intercept traffic · Restore key functions
        │
        ▼
  🧠 ③ Deep deduction
     Trace data flow · Build PoC · Produce standard report
```

## V2.0: Dual authorization

| Mode | Trigger | Authorization basis | Behavior |
| :--- | :--- | :--- | :--- |
| **Interactive** (default) | Direct chat request | Session statement / approval ID / written consent | Gate then run the funnel |
| **CI pipeline** | `AUTHORIZATION_MODE=CI_PIPELINE` | `AUDIT_APPROVAL_ID` + `AUDIT_TARGETS` + CI context | Three-state: **EXECUTE** / **BLOCKED** / **DEGRADED** |

>The mode switch alone is not authorization. The skill only honors two verifiable fields — approval ID and target list — and fails closed when either is missing.

## Input / output contract

**You give it:** a code snippet, a local path, a URL, or a binary sample.

**It gives you a six-section report:** conclusion → Mermaid flow → evidence (`[STATIC]`/`[DYNAMIC]`/`[REVERSE]`/`[HTTP]`) → findings by severity → minimal non-destructive PoC → remediation with acceptance criteria.

OWASP LLM Top 10 2025 mapping is **conditional**: only when the target is itself an LLM/Agent app (prompt, tool schema, vector store, openai/langchain/mcp dependency) does the findings table get a compliance column. Each tag must trace back to one piece of evidence; year-pinned numbers are required (2025 ≠ 2023). Non-LLM targets write `[compliance: N/A]`.

## Quick start

```bash
# Option A: native agent skill
git clone https://github.com/Trace520/ultimate-security-audit.git ~/.claude/skills/ultimate-security-audit

# Option B: Python
pip install openai
export OPENAI_API_KEY=sk-xxxx
python api/openai_compatible.py

# Option C: Docker (with Playwright)
docker build -t ultimate-security-audit .
docker run --rm -it ultimate-security-audit

# Option D: CI (unattended)
# AUTHORIZATION_MODE=CI_PIPELINE, AUDIT_APPROVAL_ID, AUDIT_TARGETS required
```

## Roadmap

- [x] **v1.0.0** — Initial release
- [x] **v1.1** — README as practical spec, cross-platform CI matrix, pathlib refactor
- [x] **v2.0** — Industrial upgrade: dual auth (interactive + CI pipeline), forced evidence self-check, six-section report, conditional OWASP LLM 2025 mapping, progressive-disclosure references/assets
- [ ] **v2.1** — iOS / Android client sample flows
- [ ] **v2.2** — Markdown / HTML dual-format report export

## Disclaimer

> [!WARNING]
> For legitimate auditing of your own assets, open-source code analysis, and authorized engagements only. You must have explicit written permission before testing any third-party system. See [DISCLAIMER.md](DISCLAIMER.md).

---

<div align="center">

**[📢 Release v2.0](https://github.com/Trace520/ultimate-security-audit/releases/tag/v2.0)** ·
**[🐛 Report a bug](https://github.com/Trace520/ultimate-security-audit/issues/new?template=bug_report.md)** ·
**[✨ Request a feature](https://github.com/Trace520/ultimate-security-audit/issues/new?template=feature_request.md)**

<sub>Built with care · MIT licensed · Not affiliated with any listed tool vendor</sub>

</div>
