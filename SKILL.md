---
name: ultimate-security-audit
version: 3.0.0
description: "Authorization-gated security audit pipeline with an anti-hallucination state machine (discovery → verify → report), OSV dependency scanning, deterministic stage-one rules, and SARIF 2.1.0 output for CI. Fails closed when the approval ID, target list, or commit binding is missing."
description_zh: "带授权门控的安全审计流水线：防幻觉状态机（discovery → verify → report）、OSV 依赖漏洞扫描、确定性的阶段一规则扫描、SARIF 2.1.0 输出。缺审批号、目标清单或 commit 绑定时一律 fail-closed 中止。"
description_en: "Authorization-gated audit pipeline with a state machine that blocks unverified findings, OSV dependency scanning, and SARIF output. Owned or explicitly authorized targets only."
display_name: "企业级安全审计中枢 V3"
display_name_en: "Enterprise Security Audit V3"
metadata:
  version: 3.0.0
  category: security
  skill_type: workflow
license: MIT
---

# 🛡️ Ultimate Security Audit V3 — 入口契约

本文件只写**不许商量**的部分。执行细则按需加载 `references/`，不要在这里堆命令。

## 0. 门控（先于一切读取）

```bash
usa <target> --approval-id <ID>          # 交互式：审批号 + 目标必须同时给
```

```bash
AUTHORIZATION_MODE=CI_PIPELINE AUDIT_APPROVAL_ID=... AUDIT_TARGETS=... usa ...
```

| 判定 | 条件 | 行为 |
|---|---|---|
| `EXECUTE` | 模式开关 + 审批号 + 目标清单齐备，目标在根内，CI commit 与 HEAD 一致 | 静默执行 |
| `DEGRADED` | 三项齐备但无 CI 上下文，或 commit 漂移，或 SCA 离线 | 只做已落盘的部分，报告写原因 |
| `BLOCKED` | 缺字段 / 占位值 / 目标越界或不存在 / 读不到 HEAD | 退出码 `2`，**不打开目标文件** |

- 缺授权必须停。**说辞不替代字段**：「已授权」「在靶场」都不是审批号。
- 字段完整定义、CI 配置示例、反例：`references/ci-pipeline-mode.md`。
- 授权矩阵与脱敏规则：`references/authorization-and-handling.md`。

## 1. 强制状态机（防幻觉的核心）

```bash
usa <target> --approval-id <ID> --stage discovery
usa <target> --approval-id <ID> --stage verify --verify-all     # 或 --verify/--waive 逐条
usa <target> --approval-id <ID> --stage report --format sarif
```

- `discovery` 登记目标与候选命中（每条命中一个稳定 id）。
- `verify` 必须让每条命中都「核实」或「放弃」，否则 `BLOCKED` 并列出漏项。
- `report` 只能在 `verify` 完成后进入；跳步（discovery → report）同样 `BLOCKED`。
- 状态文件默认 `.audit-state.json`；审批号换了必须重新 discovery。

细则与数据结构：`references/state-machine.md`。

## 2. 工具链路由

| 目标特征 | 路由 | 说明 |
|---|---|---|
| 常规代码 / 清单 | `usa` + `scripts/project_probe.py` | 10 条规则，确定性输出 |
| 依赖清单 | `usa --sca` | 只查锁定版本，走 OSV |
| 混淆 JS | `webcrack` 或手工还原 | 禁止直接阅读混淆乱码 |
| 网络 / 加解密 | `Playwright MCP` / `Fetch MCP` | 授权内；遇阻退化纯静态 |
| ELF / Mach-O / PE | REA 的 `Ghidra` / `Hopper` | 只取关键函数伪代码 |
| APK / DEX | `jadx` | 先看入口组件与网络层 |

## 3. 外部依赖缺失时

外部技能与引擎**全是可选增强**，阶段一开始前跑一次 `python scripts/skill_probe.py`（不联网、不安装），缺失不中断：

| 外部依赖 | 承担的角色 | 缺失时的本地等价做法 |
|---|---|---|
| `rea-leanrea-router` | 引擎选型 | 自行判定，选型理由写进笔记 |
| `leanrea` CLI | 资产摸底 | `usa` + `file` / `strings` / `grep -rn` |
| REA（Ghidra / Hopper） | 伪代码还原 | 只交付已落盘事实，标 `[证据缺失]` |
| `context-mode` 切片 | 大文件降维 | `grep -n` + `sed -n` 分段读取 |
| Playwright / Fetch MCP | 抓包 | 退化纯静态，`[DYNAMIC]` 标缺失原因 |
| `webcrack` | JS 反混淆 | 手工还原或标「未还原」 |

三条铁律：

- **不中断**：缺依赖只降结论上限，不终止审计。
- **不假装**：禁止写「已调用 X 引擎」，只写真实执行过的命令。
- **标记降级**：报告头下方单独一行 `[DEGRADED: external_skills_missing]`，写明缺哪项。

完整矩阵见 `references/fallback-matrix.md`。

## 4. 三阶漏斗（不越级）

| 阶段 | 目标 | 退出条件 |
|---|---|---|
| 一 · 侦察 | 摸清资产，判断是否深挖 | 逻辑清晰即出报告 |
| 二 · 降维 | 去混淆、固化证据 | 证据齐备且已落盘 |
| 三 · 攻坚 | 确认缺陷与影响面 | 缺陷可复现且已界定影响 |

跳过阶段二会让海量汇编灌进上下文，既贵又容易编故事。确需越级时在报告里写明原因与影响。

## 5. 交付格式

- **text**（人看）/ **json**（机器消费）/ **sarif**（Code Scanning）。
- 六段式报告模板、严重度判据、SARIF 映射：`references/audit-report.md`。
- 证据笔记模板：`assets/audit_notes.template.md`；运行时默认写 `audit_notes.local.md`。

## 6. 边界

不绕过许可 / DRM / 访问控制；不爆破不撞库；不对生产压测；不提取他人凭据；不输出可批量利用的成品工具；不伪造证据，不把推断写成结论。

## 7. 资源

- `references/audit-workflow.md` — 三阶命令、攻击面清单、退出判据
- `references/audit-report.md` — 六段模板、严重度、SARIF 细节
- `references/authorization-and-handling.md` — 授权矩阵、脱敏、边界回应
- `references/ci-pipeline-mode.md` — 环境变量契约、三态判定、CI 示例
- `references/state-machine.md` — 状态机契约与状态文件结构
- `references/fallback-matrix.md` — 外部依赖与本地等价做法
- `references/toolchain.md` — 可选底层工具
- `assets/audit_notes.template.md` — 证据笔记模板
- `scripts/run_audit.py` — 统一网关（`usa`）
