<div align="center">

<img src="https://aka.doubaocdn.com/s/pYlBq9mxGd" alt="Ultimate Security Audit" width="100%" />

# 🛡️ Ultimate Security Audit

**结构化代码 & 架构审查的 AI Agent 技能**

[![CI](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v1.02-blue?logo=github&style=flat-square)](https://github.com/Trace520/ultimate-security-audit/releases/tag/v1.02)
[![License](https://img.shields.io/badge/license-MIT%20%2B%20Security%20Terms-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&style=flat-square)](api/openai_compatible.py)
[![Docker](https://img.shields.io/badge/docker-ready-blue?logo=docker&style=flat-square)](Dockerfile)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

**[English](#-english) · [简体中文](#-中文)**

</div>

---

<a id="-中文"></a>

## 🎯 这是什么

一个可移植的 AI Agent 技能，把任意大模型变成**结构化的代码与架构审查员**。它不直接下结论，而是强制走三阶漏斗、写证据链、引用具体行号——输出可审计，不可"AI 味"。

> [!NOTE]
> **核心区别**：普通 LLM 会直接给结论；这个技能强制 AI 先扫描、再降维、最后推演，每一步都留下证据笔记。你看到的不是"一段分析"，而是"一份可复盘的审查记录"。

## ✨ 核心亮点

| 能力 | 解决什么问题 |
| :--- | :--- |
| 🪣 **三阶漏斗模型** | 静态发现 → 中间层降维 → 深度推演，不跳步 |
| 🔍 **证据溯源** | 所有结论必须绑定文件 + 行号；信息不足直接说"不确定" |
| 🧠 **防幻觉记忆** | 审查笔记实时写入 `reverse_notes.md`，按时间倒序累积 |
| 🛠 **工具链路由** | 自动引导 Playwright MCP / webcrack / Ghidra / jadx |
| 🌐 **全平台兼容** | Claude Code / Cursor / ChatGPT / Kimi / 豆包 / OpenAI API |

## 🪣 工作流

```text
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│  ① 静态发现          │ -> │  ② 中间层降维        │ -> │  ③ 深度推演          │
│                     │    │                     │    │                     │
│  · 扫描入口点        │    │  · 反混淆 / 反编译   │    │  · 数据流追踪       │
│  · 提取 API 路径     │    │  · 还原关键函数      │    │  · 构造 PoC          │
│  · 识别可疑模式      │    │  · 流量拦截 / HAR   │    │  · 输出标准报告     │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
           │                          │                          │
           └──────────────┬───────────┴──────────────┬──────────────┘
                          ▼                            ▼
                  📝 reverse_notes.md（证据链）   📄 audit_report.md（结论）
```

## 🚀 全平台支持矩阵

| 平台类型 | 使用方式 | 对应文件 |
| :--- | :--- | :--- |
| **Claude Code / Cursor / 其他 Agent 运行时** | 原生技能加载（放入 skills 目录） | `skill/SKILL.md` |
| **ChatGPT / Kimi / 豆包 网页版** | 复制粘贴作为系统提示词 | `prompt/system_prompt.txt` |
| **Python / 自动化脚本** | 作为 System Message 注入 | `api/openai_compatible.py` |

## 🚦 快速开始

> [!TIP]
> **前置要求**：Python 3.10+；如需 Agent 技能加载，客户端需支持本地技能目录（Claude Code / Cursor）。

**方式 A：克隆至 Agent 技能目录**

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

<p>
  <img src="https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/-OpenAI%20API-412991?logo=openai&logoColor=white" />
  <img src="https://img.shields.io/badge/-Playwright-2EAD33?logo=playwright&logoColor=white" />
  <img src="https://img.shields.io/badge/-Docker-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/-GitHub%20Actions-2088FF?logo=githubactions&logoColor=white" />
  <img src="https://img.shields.io/badge/-Ghidra-2C2D72?logo=gnu%20emacs&logoColor=white" />
</p>

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
│   ├── banner.png           # 项目横幅
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

- [x] v1.02 — 初始发布：三阶漏斗、全平台支持、CI、Docker、社区健康文件
- [ ] v1.1 — 新增对 iOS / Android 客户端样本的专项分析流程
- [ ] v1.2 — 支持导出 Markdown / HTML 双格式审计报告
- [ ] v2.0 — 多模型并行审查（同时跑 GPT / Claude / DeepSeek 并合并结论）

## ⚠️ 免责声明

> [!WARNING]
> 本项目**仅用于**合法的企业级软件安全审计、自有资产测试、开源项目分析及已授权的安全研究。使用者需确保对审查目标拥有合法授权；**严禁**用于任何未授权的逆向、破解或攻击行为。详见 [DISCLAIMER.md](DISCLAIMER.md) 与 [LICENSE](LICENSE) 中的安全工具附加条款。

## 📚 更多文档

- [底层工具链配置指南](docs/toolchain.md)
- [示例：对演示样本的审计输出](examples/audit_report.md)
- [安全策略（漏洞披露）](SECURITY.md)
- [贡献指南](CONTRIBUTING.md)
- [行为准则](CODE_OF_CONDUCT.md)

---

<a id="-english"></a>

## 🌐 English

### What is this?

A portable AI Agent skill that turns any LLM into a **structured code & architecture reviewer**. Instead of jumping to conclusions, it enforces a three-stage funnel, writes an evidence trail, and cites specific file/line references—output is auditable, not hallucinated.

> [!NOTE]
> **The difference**: vanilla LLMs hand you a conclusion. This skill forces the model to scan, deobfuscate, then reason—leaving a paper trail at every step. What you get back isn't "an analysis," it's "a review log you can audit."

### Core capabilities

| Capability | Problem solved |
| :--- | :--- |
| 🪣 **Three-stage funnel** | Static discovery → intermediate deobfuscation → deep deduction, no skipping |
| 🔍 **Evidence-first** | Every claim must cite a file and line; "uncertain" is a valid answer |
| 🧠 **Anti-hallucination log** | Review notes appended to `reverse_notes.md` in real time |
| 🛠 **Tool routing** | Guides Playwright MCP / webcrack / Ghidra / jadx based on target type |
| 🌐 **Any platform** | Claude Code, Cursor, ChatGPT, Kimi, Doubao, or any OpenAI-compatible API |

### Quick start

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

### Platforms

| Platform | How to use | File |
| :--- | :--- | :--- |
| Claude Code / Cursor / agent runtimes | Load as a native skill | `skill/SKILL.md` |
| ChatGPT / Kimi / Doubao web UIs | Paste as system prompt | `prompt/system_prompt.txt` |
| Python / automation | Inject as system message | `api/openai_compatible.py` |

### Roadmap

- [x] v1.02 — Initial release: three-stage funnel, multi-platform, CI, Docker, community health files
- [ ] v1.1 — Targeted flows for iOS / Android client samples
- [ ] v1.2 — Export reports in both Markdown and HTML
- [ ] v2.0 — Multi-model parallel review (GPT / Claude / DeepSeek consensus)

### Disclaimer

> [!WARNING]
> This project is for legitimate security auditing of your own assets, open-source code analysis, and authorized engagements only. You must have explicit written permission before testing any third-party system. See [DISCLAIMER.md](DISCLAIMER.md) and the additional terms in [LICENSE](LICENSE).

---

<div align="center">

**[📢 Release v1.02](https://github.com/Trace520/ultimate-security-audit/releases/tag/v1.02)** ·
**[🐛 Report a bug](https://github.com/Trace520/ultimate-security-audit/issues/new?template=bug_report.md)** ·
**[✨ Request a feature](https://github.com/Trace520/ultimate-security-audit/issues/new?template=feature_request.md)**

<sub>Built with care · MIT licensed · Not affiliated with any listed tool vendor</sub>

</div>
