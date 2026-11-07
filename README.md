# 🛡️ Ultimate Security Audit Agent Skill

> 让 AI Agent 协助进行结构化的代码与架构审查：内置三阶漏斗模型、强制工具链路由与证据溯源机制。**全平台兼容，开源免费。**

## 🌟 全平台支持矩阵

| 平台类型 | 使用方式 | 对应文件 |
| :--- | :--- | :--- |
| **Claude Code / Cursor / 其他 Agent 运行时** | 原生技能加载（放入 skills 目录） | `skill/SKILL.md` |
| **ChatGPT / Kimi / 豆包 网页版** | 复制粘贴作为系统提示词 | `prompt/system_prompt.txt` |
| **Python / 自动化脚本** | 作为 System Message 注入 | `api/openai_compatible.py` |

## 💡 解决的痛点

- **结构化审查**：三阶漏斗（静态发现 → 中间层降维 → 深度推演），避免一上来就陷入细节。
- **节省上下文**：分层处理，先抓核心模块再下钻，减少无效 Token 消耗。
- **拒绝幻觉**：强制证据溯源，所有结论必须引用代码中的具体行/特征，信息不足时直接说明。

## 🚀 快速开始

克隆本项目后，根据上方的平台矩阵选择对应文件。在审查自有代码、开源项目或已授权目标时，建议配合 `Playwright MCP`、`webcrack`、`Ghidra` 等底层工具使用。

```bash
git clone https://github.com/Trace520/ultimate-security-audit.git
cd ultimate-security-audit
# 按平台选择 skill/SKILL.md 或 prompt/system_prompt.txt
```

## 📂 仓库结构

```text
ultimate-security-audit/
├── README.md
├── LICENSE
├── skill/
│   └── SKILL.md
├── prompt/
│   └── system_prompt.txt
├── api/
│   └── openai_compatible.py
└── docs/
    └── toolchain.md
```

## ⚠️ 免责声明

本项目仅用于合法的企业级软件安全审计、自有资产测试、开源项目分析及已授权的安全研究。使用者需确保对审查目标拥有合法授权；严禁用于任何未授权的逆向、破解或攻击行为。

## 📚 扩展阅读

- [底层工具链配置指南](docs/toolchain.md)
