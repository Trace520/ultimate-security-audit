<div align="center">

<img src="https://aka.doubaocdn.com/s/eopsS0yVb4" alt="Ultimate Security Audit" width="100%" />

# 🛡️ Ultimate Security Audit

**结构化代码 & 架构审查的 AI Agent 技能**

[![CI](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v1.1-blue?logo=github&style=flat-square)](https://github.com/Trace520/ultimate-security-audit/releases/tag/v1.1)
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
> 它不是自动化扫描器（不是 Semgrep/CodeQL），也不是漏洞利用生成器。它是一套**流程规范**——强制 AI 按固定三步走，每步把过程写进本地文件，让输出从"一段话说"变成"一份可复盘的审查记录"。

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
| **① 静态发现** | 读源码/抓包，列入口点（路由、导出函数、事件监听）、外部调用（fetch/XHR/socket）、可疑模式（eval、atob、硬编码密钥） | `reverse_notes.md` 的"发现清单"段 |
| **② 中间层降维** | 对混淆代码反混淆（webcrack）、对二进制反编译（jadx/Ghidra）、对前端流量用 Playwright MCP 拦截，还原关键函数真实逻辑 | `reverse_notes.md` 的"还原"段 |
| **③ 深度推演** | 从入口追数据流到 sink，判断可达性，构造最简 PoC，按严重度分级 | `audit_report.md` |

**铁律：**
- 每个结论必须引用具体文件 + 行号；找不到证据就写"不确定"，不准编。
- 中间发现按时间追加到 `reverse_notes.md`，多轮对话不丢上下文。
- 需要工具时（抓包、反编译）必须显式调用，不准凭想象猜。

## 📥 输入 / 输出契约

**你给它什么：**
- 一段代码片段（直接贴）
- 一个本地文件路径或目录
- 一个 URL（引导你用 Playwright MCP 抓）
- 一个样本二进制（引导 jadx / Ghidra）

**它给你什么：**
- `reverse_notes.md` — 全过程证据链（按时间倒序，每步带文件+行号）
- `audit_report.md` — 最终报告：概述 → 发现列表（按严重度）→ 每个发现的证据链 → 复现步骤 → 建议修复

示例见 [`examples/`](examples/)：
- [`sample_code.js`](examples/sample_code.js) — 带 XOR 混淆的演示样本
- [`reverse_notes.md`](examples/reverse_notes.md) — 对该样本的证据链
- [`audit_report.md`](examples/audit_report.md) — 最终报告

## ✨ 核心能力

| 能力 | 说明 |
| :--- | :--- |
| 🪣 **三阶漏斗模型** | 静态 → 降维 → 推演，不跳步、不越级下结论 |
| 🔍 **证据溯源** | 所有结论必须绑定文件 + 行号；信息不足直接说"不确定" |
| 🧠 **防幻觉记忆** | 笔记按时间倒序累积，多轮对话不丢上下文 |
| 🛠 **工具链路由** | 根据目标自动引导 Playwright MCP / webcrack / Ghidra / jadx |
| 🌐 **全平台兼容** | Claude Code / Cursor / ChatGPT / Kimi / 豆包 / OpenAI API |

## 🚀 全平台支持矩阵

| 平台类型 | 使用方式 | 对应文件 |
| :--- | :--- | :--- |
| **Claude Code / Cursor 等 Agent** | 原生技能加载（放入 skills 目录） | `skill/SKILL.md` |
| **ChatGPT / Kimi / 豆包 网页版** | 复制粘贴作为系统提示词 | `prompt/system_prompt.txt` |
| **Python / 自动化脚本** | 作为 System Message 注入 | `api/openai_compatible.py` |

## 🚦 快速开始

> [!TIP]
> **前置要求**：Python 3.10+；Agent 技能加载需要客户端支持本地技能目录（Claude Code / Cursor）。

**方式 A：作为 Agent 技能**
```bash
git clone https://github.com/Trace520/ultimate-security-audit.git ~/.claude/skills/ultimate-security-audit
```
然后在对话里直接说："审计这个文件 xxx.js"，AI 会自动走三步流程。

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

## 🧰 技术栈

<p align="center">
  <img src="https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-OpenAI%20API-412991?logo=openai&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-Playwright-2EAD33?logo=playwright&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-Ghidra-2C2D72?logo=gnu%20emacs&logoColor=white&style=flat-square" />
  <img src="https://img.shields.io/badge/-jadx-FF6B00?style=flat-square" />
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

直接丢给 ChatGPT，它会跳过扫描和降维，根据表面特征直接给结论。这个技能强制 AI 先走三阶漏斗，每步写证据笔记——你能看到它"怎么想的"，而不只是"想出来什么"。
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
│   └── SKILL.md             # 原生 Agent 技能定义
├── prompt/
│   └── system_prompt.txt    # 网页端系统提示词
├── api/
│   └── openai_compatible.py # OpenAI 兼容 Python 客户端
├── docs/
│   └── toolchain.md         # Playwright / webcrack / Ghidra / jadx
├── examples/
│   ├── sample_code.js       # 演示样本
│   ├── reverse_notes.md     # 证据链笔记示例
│   └── audit_report.md      # 标准审计报告示例
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/ci.yml
```

## 🗺 路线图

- [x] **v1.0.0** — 初始发布：三阶漏斗、全平台支持、CI、Docker、社区健康文件
- [x] **v1.1** — README 升级为实用规格（工作流表 + 输入/输出契约）、CI 跨平台矩阵、pathlib 重构
- [ ] **v1.2** — 新增对 iOS / Android 客户端样本的专项分析流程
- [ ] **v1.3** — 支持导出 Markdown / HTML 双格式审计报告
- [ ] **v2.0** — 多模型并行审查（GPT / Claude / DeepSeek 合并结论）

## ⚠️ 免责声明

> [!WARNING]
> 本项目**仅用于**合法的企业级软件安全审计、自有资产测试、开源项目分析及已授权的安全研究。使用者需确保对审查目标拥有合法授权；**严禁**用于任何未授权的逆向、破解或攻击行为。详见 [DISCLAIMER.md](DISCLAIMER.md)。

## 📚 更多文档

- [底层工具链配置指南](docs/toolchain.md)
- [示例：对演示样本的审计输出](examples/audit_report.md)
- [安全策略（漏洞披露）](SECURITY.md)
- [贡献指南](CONTRIBUTING.md)
- [行为准则](CODE_OF_CONDUCT.md)

---

<a id="-english"></a>

## 🌐 English

> [!NOTE]
> This is not an automated scanner (not Semgrep/CodeQL) and not an exploit generator. It's a **process spec**: forces the LLM through three fixed stages, writes every step to a local file, turning output from "a paragraph" into "an auditable review log."

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

## The three stages (what the agent actually does)

| Stage | Agent action | Output |
| :--- | :--- | :--- |
| **① Static** | List entry points (routes, exports, event listeners), external calls (fetch/XHR/socket), suspicious patterns (eval, atob, hardcoded keys) | `reverse_notes.md` "findings" section |
| **② Deobfuscation** | webcrack for JS, jadx/Ghidra for binaries, Playwright MCP for web traffic — restore real logic | `reverse_notes.md` "restored" section |
| **③ Deduction** | Trace entry → sink, judge reachability, build minimal PoC, severity-rate | `audit_report.md` |

**Iron rules:**
- Every claim must cite file + line; write "uncertain" when evidence is missing — never invent.
- Append findings chronologically to `reverse_notes.md`; context survives multi-turn.
- Call tools explicitly when needed — don't guess.

## Input / output contract

**You give it:** a code snippet, a local path, a URL, or a binary sample.

**It gives you:**
- `reverse_notes.md` — full evidence log with file + line citations
- `audit_report.md` — final report: summary → findings (by severity) → evidence chain per finding → repro steps → remediation

See [`examples/`](examples/) for a worked sample.

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
```

## Roadmap

- [x] **v1.0.0** — Initial release
- [x] **v1.1** — README as practical spec (workflow table + I/O contract), cross-platform CI matrix, pathlib refactor
- [ ] **v1.2** — iOS / Android client sample flows
- [ ] **v1.3** — Markdown / HTML report export
- [ ] **v2.0** — Multi-model parallel review (GPT / Claude / DeepSeek consensus)

## Disclaimer

> [!WARNING]
> For legitimate auditing of your own assets, open-source code analysis, and authorized engagements only. You must have explicit written permission before testing any third-party system. See [DISCLAIMER.md](DISCLAIMER.md).

---

<div align="center">

**[📢 Release v1.1](https://github.com/Trace520/ultimate-security-audit/releases/tag/v1.1)** ·
**[🐛 Report a bug](https://github.com/Trace520/ultimate-security-audit/issues/new?template=bug_report.md)** ·
**[✨ Request a feature](https://github.com/Trace520/ultimate-security-audit/issues/new?template=feature_request.md)**

<sub>Built with care · MIT licensed · Not affiliated with any listed tool vendor</sub>

</div>
