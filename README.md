#🛡️ 安全审核代理技能

[英语](现在我们要做些什么?) | [简体中文](#中文版)

![美国](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml/badge.svg)
![许可证](https://img.shields.io/badge/license-MIT-blue.svg)

> 让 AI Agent 化身无情的白帽审计机器：内置三阶漏斗模型、强制工具链路由与防幻觉记忆机制。告别 AI 的废话与无脑拒答。

---

<一个标签:="中文版"></一个>
## 🇨🇳 中文版

### 💡 解决的痛点

- **拒绝死循环**：通过严谨的“红队靶场”上下文覆盖，消除 AI 无限索要授权的问题。
- **拒绝上下文爆炸**：独创三阶漏斗（侦察 -> 中间件降维 -> 重型攻坚），极大节省 Token。
- **拒绝幻觉**：强制将证据写入本地 `reverse_notes.md`，所有结论必须有源可溯。

### 🌟 全平台支持矩阵

| 平台类型 | 使用方式 | 对应文件 |
| :--- | :--- | :--- |
| **克劳德代码/光标/工作伙伴** | 原生技能加载（放入 skills 目录） | `skill/SKILL.md` |
| **ChatGPT / Kimi / 豆包 网页版** | 复制粘贴作为系统提示词 | `系统的提示` |
| **Python / 自动化脚本** | 作为 System Message 注入 API | `美国政府` |

### 🚀 快速开始

**方式一：克隆至 Agent 技能目录（以 Claude Code 为例）**
```猛击
git克隆https://github.com/Trace520/ultimate-security-audit.git~/.claude/skillips/终极安全审核
```

方式二：Docker 快速体验

```猛击
# 构建镜像
Docker构建-t最终-安全-审计。

# 运行容器
Docker run-rm-it最终-安全-审核
```

📂 仓库结构

· skill/ - 原生 Agent 技能核心文件（SKILL.md）
· prompt/ - 适用于网页版大模型的纯文本提示词
· api/ - Python 自动化集成脚本
· examples/ - 真实运行演示（包含代码样本、证据链笔记、Mermaid 审计报告）
🛡️ 终极安全审核代理技能

⚠️ 免责声明

本项目仅用于合法的企业级软件安全审计、自有资产测试及已获授权的红队演练。严禁用于任何未授权的恶意攻击行为。 使用前请务必阅读 DISCLAIMER.md 及 SECURITY.md。

---

<一个标签:="英语版本"></一个>

🇬🇧 英文版

终极安全审核代理技能

企业级代码审查和自动化逆向工程AI代理工作流技能。

✨ 功能

·三级漏斗：强制AI执行“静态侦察->中间件去模糊->深度分析”，保存令牌，防止幻觉。
·上下文覆盖：内置红队演练上下文，绕过AI重复的授权提示。
·抗幻觉存储器：在得出结论之前，强制AI将证据(API路径、伪代码)写入本地reverse_notes.md。
·Toolchain路由：根据目标特性自动路由到Playwright MCP(流量捕获)、webcrack(去模糊处理)或jadx(反编译)。

🚀 快速入门

```猛击
git克隆https://github.com/Trace520/ultimate-security-audit.git~/.claude/skillips/终极安全审核
```

⚠️ 免责声明

此工具严格用于授权安全测试、资产审计和红色团队演练。有关详细信息，请参阅DISCLAIMER.MD。

---

如果这个项目对你有帮助，请考虑给它安0！
