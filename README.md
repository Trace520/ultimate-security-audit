[英语](现在我们要做些什么?) | [简体中文](#中文版)
##🛡️ 安全审核代理技能

![美国](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml/badge.svg)

> 让 AI Agent 协助进行结构化的代码与架构审查：内置三阶漏斗模型、强制工具链路由与证据溯源机制。**全平台兼容，开源免费。**

<一个身份标识="中文版"></一个>

## 🌟 全平台支持矩阵

| 平台类型 | 使用方式 | 对应文件 |
| :--- | :--- | :--- |
| **Claude Code / Cursor / 其他 Agent 运行时** | 原生技能加载（放入 skills 目录） | `skill/SKILL.md` |
| **ChatGPT / Kimi / 豆包 网页版** | 复制粘贴作为系统提示词 | `系统的提示` |
| **Python / 自动化脚本** | 作为 System Message 注入 | `美国政府` |

## 💡 解决的痛点

- **结构化审查**：三阶漏斗（静态发现 → 中间层降维 → 深度推演），避免一上来就陷入细节。
- **节省上下文**：分层处理，先抓核心模块再下钻，减少无效 Token 消耗。
- **拒绝幻觉**：强制证据溯源，所有结论必须引用代码中的具体行/特征，信息不足时直接说明。

## 🚀 快速开始

**方式 A：直接克隆到 Agent 的 skills 目录（以 Claude Code 为例）**

```bash
git clone https://github.com/Trace520/ultimate-security-audit.git ~/.claude/skills/ultimate-security-audit
```

**方式 B：克隆到任意位置，按平台挑选文件**

```bash
git clone https://github.com/Trace520/ultimate-security-audit.git
cd ultimate-security-audit
# 按平台选择 skill/SKILL.md 或 prompt/system_prompt.txt
```

**方式 C：Docker（自带 Playwright 运行时）**

```bash
docker build -t ultimate-security-audit .
```

在审查自有代码、开源项目或已授权目标时，建议配合 `Playwright MCP`、`webcrack`、`Ghidra` 等底层工具使用。

## 📂 仓库结构

```text
ultimate-security-audit/
├── README.md
├── LICENSE
├── Dockerfile
├── skill/
│   └── SKILL.md
├── prompt/
│   └── system_prompt.txt
├── api/
│   └── openai_compatible.py
├── docs/
│   └── toolchain.md
├── examples/
│   ├── sample_code.js
│   ├── reverse_notes.md
│   └── audit_report.md
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   └── feature_request.md
    └── workflows/
        └── ci.yml
```

## ⚠️ 免责声明

本项目仅用于合法的企业级软件安全审计、自有资产测试、开源项目分析及已授权的安全研究。使用者需确保对审查目标拥有合法授权；严禁用于任何未授权的逆向、破解或攻击行为。详见 [DISCLAIMER.md](DISCLAIMER.md)。

## 📚 扩展阅读

- [底层工具链配置指南](docs/toolchain.md)
- [示例：对演示样本的审计输出](examples/audit_report.md)
- [安全策略（漏洞披露）](SECURITY.md)
- [贡献指南](CONTRIBUTING.md)

---

<a id="english-version"></a>

## English Version

**Ultimate Security Audit** is a portable AI Agent skill that turns any LLM into a structured code & architecture reviewer. It uses a three-stage funnel (static discovery → intermediate deobfuscation → deep logic deduction) with evidence-first output (every claim must cite a file and line, no hallucination).

### Supported platforms

| Platform | How to use | File |
| :--- | :--- | :--- |
| Claude Code / Cursor / other agent runtimes | Load as a native skill | `skill/SKILL.md` |
| ChatGPT / Kimi / Doubao web UIs | Paste as system prompt | `prompt/system_prompt.txt` |
| Python / automation | Inject as a system message | `api/openai_compatible.py` |

### Quick start

```bash
git clone https://github.com/Trace520/ultimate-security-audit.git ~/.claude/skills/ultimate-security-audit
# or
docker build -t ultimate-security-audit .
```

### Disclaimer

This project is for legitimate security auditing of your own assets, open-source code analysis, and authorized red-team exercises only. You must have explicit written permission before testing any third-party system. See [DISCLAIMER.md](DISCLAIMER.md) and the additional terms in [LICENSE](LICENSE).
