---
name: ultimate-security-audit
version: 3.0.0
description: 针对代码库执行严格的安全审计，内置防幻觉状态机与供应链扫描。
compatibility: "Python 3.10+ required for scripts/. Falls back to local grep if external tools are missing."
license: MIT
---

# 终极安全审计技能 (USA)

## 🚨 强制铁律（必须遵守）
1. **授权校验**：任何行动前，必须确认存在 `--approval-id` 或有效授权证明，否则立即终止。
2. **防幻觉**：禁止凭空推演。必须先运行 `usa <target> --stage discovery` 将入口点写入状态机，然后运行 `usa <target> --stage verify`。若被 `BLOCKED`，退回阶段一重新收集证据。
3. **兜底自检**：如果发现 `scripts/run_audit.py` 不存在，直接输出 `[BLOCKED: scripts_missing]` 并停止，不要尝试继续审计。

## 🔄 三阶漏斗执行
请参考 `references/audit-workflow.md` 严格推进：
1. 静态发现 (Discovery)
2. 中间层降维 (De-obfuscation)
3. 深度推演 (Deep Dive)

## 📦 核心工具与报告
- **扫描依赖/密钥**：`usa <target> --stage discovery --format json`
- **生成 SARIF 报告**：`usa <target> --format sarif --out results.sarif`
- **环境降级探测**：运行 `python scripts/skill_probe.py`，若缺失外部能力，参考 `references/fallback-matrix.md` 执行本地命令。
