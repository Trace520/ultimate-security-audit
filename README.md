<div align="center">

# 🛡️ Ultimate Security Audit

**结构化代码 & 架构审查的 AI Agent 技能**

[![CI](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v1.02-blue?logo=github)](https://github.com/Trace520/ultimate-security-audit/releases/tag/v1.02)
[![License](https://img.shields.io/badge/license-MIT%20%2B%20Security%20Terms-green)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Claude%20Code%20%7C%20Cursor%20%7C%20OpenAI%20API-purple)](#-全平台支持矩阵)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen)](CONTRIBUTING.md)

**[English](#-english-version) · [简体中文](#-简体中文)**

</div>

---

<a id="-简体中文"></a>

## 🎯 这是什么

一个可移植的 AI Agent 技能，把任意大模型变成**结构化的代码与架构审查员**。它不直接下结论，而是强制走三阶漏斗、写证据链、引用具体行号，避免"AI 一本正经地胡说八道"。

## ✨ 核心亮点

| 能力 | 解决什么问题 |
| :--- | :--- |
| 🪣 **三阶漏斗模型** | 静态发现 → 中间层降维 → 深度推演，不跳步 |
| 🔍 **证据溯源** | 所有结论必须绑定文件 + 行号，信息不足直接说"不确定" |
| 🧠 **防幻觉记忆** | 审查笔记实时写入 `reverse_notes.md`，可追溯可复盘 |
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
│   └── audit_report.md     # 标准审计报告示例
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/ci.yml
```

## 📚 更多文档

- [底层工具链配置指南](docs/toolchain.md)
- [示例：对演示样本的审计输出](examples/audit_report.md)
- [安全策略（漏洞披露）](SECURITY.md)
- [贡献指南](CONTRIBUTING.md)
- [行为准则](CODE_OF_CONDUCT.md)

## ⚠️ 免责声明

本项目仅用于合法的企业级软件安全审计、自有资产测试、开源项目分析及已授权的安全研究。使用者需确保对审查目标拥有合法授权；严禁用于任何未授权的逆向、破解或攻击行为。详见 [DISCLAIMER.md](DISCLAIMER.md)。

---

<a id="-english-version"></a>

## 🌐 English Version

### What is this?

A portable AI Agent skill that turns any LLM into a **structured code & architecture reviewer**. Instead of jumping to conclusions, it enforces a three-stage funnel, writes an evidence trail, and cites specific file/line references — so the output is auditable, not hallucinated.

### Why use it

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

### Disclaimer

This project is for legitimate security auditing of your own assets, open-source code analysis, and authorized engagements only. You must have explicit written permission before testing any third-party system. See [DISCLAIMER.md](DISCLAIMER.md) and the additional terms in [LICENSE](LICENSE).

---

<div align="center">

**[📢 Release v1.02](https://github.com/Trace520/ultimate-security-audit/releases/tag/v1.02)** · **[Report a bug](https://github.com/Trace520/ultimate-security-audit/issues/new?template=bug_report.md)** · **[Request a feature](https://github.com/Trace520/ultimate-security-audit/issues/new?template=feature_request.md)**

</div>
