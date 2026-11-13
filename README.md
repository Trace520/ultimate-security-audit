<div align="center">

<img src="https://aka.doubaocdn.com/s/eopsS0yVb4" alt="Ultimate Security Audit" width="100%" />

# 🛡️ Ultimate Security Audit (USA)

**授权门控 + 防幻觉状态机 + SCA 供应链扫描 + SARIF 标准输出（V3.0.0）**

[![CI](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml)
[![SARIF 2.1.0](https://img.shields.io/badge/report-SARIF%202.1.0-blue?style=flat-square)](references/audit-report.md)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.12-3776AB?logo=python&style=flat-square)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT%20%2B%20Security%20Terms-green?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

**简体中文** · [English](README.en.md)

</div>

---

> [!NOTE]
> 它不是 Semgrep/CodeQL 那类规则引擎，也不是漏洞利用生成器。它是一套**可断言的审计流水线**：授权先行、命中可复算、状态可追溯、报告能被 CI 直接消费。

## 为什么需要它

AI 做安全审计有三个反复出现的问题：

| 问题 | 表现 | USA 的答案 |
|---|---|---|
| **幻觉** | 推演到一半忘了入口点从哪来，凭「看起来像」下结论 | 强制状态机 `discovery → verify → report`，没核实的不许出报告 |
| **格式孤立** | 报告只有人能读，CI / Code Scanning 消费不了 | 原生 SARIF 2.1.0，PR 里带行号标注 |
| **维度单一** | 只扫自己的代码，不看第三方依赖的已知漏洞 | OSV 依赖扫描，拿不到数据就降级，绝不编造 |

外面还套了一层 **fail-closed 授权门控**：没有审批号，一行代码都不读。

## 快速开始

```bash
pip install -e .
usa --help
```

第一次跑（把审批号换成本次任务的真实编号）：

```bash
usa tests/fixtures/sample --approval-id CHG-2026-0417
```

```text
[AUDIT_MODE: DEGRADED | approval: CHG-2026-0417 | targets: 1 | ci: none]
  sample_code.js:5 [HARDCODED_SECRET] secret_key_123
[*] 扫描目标 1 个，可疑模式命中 1 条
[*] 分级：error 1 / warning 0 / note 0
```

没有审批号时：

```text
[AUDIT_MODE: BLOCKED | missing: AUTHORIZATION_MODE=CI_PIPELINE 或 --approval-id + 目标; AUDIT_APPROVAL_ID]
exit=2
```

## 核心特性

| 特性 | 说明 |
|---|---|
| 🔒 Fail-Closed 门控 | 缺审批号 / 占位值（`TBD`、`0000`）/ 目标越界 / 读不到 HEAD → `BLOCKED` + 退出码 `2`，且不打开目标文件 |
| 🧠 防幻觉状态机 | 每条命中必须「核实」或「明确放弃」；跳步（没 discovery 就 verify、没 verify 就 report）直接 `BLOCKED` |
| 📦 SCA 供应链扫描 | 只查锁定版本的 `requirements.txt` / `package-lock.json`，走 OSV `querybatch`；离线降级为 `DEGRADED` |
| 📊 SARIF 2.1.0 | `--format sarif` 可直接上传 GitHub Code Scanning |
| 🧾 证据落盘 | 授权段、命中表、未执行阶段写进 `audit_notes.local.md`（已 gitignore） |
| 🪪 三入口等价 | `usa` / `python -m scripts` / `python scripts/run_audit.py` 共用同一套门控 |
| 🤖 AI 复核（可选） | `--use-ai` 把本地命中逐条送模型判真假，**失败降级、命中保留**，不加新命中 |
| 📄 确定性输出 | 同一目标同一 commit，扫描结果逐字节一致（`tests/test_golden.py` 守着） |

## 典型用法

**1. 本地快速扫描**

```bash
usa ./src --approval-id CHG-2026-0417 --format json --out audit.json
```

**2. 带状态机（推荐给 AI / 长链路审计）**

```bash
usa ./src --approval-id CHG-2026-0417 --stage discovery
usa ./src --approval-id CHG-2026-0417 --stage verify --verify-all
usa ./src --approval-id CHG-2026-0417 --stage report --format sarif --out results.sarif
```

`--verify` 逐条核实（可重复），`--waive` 明确放弃；两者都没覆盖到的命中会让 `verify` 失败并列出来。

**3. SCA 依赖扫描**

```bash
usa . --approval-id CHG-2026-0417 --sca
```

命中形如 `DEP_VULN  requests==2.19.0 GHSA-9hjg-9r4m-mvj7 fix>=2.20.0`。只读本地清单 + 只调 OSV 一个只读接口，不装包、不执行目标代码。

**4. CI 无人值守**

```yaml
env:
  AUTHORIZATION_MODE: CI_PIPELINE
  AUDIT_APPROVAL_ID: ${{ vars.AUDIT_APPROVAL_ID }}
  AUDIT_TARGETS: "src/;dist/app.asar"
run: usa --format sarif --out results.sarif
```

**5. 可选 AI 复核（过滤误报）**

```bash
pip install -e '.[ai]'
export OPENROUTER_API_KEY="sk-or-v1-..."
usa . --approval-id CHG-2026-0417 --use-ai --format json --out audit.json
```

只把「相对路径 + 行号 + 命中片段」送出去，命中里追加 `ai_verdict`（`CONFIRMED` / `DISMISSED` / `UNRESOLVED`）。
没 key、没装 `requests`、网络失败、返回不合法 —— 一律保留原命中并记 `UNRESOLVED`，不会静默丢结果。
阈值、降级矩阵与隐私说明见 `references/ai-layer.md`。

## 报告格式

| 格式 | 用途 | 命令 |
|---|---|---|
| text | 人在终端看 | 默认 |
| json | 机器消费 / 存档 | `--format json --out audit.json` |
| sarif | GitHub Code Scanning | `--format sarif --out results.sarif` |

SARIF 每条结果都带 `file` + `startLine` + `ruleId`。等级映射固定：硬编码凭据 / `eval` / 关闭证书校验 → `error`；其余 → `warning` 或 `note`。

## 吃自己的狗粮

CI 不只跑 pytest——它让 USA 扫自己，并把 SARIF 传到 Security 面板：

```yaml
- run: usa . --approval-id CI-SELF-AUDIT --format sarif --out results.sarif --allow-findings
- uses: github/codeql-action/upload-sarif@v3
  with: { sarif_file: results.sarif }
```

这份结果会出现在仓库的 Security 标签页里。**注意**：扫到 `examples/` 与 `tests/fixtures/` 的演示密钥是预期行为，所以自我审计用 `--allow-findings` 不让 CI 红。

## 目录结构

```text
ultimate-security-audit/
├── README.md / README.en.md # 门面（中 / 英双语）
├── SKILL.md                 # Agent 入口契约（门控 + 状态机铁律）
├── CAPABILITIES.md          # 一页能力矩阵（含 .en 英文版）
├── references/              # 渐进披露：按需加载的细则（含 ai-layer.md）
├── assets/                  # 证据笔记模板
├── scripts/
│   ├── run_audit.py         # 统一网关 usa
│   ├── project_probe.py     # 阶段一静态扫描（10 条规则）
│   ├── dep_scanner.py       # SCA：OSV 依赖漏洞
│   ├── llm_analyzer.py      # AI 复核层（可选，唯一会调外部模型的模块）
│   ├── state_manager.py     # 防幻觉状态机
│   ├── report_formatter.py  # SARIF 输出
│   └── check_docs.py        # 文档死链校验
├── tests/                   # golden / 状态机 / SCA / AI 层 / 完整性
└── .github/workflows/ci.yml # 测试 + 自我审计 + SARIF 上传
```

## 自检

```bash
make check     # 文档校验 + pytest + 门控冒烟 + SARIF 冒烟
```

## 边界

只用于**自有资产或已获书面授权**的目标。不做未授权测试、不绕过许可与访问控制、不输出可批量利用的成品工具。`--use-ai` 会把命中片段送到第三方接口，敏感仓库请先看降级矩阵与隐私说明。细节见 [DISCLAIMER.md](DISCLAIMER.md) 与 [SECURITY.md](SECURITY.md)。
