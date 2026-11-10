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
| `skill/SKILL.md` | Native skill definition (Claude Code / Cursor / similar) |
| `prompt/system_prompt.txt` | Plain-text system prompt for web chat UIs |
| `api/openai_compatible.py` | Minimal OpenAI-compatible client wrapper |
| `scripts/run_audit.py` | CI gate + stage-one static recon CLI (stdlib only, offline, read-only) |
| `examples/` | Self-contained demo fixtures and sample audit output |
| `docs/toolchain.md` | Optional underlying tooling (Playwright, webcrack, Ghidra) |
| `docs/CAPABILITIES.md` | One-page map of what each entry point can and cannot answer |

See [LICENSE](LICENSE), [DISCLAIMER.md](DISCLAIMER.md), and
[SECURITY.md](SECURITY.md) for legal and reporting terms.
