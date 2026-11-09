<div align="center">

<img src="https://aka.doubaocdn.com/s/eopsS0yVb4" alt="Ultimate Security Audit" width="100%" />

# 🛡️ Ultimate Security Audit

**给 AI Agent 用的结构化代码安全审计技能**

[![CI](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml)
[![Release](https://img.shields.io/badge/release-v1.1-blue?logo=github&style=flat-square)](https://github.com/Trace520/ultimate-security-audit/releases/tag/v1.1)
[![License](https://img.shields.io/badge/license-MIT%20%2B%20Security%20Terms-green?style=flat-square)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&style=flat-square)](api/openai_compatible.py)

</div>

---

## 它到底做什么

你把一段代码、一个 URL、或一个二进制样本丢给 AI，普通做法是它直接给结论。这个技能强制 AI 按**固定三步**走，并且每一步都把过程写进本地文件——你事后能复盘它"看到了什么、怎么判断的"。

它不是自动化扫描器（不是 Semgrep/CodeQL），也不是漏洞利用生成器。它是一套**流程规范**，让 AI 的输出从"一段话说"变成"一份可审计的记录"。

---

## 三步工作流

| 阶段 | AI 实际在做什么 | 产出 |
| :--- | :--- | :--- |
| **① 静态发现** | 读源码/抓包，列出入口点（路由、导出函数、事件监听）、外部调用（fetch/XHR/socket）、可疑模式（eval、atob、硬编码密钥） | 写入 `reverse_notes.md` 的"发现清单"段落 |
| **② 中间层降维** | 对混淆代码反混淆（webcrack）、对二进制反编译（jadx/Ghidra）、对前端流量用 Playwright MCP 拦截，还原关键函数真实逻辑 | 写入 `reverse_notes.md` 的"还原"段落 |
| **③ 深度推演** | 从入口追数据流到 sink，判断可达性，构造最简 PoC，按严重度分级 | 输出 `audit_report.md` |

**铁律：**
- 每个结论必须引用具体文件 + 行号；找不到证据就直接写"不确定"，不准编。
- 所有中间发现按时间顺序追加到 `reverse_notes.md`，多轮对话不丢上下文。
- 遇到需要工具的场景（抓包、反编译），AI 必须显式调用对应工具，不准凭想象猜。

---

## 输入 / 输出契约

**你给它什么：**
- 一段代码片段（直接贴）
- 一个本地文件路径或目录
- 一个 URL（会引导你用 Playwright MCP 抓）
- 一个样本二进制（会引导 jadx/Ghidra）

**它给你什么：**
- `reverse_notes.md` — 全过程证据链（按时间倒序，每步带文件+行号引用）
- `audit_report.md` — 最终报告，结构：概述 → 发现列表（按严重度）→ 每个发现的证据链 → 复现步骤 → 建议修复

示例见 [`examples/`](examples/)：
- [`sample_code.js`](examples/sample_code.js) — 带 XOR 混淆的演示样本
- [`reverse_notes.md`](examples/reverse_notes.md) — 对该样本的证据链
- [`audit_report.md`](examples/audit_report.md) — 最终报告

---

## 三种用法

| 平台 | 怎么加载 | 文件 |
| :--- | :--- | :--- |
| **Claude Code / Cursor** | 克隆到 skills 目录，原生加载 | `skill/SKILL.md` |
| **ChatGPT / Kimi / 豆包 网页版** | 复制 `prompt/system_prompt.txt` 作为系统提示词 | `prompt/system_prompt.txt` |
| **Python 脚本 / 自动化** | 作为 System Message 注入 | `api/openai_compatible.py` |

---

## 快速开始

**方式 A：Claude Code / Cursor 技能**
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

**方式 C：Docker（自带 Playwright）**
```bash
docker build -t ultimate-security-audit .
docker run --rm -it ultimate-security-audit
```

---

## 仓库结构

```text
ultimate-security-audit/
├── skill/SKILL.md              # Agent 技能定义
├── prompt/system_prompt.txt    # 网页版系统提示词
├── api/openai_compatible.py    # OpenAI 兼容 Python 客户端
├── docs/toolchain.md           # Playwright / webcrack / Ghidra / jadx 接入说明
├── examples/                   # 演示样本 + 证据链 + 报告
├── .github/workflows/ci.yml    # 跨平台 CI (ubuntu/windows × py3.10/3.12)
├── Dockerfile
├── LICENSE                     # MIT + 安全工具附加条款
├── SECURITY.md                 # 漏洞披露政策
├── DISCLAIMER.md               # 法律免责
└── CONTRIBUTING.md / CODE_OF_CONDUCT.md
```

---

## 外部工具依赖（按需安装）

技能本身不强制装这些，但 AI 会引导你在需要时调用：

- **Playwright MCP** — 前端抓包 / 动态分析
- **webcrack** — JS 反混淆（`npm i -g webcrack`）
- **jadx** — Android APK 反编译
- **Ghidra** — 原生二进制逆向

详见 [`docs/toolchain.md`](docs/toolchain.md)。

---

## ⚠️ 免责声明

> [!WARNING]
> 本项目**仅用于**合法的企业级软件安全审计、自有资产测试、开源项目分析及已授权的安全研究。使用者需确保对审查目标拥有合法授权；**严禁**用于任何未授权的逆向、破解或攻击行为。详见 [DISCLAIMER.md](DISCLAIMER.md)。

---

<div align="center">

**[📢 v1.1 Release](https://github.com/Trace520/ultimate-security-audit/releases/tag/v1.1)** ·
**[🐛 报 Bug](https://github.com/Trace520/ultimate-security-audit/issues/new?template=bug_report.md)** ·
**[✨ 提需求](https://github.com/Trace520/ultimate-security-audit/issues/new?template=feature_request.md)**

</div>
