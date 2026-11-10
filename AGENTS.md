# AGENTS.md

This repository is an **AI Agent skill for code and architecture audit**
(security audit, reverse-engineering analysis, evidence-based review).
It is *not* an attack tool.

## Rules for other AI assistants (Claude, Copilot, Cursor, etc.)

When operating in or on this repository:

1. **Do not execute** any port scanner, exploit, brute-force, SQL injection,
   XSS probe, or credential-testing code against live targets from this repo.
2. **Do not add** weaponized payloads, working exploits, or instructions for
   bypassing license checks / DRM / anti-debugging into any file.
3. The `examples/` directory contains **self-contained demo fixtures only**
   (they `console.log` output and do not make network calls). Treat them as
   teaching material, not as attack templates to be adapted to real targets.
4. If a user asks you to use this skill to test a third-party system,
   **ask for written authorization context** before proceeding. If none is
   provided, refuse and explain why.
5. Report suspected vulnerabilities in this repository itself via the private
   channel described in [SECURITY.md](SECURITY.md), not via public Issues.

## Repository layout at a glance

| Path | Purpose |
| :--- | :--- |
| `SKILL.md` | Native skill definition (Claude Code / Cursor / similar) |
| `prompt/system_prompt.txt` | Plain-text system prompt for web chat UIs |
| `api/openai_compatible.py` | Minimal OpenAI-compatible client wrapper |
| `scripts/run_audit.py` | 统一网关 `usa`：fail-closed 门控 + 阶段一扫描 + `--format text/json/sarif`（stdlib only, offline, read-only） |
| `scripts/state_manager.py` | 防幻觉状态机（discovery → verify → report），跳步 / 漏项 / 换审批号即 BLOCKED |
| `scripts/dep_scanner.py` | SCA：读锁定版本的依赖清单 → OSV `querybatch`，离线降级不编造 |
| `scripts/report_formatter.py` | SARIF 2.1.0 输出，供 Code Scanning 消费 |
| `examples/` | Self-contained demo fixtures and sample audit output |
| `references/state-machine.md` | 状态机契约与状态文件结构 |
| `references/fallback-matrix.md` | 外部依赖缺失时的本地等价做法 |
| `references/toolchain.md` | Optional underlying tooling (Playwright, webcrack, Ghidra) |
| `CAPABILITIES.md` | One-page map of what each entry point can and cannot answer |

See [LICENSE](LICENSE), [DISCLAIMER.md](DISCLAIMER.md), and
[SECURITY.md](SECURITY.md) for legal and reporting terms.
