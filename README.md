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
> **"AI 给的结论我不敢信"** —— 这是每个安全研究员的共同痛点。本项目不替 AI 变聪明，而是**强制它把思考过程摊开给你看**：每一步扫描、每一行引用、每一次不确定，都写在证据链里。

## 🎯 它解决什么问题

普通 LLM 审查代码时会直接给你一段结论，你分不清它是真看懂了还是在编。这个技能把审查拆成**三步漏斗**，每一步都留痕：

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

> 每一步的笔记都实时写入 `reverse_notes.md`，最终结论绑定到 `audit_report.md`。**你看到的不是"一段分析"，是"一份可复盘的审查记录"。**

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

## ❓ 常见问题

<details>
<summary><b>Q：这和直接把代码丢给 ChatGPT 有什么区别？</b></summary>

<br/>

直接丢给 ChatGPT，它会跳过扫描和降维，直接根据表面特征给结论。这个技能强制 AI 先走完三阶漏斗，每一步都要写证据笔记——你能看到它"怎么想的"，而不只是"想出来什么"。
</details>

<details>
<summary><b>Q：支持哪些大模型？</b></summary>

<br/>

任何兼容 OpenAI Chat Completions 接口的模型都可以：GPT-4o、DeepSeek、通义千问、Kimi、豆包、本地 vLLM 部署等。通过 `OPENAI_BASE_URL` 环境变量切换端点。
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
- [x] **v1.1** — README 全面升级（横幅 / 徽章 / FAQ / 双语对等）、CI 跨平台矩阵、pathlib 重构
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
> **"I don't trust AI conclusions."** — that's a shared feeling among every security researcher. This project doesn't make AI smarter; it **forces it to show its work**: every scan, every line citation, every "I'm not sure" — written down in an evidence log.

## What it does

Instead of jumping straight to a conclusion, this skill forces the LLM through a **three-stage funnel**, leaving a paper trail at every step:

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

> Every stage is logged to `reverse_notes.md`; final findings land in `audit_report.md`. What you get back isn't "an analysis" — it's "a review log you can audit."

## Core capabilities

| Capability | What it does |
| :--- | :--- |
| 🪣 **Three-stage funnel** | Static → deobfuscation → deduction, no skipping |
| 🔍 **Evidence-first** | Every claim cites file + line; "uncertain" is valid |
| 🧠 **Anti-hallucination log** | Notes appended over time, context preserved across turns |
| 🛠 **Tool routing** | Guides Playwright MCP / webcrack / Ghidra / jadx |
| 🌐 **Any platform** | Claude Code, Cursor, ChatGPT, Kimi, Doubao, OpenAI API |

## Quick start

```bash
# Option 1: as a native agent skill
git clone https://github.com/Trace520/ultimate-security-audit.git ~/.claude/skills/ultimate-security-audit

# Option 2: Python
pip install openai
export OPENAI_API_KEY=sk-xxxx
python api/openai_compatible.py

# Option 3: Docker (with Playwright runtime)
docker build -t ultimate-security-audit .
docker run --rm -it ultimate-security-audit
```

## FAQ

<details>
<summary><b>Q: How is this different from just pasting code into ChatGPT?</b></summary>

<br/>

Pasting code directly lets the model jump to conclusions based on surface features. This skill forces it through the full three-stage funnel, writing evidence notes at each step — you see *how* it thinks, not just *what* it concluded.
</details>

<details>
<summary><b>Q: Which models are supported?</b></summary>

<br/>
Any OpenAI Chat Completions-compatible model: GPT-4o, DeepSeek, Qwen, Kimi, Doubao, self-hosted vLLM, etc. Switch endpoints via `OPENAI_BASE_URL`.
</details>

<details>
<summary><b>Q: Can I use this to audit my clients' systems?</b></summary>

<br/>
Yes, but only with explicit written authorization. See [DISCLAIMER.md](DISCLAIMER.md) and the additional terms in [LICENSE](LICENSE). Unauthorized testing is illegal.
</details>

## Roadmap

- [x] **v1.0.0** — Initial release: three-stage funnel, multi-platform, CI, Docker, community health files
- [x] **v1.1** — README overhaul (hero / badges / FAQ / bilingual parity), cross-platform CI matrix, pathlib refactor
- [ ] **v1.2** — Targeted flows for iOS / Android client samples
- [ ] **v1.3** — Export reports in both Markdown and HTML
- [ ] **v2.0** — Multi-model parallel review (GPT / Claude / DeepSeek consensus)

## Disclaimer

> [!WARNING]
> This project is for legitimate security auditing of your own assets, open-source code analysis, and authorized engagements only. You must have explicit written permission before testing any third-party system. See [DISCLAIMER.md](DISCLAIMER.md).

---

<div align="center">

**[📢 Release v1.1](https://github.com/Trace520/ultimate-security-audit/releases/tag/v1.1)** ·
**[🐛 Report a bug](https://github.com/Trace520/ultimate-security-audit/issues/new?template=bug_report.md)** ·
**[✨ Request a feature](https://github.com/Trace520/ultimate-security-audit/issues/new?template=feature_request.md)**

<sub>Built with care · MIT licensed · Not affiliated with any listed tool vendor</sub>

</div>
