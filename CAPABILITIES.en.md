# Capabilities

**English** · [简体中文](CAPABILITIES.md)

One-page reference. Each entrypoint answers exactly one question and none replaces another; the rules behind them live in `references/`, and runtime evidence lands in `audit_notes.local.md`.

## 1. Entrypoints

| Entrypoint | Question it answers | How to use |
|---|---|---|
| `usa` (= `scripts/run_audit.py`) | Does this run have authorization, and what was found | `usa tests/fixtures/sample --approval-id CHG-001` |
| `scripts/project_probe.py` | Which suspicious patterns exist in one directory / file | `python scripts/project_probe.py <target>` |
| `scripts/dep_scanner.py` | Do the dependency manifests contain known vulnerabilities | `usa <target> --sca` |
| `scripts/state_manager.py` | How far this audit got, and what is still missing | `usa <target> --stage verify` |
| `scripts/report_formatter.py` | How results become SARIF | `usa <target> --format sarif` |
| `scripts/llm_analyzer.py` | Is this finding a real problem (optional, needs network) | `usa <target> --approval-id <ID> --use-ai` |
| `scripts/skill_probe.py` | Are external engines installed, is degradation required | `python scripts/skill_probe.py` |
| `scripts/check_docs.py` | Do the paths written in docs actually exist | `python scripts/check_docs.py` |

Three equivalent entrypoints: `usa` / `python -m scripts` / `python scripts/run_audit.py` share the same gate.

## 2. Gate states

| State | Condition | Behavior |
|---|---|---|
| `EXECUTE` | Mode switch + approval ID + target list all present, targets inside root, CI commit matches HEAD | Run silently |
| `DEGRADED` | All three present but no CI context / commit drift / SCA offline | Do only what is already persisted, report the reason |
| `BLOCKED` | Missing field / placeholder / target outside root or missing / HEAD unreadable | Exit code `2`, **target files never opened** |

Interactive runs require both `--approval-id` and a target; passing only one is `BLOCKED`.

## 3. State machine

`discovery → verify → report`. `verify` requires every finding to be covered by `--verify` or `--waive`;
skipping a stage, leaving gaps, or changing the approval ID is `BLOCKED`. See `references/state-machine.md`.

## 4. What the first stage can answer

- Suspicious patterns for 10 rules: hardcoded credentials, `eval`, `Function` constructor, process calls, disabled certificate checks, HTML injection sinks, SQL concatenation, plaintext HTTP, debug switches, obfuscated variable names assigned strings.
- SCA: pinned versions only (`==` in `requirements.txt`, `version` in `package-lock.json`), via OSV `querybatch`.
- Every finding carries `file:line`, a rule ID and a snippet; output is deterministic, enforced by `tests/test_golden.py`.
- Noise control: plaintext `http://` to loopback / example hosts is dropped; `--exclude` skips a third-party bundle whole; `--baseline` reports only new findings.

## 4.5 AI review (optional second layer)

`--use-ai` sends each local finding to a model for review. It only decides "real / not real" — it never adds findings.
No `OPENROUTER_API_KEY`, no `requests`, network failure, malformed response — the original finding is kept and marked
`ai_verdict=UNRESOLVED`. Results are never silently dropped. Budgets and the degradation matrix are in `references/ai-layer.md`.

## 5. What it deliberately does not answer

- No vulnerability verdict. A finding is a "suspicious pattern"; reachability and impact belong to stages two and three.
- No packet capture, no deobfuscation, no decompilation, no PoC construction.
- No executing target code, no installing dependencies, no modifying target files. Exactly two network actions exist — OSV queries (`--sca`) and AI review (`--use-ai`) — and both must be switched on explicitly.
- Range versions in manifests (`^1.2.3`) are not guessed at; they are skipped and reported.
- If any target in the list is missing, the whole run is `BLOCKED`; it never "runs part of it first".

## 6. Report formats

| Format | Use | Command |
|---|---|---|
| text | Terminal reading | default |
| json | Machine consumption / archive | `--format json --out audit.json` |
| sarif | GitHub Code Scanning | `--format sarif --out results.sarif` |

SARIF level mapping: hardcoded credentials / `eval` / disabled certificate checks → `error`; everything else → `warning` / `note`.

## 7. When not to use it

- No authorization and the target is not your own asset — the gate will stop you; don't work around it with environment variables.
- When finding snippets are not allowed to leave the machine, don't turn on `--use-ai`.
