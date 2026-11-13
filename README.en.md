# 🛡️ Ultimate Security Audit (USA)

<div align="center">

<img src="https://aka.doubaocdn.com/s/eopsS0yVb4" alt="Ultimate Security Audit" width="100%" />

<h1>🛡️ Ultimate Security Audit (USA)</h1>

<p><strong>Authorization gate + anti-hallucination state machine + SCA + SARIF 2.1.0 output (v3.0.0)</strong></p>

<p>

[![CI](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml/badge.svg)](https://github.com/Trace520/ultimate-security-audit/actions/workflows/ci.yml)
[![SARIF 2.1.0](https://img.shields.io/badge/report-SARIF%202.1.0-blue?style=flat-square)](references/audit-report.md)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.12-3776AB?logo=python&style=flat-square)](pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT%20%2B%20Security%20Terms-green?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

</p>

<p><strong>English</strong> · <a href="README.md">简体中文</a></p>

</div>

---

> [!NOTE]
> This is not a rule engine like Semgrep/CodeQL, and it is not an exploit generator. It is an **assertable audit pipeline**: authorization comes first, findings are reproducible, state is traceable, and reports are directly consumable by CI.

## Why it exists

Three problems keep showing up when AI is asked to audit code:

| Problem | Symptom | What USA does |
|---|---|---|
| **Hallucination** | Mid-analysis the model forgets where its entry points came from and concludes from "it looks like" | A forced state machine `discovery → verify → report`; nothing unverified reaches the report |
| **Isolated output** | Reports only humans can read; CI / Code Scanning cannot consume them | Native SARIF 2.1.0 with line annotations in the PR |
| **Single dimension** | Only your own code gets scanned, never known CVEs in third-party dependencies | OSV dependency scan; degrades when data is unavailable, never fabricates |

Wrapped around all of it is a **fail-closed authorization gate**: no approval ID, not a single line of code is read.

## Quick start

```bash
pip install -e .
usa --help
```

First run (replace the approval ID with the real ticket number for this job):

```bash
usa tests/fixtures/sample --approval-id CHG-2026-0417
```

```text
[AUDIT_MODE: DEGRADED | approval: CHG-2026-0417 | targets: 1 | ci: none]
  sample_code.js:5 [HARDCODED_SECRET] secret_key_123
[*] 扫描目标 1 个，可疑模式命中 1 条
[*] 分级：error 1 / warning 0 / note 0
```

Without an approval ID:

```text
[AUDIT_MODE: BLOCKED | missing: AUTHORIZATION_MODE=CI_PIPELINE 或 --approval-id + 目标; AUDIT_APPROVAL_ID]
exit=2
```

## Features

| Feature | Details |
|---|---|
| 🔒 Fail-closed gate | Missing approval ID / placeholder (`TBD`, `0000`) / target outside root / HEAD unreadable → `BLOCKED` + exit code `2`, target files never opened |
| 🧠 Anti-hallucination state machine | Every finding must be `--verify`'d or `--waive`'d; skipping a stage (`verify` before `discovery`, `report` before `verify`) is `BLOCKED` |
| 📦 SCA supply-chain scan | Only pinned versions in `requirements.txt` / `package-lock.json`, via OSV `querybatch`; offline runs degrade to `DEGRADED` |
| 📊 SARIF 2.1.0 | `--format sarif` uploads straight to GitHub Code Scanning |
| 🧾 Evidence on disk | Authorization block, finding table and unexecuted stages land in `audit_notes.local.md` (gitignored) |
| 🪪 Three equivalent entrypoints | `usa` / `python -m scripts` / `python scripts/run_audit.py` share one gate |
| 🤖 Optional AI review | `--use-ai` asks a model whether each finding is real; **failure degrades, findings are kept**, no new findings |
| 📄 Deterministic output | Same target, same commit → byte-identical scan results (`tests/test_golden.py` enforces it) |

## Usage

**1. Quick local scan**

```bash
usa ./src --approval-id CHG-2026-0417 --format json --out audit.json
```

**2. With the state machine (recommended for AI-driven / long audits)**

```bash
usa ./src --approval-id CHG-2026-0417 --stage discovery
usa ./src --approval-id CHG-2026-0417 --stage verify --verify-all
usa ./src --approval-id CHG-2026-0417 --stage report --format sarif --out results.sarif
```

`--verify` confirms one finding (repeatable), `--waive` explicitly dismisses one; findings covered by neither make `verify` fail and list them.

**3. SCA dependency scan**

```bash
usa . --approval-id CHG-2026-0417 --sca
```

Findings look like `DEP_VULN  requests==2.19.0 GHSA-9hjg-9r4m-mvj7 fix>=2.20.0`. Reads local manifests only and calls exactly one read-only OSV endpoint — no installs, no execution of target code.

**4. Unattended CI**

```yaml
env:
  AUTHORIZATION_MODE: CI_PIPELINE
  AUDIT_APPROVAL_ID: ${{ vars.AUDIT_APPROVAL_ID }}
  AUDIT_TARGETS: "src/;dist/app.asar"
run: usa --format sarif --out results.sarif
```

**5. Optional AI review (false-positive filtering)**

```bash
pip install -e '.[ai]'
export OPENROUTER_API_KEY="sk-or-v1-..."
usa . --approval-id CHG-2026-0417 --use-ai --format json --out audit.json
```

Only "relative path + line number + matched snippet" leaves the machine; findings gain `ai_verdict` (`CONFIRMED` / `DISMISSED` / `UNRESOLVED`).
No key, no `requests`, network failure, malformed response — the original finding is kept and marked `UNRESOLVED`; results are never silently dropped.
Budgets, the degradation matrix and privacy notes live in `references/ai-layer.md`.

## Report formats

| Format | Use | Command |
|---|---|---|
| text | Human, terminal | default |
| json | Machine consumption / archive | `--format json --out audit.json` |
| sarif | GitHub Code Scanning | `--format sarif --out results.sarif` |

Every SARIF result carries `file` + `startLine` + `ruleId`. Level mapping is fixed: hardcoded credentials / `eval` / disabled certificate checks → `error`; everything else → `warning` or `note`.

## Dogfooding

CI doesn't just run pytest — it points USA at itself and ships the SARIF to the Security tab:

```yaml
- run: usa . --approval-id CI-SELF-AUDIT --format sarif --out results.sarif --allow-findings
- uses: github/codeql-action/upload-sarif@v3
  with: { sarif_file: results.sarif }
```

The results show up under the repository's Security tab. **Note**: demo keys in `examples/` and `tests/fixtures/` are expected findings, so the self-audit uses `--allow-findings` to keep CI green.

## Layout

```text
ultimate-security-audit/
├── README.md / README.en.md # Front page (Chinese / English)
├── SKILL.md                 # Agent entry contract (gate + state-machine rules)
├── CAPABILITIES.md          # One-page capability matrix
├── references/              # Progressive disclosure: details on demand (incl. ai-layer.md)
├── assets/                  # Evidence-note template
├── scripts/
│   ├── run_audit.py         # Unified gateway `usa`
│   ├── project_probe.py     # Stage 1 static scan (10 rules)
│   ├── dep_scanner.py       # SCA: OSV dependency vulnerabilities
│   ├── llm_analyzer.py      # Optional AI review (only module that talks to a model)
│   ├── state_manager.py     # Anti-hallucination state machine
│   ├── report_formatter.py  # SARIF output
│   └── check_docs.py        # Docs dead-link check
├── tests/                   # golden / state machine / SCA / AI layer / integrity
└── .github/workflows/ci.yml # tests + self-audit + SARIF upload
```

## Self-check

```bash
make check     # docs check + pytest + gate smoke + SARIF smoke
```

## Scope

Use it only against **assets you own or are authorized in writing to test**. No unauthorized testing, no bypassing licenses or access controls, no output that amounts to a ready-to-use exploitation tool. `--use-ai` sends finding snippets to a third-party endpoint — for sensitive repositories read the degradation matrix and privacy notes first. See [DISCLAIMER.md](DISCLAIMER.md) and [SECURITY.md](SECURITY.md).
