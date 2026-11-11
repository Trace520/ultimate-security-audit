#!/usr/bin/env python3
"""审计入口：授权门控（fail-closed）→ 阶段一扫描 → 证据笔记落盘。

门控判据见 ``references/ci-pipeline-mode.md``：

- **EXECUTE**：模式开关、审批编号、目标清单三项齐备，目标全部落在仓库根内，
  且 CI 声明的 commit 与本地 HEAD 一致。
- **DEGRADED**：三项齐备但无 CI 上下文，或 commit 与 HEAD 不一致 —— 只做阶段一。
- **BLOCKED**：缺字段 / 占位值 / 目标越界或不存在 / 读不到本地 HEAD。
  **退出码 2，且不打开任何目标文件。**

两种用法：CI 流水线（环境变量注入），或交互式命令行 ``usa <target> --approval-id <ID>``；
后者没有 CI 上下文，必然降为 DEGRADED，只做阶段一。
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
EXIT_OK, EXIT_FINDINGS, EXIT_BLOCKED = 0, 1, 2

sys.path.insert(0, str(SCRIPTS))

import dep_scanner  # noqa: E402
import report_formatter  # noqa: E402
import state_manager  # noqa: E402

VERSION = "3.0.0"

PLACEHOLDER_APPROVAL = {
    "tbd", "todo", "none", "null", "n/a", "na", "-", "0000", "00000",
    "changeme", "example", "xxx", "placeholder",
}


def _env(name: str) -> str:
    return (os.environ.get(name) or "").strip()


def detect_ci() -> tuple[str, str]:
    """返回 (平台名, CI 声明的 commit)。平台名 ``none`` 表示无 CI 上下文。"""
    if _env("GITHUB_ACTIONS").lower() == "true" or _env("GITHUB_SHA"):
        return "github", _env("GITHUB_SHA")
    if _env("GITLAB_CI").lower() == "true":
        return "gitlab", _env("CI_COMMIT_SHA")
    if _env("JENKINS_URL") or _env("JENKINS_HOME"):
        return "jenkins", _env("GIT_COMMIT")
    if _env("CI") and _env("CI").lower() != "false":
        return "other", ""
    return "none", ""


def head_sha(root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.stdout.strip() or None


def split_targets(raw: str) -> list[str]:
    for sep in ("\n", ","):
        raw = raw.replace(sep, ";")
    return [item.strip().strip('"').strip("'") for item in raw.split(";") if item.strip()]


def resolve_targets(specs: list[str], root: Path) -> tuple[list[Path], str | None]:
    resolved: list[Path] = []
    for spec in specs:
        p = Path(spec)
        if not p.is_absolute():
            p = root / p
        p = p.resolve()
        if not p.exists():
            return [], f"目标不存在: {spec}"
        if not p.is_relative_to(root):
            return [], f"目标越界（不在仓库根 {root} 内）: {spec}"
        resolved.append(p)
    return resolved, None


def write_notes(path: Path, *, approval: str, targets: list[str], ci: str,
                run_id: str, status: str, findings: list[dict], reason: str) -> None:
    lines = [
        "# Audit Notes",
        "",
        f"> 生成时间：{datetime.now(timezone.utc).astimezone().isoformat(timespec='seconds')}",
        f"> 判定结果：`{status}`" + (f"（{reason}）" if reason else ""),
        "",
        "## 授权段",
        "",
        "| 字段 | 值 |",
        "|---|---|",
        f"| 授权模式 | {_env('AUTHORIZATION_MODE') or '（缺失）'} |",
        f"| 审批编号 | {approval or '（缺失）'} |",
        f"| 审计目标 | {', '.join(targets) if targets else '（缺失）'} |",
        f"| 范围说明 | {_env('AUDIT_SCOPE_NOTE') or '（未提供）'} |",
        f"| CI 平台 | {ci} |",
        f"| 运行 ID | {run_id or '（无）'} |",
        "",
        "## 阶段一命中（project_probe）",
        "",
    ]
    if findings:
        lines += ["| 文件:行 | 规则 | 片段 |", "|---|---|---|"]
        for f in findings:
            lines.append(f"| `{f['file']}:{f['line']}` | {f['rule']} | `{f['match']}` |")
    else:
        lines.append("无命中。")
    lines += [
        "",
        "## 未执行的阶段",
        "",
        "- 阶段二（动态抓包 / 反混淆 / 证据固化）：未执行。",
        "- 阶段三（深度审计 / 伪代码还原）：未执行。",
        "",
        "> 阶段一命中只是「可疑模式」，是否成立、可达性、影响面须按阶段二 / 三复核，",
        "> 本脚本不对命中做定性背书。",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="Ultimate Security Audit — 门控 + 阶段一")
    ap.add_argument("target", nargs="*",
                    help="目标（可多个），等价于 --targets")
    ap.add_argument("--targets", default=None,
                    help="目标清单，分号 / 逗号 / 换行分隔；缺省读 AUDIT_TARGETS")
    ap.add_argument("--approval-id", default=None,
                    help="审批编号，等价于 AUDIT_APPROVAL_ID；交互式命令行使用")
    ap.add_argument("--repo-root", default=None, help="目标必须落在该目录内")
    ap.add_argument("--notes", default=None,
                    help="证据笔记输出路径，默认 audit_notes.local.md")
    ap.add_argument("--json", action="store_true", help="stdout 只输出单行 JSON")
    ap.add_argument("--allow-findings", action="store_true",
                    help="有命中仍返回 0（供冒烟测试）")
    ap.add_argument("--strict", action="store_true",
                    help="外部能力缺失时直接 BLOCKED（退出码 2）")
    ap.add_argument("--format", choices=["text", "json", "sarif"], default=None,
                    help="输出格式，默认 text；--format sarif 供 Code Scanning")
    ap.add_argument("--out", default=None, help="SARIF / JSON 输出文件路径")
    ap.add_argument("--stage", choices=list(state_manager.STAGES), default=None,
                    help="推进防幻觉状态机：discovery → verify → report")
    ap.add_argument("--verify", action="append", default=None,
                    help="verify 阶段核实的 finding id（可重复）")
    ap.add_argument("--verify-all", action="store_true",
                    help="verify 阶段一次性声明全部已核实（需人工确认后再用）")
    ap.add_argument("--waive", action="append", default=None,
                    help="明确放弃的 finding id（与 --verify 二选一）")
    ap.add_argument("--state", default=None,
                    help="状态文件，默认 .audit-state.json")
    ap.add_argument("--sca", action="store_true",
                    help="额外跑依赖漏洞扫描（OSV，需要网络；失败降级不编造）")
    ap.add_argument("--use-ai", action="store_true",
                    help="对本地命中做 AI 复核（需 OPENROUTER_API_KEY；失败降级、命中保留）")
    a = ap.parse_args()
    fmt = "json" if a.json else (a.format or "text")

    root = Path(a.repo_root).resolve() if a.repo_root else ROOT
    approval = (a.approval_id or "").strip() or _env("AUDIT_APPROVAL_ID")
    interactive = bool(a.approval_id) and bool(a.target or a.targets)
    if a.targets is not None:
        raw_targets = a.targets
    elif a.target:
        raw_targets = ";".join(a.target)
    else:
        raw_targets = _env("AUDIT_TARGETS")
    specs = split_targets(raw_targets)
    ci, ci_sha = detect_ci()
    run_id = (_env("GITHUB_RUN_ID") or _env("CI_PIPELINE_ID")
              or _env("BUILD_ID") or "")

    blocked: list[str] = []
    if _env("AUTHORIZATION_MODE").upper() != "CI_PIPELINE" and not interactive:
        blocked.append("AUTHORIZATION_MODE=CI_PIPELINE 或 --approval-id + 目标")
    if not approval or approval.lower() in PLACEHOLDER_APPROVAL:
        blocked.append("AUDIT_APPROVAL_ID")
    if not specs:
        blocked.append("AUDIT_TARGETS")

    targets: list[Path] = []
    if not blocked:
        targets, err = resolve_targets(specs, root)
        if err:
            blocked.append(err)

    head = head_sha(root) if ci != "none" else None
    if not blocked and ci != "none" and head is None:
        blocked.append("本地 HEAD 不可读（git rev-parse HEAD 失败）")

    findings: list[dict] = []
    status = "BLOCKED"
    reason = ""
    if blocked:
        reason = "; ".join(blocked)
        print(f"[AUDIT_MODE: BLOCKED | missing: {reason}]", file=sys.stderr)
        print("补齐方式：在流水线里注入上述字段（不要写成字面量），"
              "字段说明见 references/ci-pipeline-mode.md。", file=sys.stderr)
    else:
        status = "EXECUTE"
        if a.strict:
            from skill_probe import probe  # noqa: PLC0415

            missing = [k for k, v in probe().items() if not v]
            if missing:
                status = "BLOCKED"
                reason = f"external_capabilities_missing: {', '.join(missing)}"
                print(f"[AUDIT_MODE: BLOCKED | missing: {reason}]", file=sys.stderr)

        if status == "EXECUTE":
            if ci == "none":
                status, reason = "DEGRADED", "无 CI 上下文，来源不可追溯"
            elif ci_sha and head and ci_sha != head:
                status, reason = "DEGRADED", (
                    f"commit 漂移: CI 声明 {ci_sha[:12]}, 本地 HEAD {head[:12]}")

            import project_probe  # noqa: PLC0415

            for t in targets:
                findings.extend(project_probe.scan(t))

            header = (f"[AUDIT_MODE: {status} | approval: {approval} | "
                      f"targets: {len(targets)} | ci: {ci} | run: {run_id or '-'}]")
            if status == "DEGRADED":
                header = header[:-1] + " | status: DEGRADED]"
            print(header, file=sys.stderr) if fmt != "text" else print(header)
            if fmt == "text":
                for f in findings:
                    print(f"  {f['file']}:{f['line']} [{f['rule']}] {f['match']}")
                print(f"[*] 扫描目标 {len(targets)} 个，可疑模式命中 {len(findings)} 条")

    warnings: list[str] = []

    # SCA：可选，唯一会联网的一步；拿不到数据就降级，不编造
    if status != "BLOCKED" and a.sca:
        dep_findings, dep_err, dep_notes = dep_scanner.scan(targets)
        findings.extend(dep_findings)
        warnings.extend(dep_notes)
        if dep_err:
            warnings.append(dep_err)
            if status == "EXECUTE":
                status, reason = "DEGRADED", dep_err

    # AI 研判：可选的第二层，只复核、不改判定；拿不到就降级，命中一律保留
    if status != "BLOCKED" and a.use_ai and findings:
        import llm_analyzer  # noqa: PLC0415

        findings, ai_notes = llm_analyzer.refine(
            findings, progress=lambda m: print(f"[ai] {m}", file=sys.stderr))
        warnings.extend(ai_notes)

    # 状态机：显式给 --stage 才强制，单次扫描保持向后兼容
    state_path = Path(a.state) if a.state else Path(state_manager.DEFAULT_STATE)
    state_info = ""
    if a.stage and status != "BLOCKED":
        verified = list(a.verify or [])
        if a.verify_all:
            verified = state_manager.load(state_path).get("discovery_ids", [])
        ok, why, st = state_manager.advance(
            state_path, a.stage,
            approval=approval, targets=specs,
            findings=findings if a.stage == "discovery" else None,
            verified=verified, waived=list(a.waive or []),
        )
        state_info = state_manager.status_line(st)
        if not ok:
            status = "BLOCKED"
            reason = why
            print(f"[AUDIT_MODE: BLOCKED | missing: {why}]", file=sys.stderr)
        else:
            print(f"[STATE] {state_info}", file=sys.stderr)

    notes = Path(a.notes) if a.notes else Path("audit_notes.local.md")
    write_notes(notes, approval=approval, targets=specs, ci=ci, run_id=run_id,
                status=status, findings=findings, reason=reason)

    report = {
        "status": status,
        "targets": len(targets),
        "findings": findings,
        "warnings": [] if status == "EXECUTE" else [
            {"code": status, "reason": reason, "missing": blocked}],
    }
    report["warnings"].extend({"code": "NOTE", "reason": w} for w in warnings)

    if fmt == "sarif":
        out = Path(a.out) if a.out else Path("results.sarif")
        doc = report_formatter.to_sarif(
            findings, version=VERSION, warnings=warnings,
            invocation_uri=" ".join(sys.argv))
        report_formatter.write(out, doc)
        print(f"[*] SARIF：{out}（{len(findings)} 条结果）")
    elif fmt == "json":
        payload = json.dumps(report, ensure_ascii=False)
        if a.out:
            out = Path(a.out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(payload, encoding="utf-8")
            print(f"[*] JSON：{out}（{len(findings)} 条结果）")
        else:
            print(payload)
    elif status != "BLOCKED":
        summary = report_formatter.summarize(findings)
        print(f"[*] 证据笔记：{notes}")
        print(f"[*] 分级：error {summary['error']} / warning {summary['warning']}"
              f" / note {summary['note']}")
        if state_info:
            print(f"[*] 状态机：{state_info}")

    if status == "BLOCKED":
        return EXIT_BLOCKED
    if findings and not a.allow_findings:
        return EXIT_FINDINGS
    return EXIT_OK


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:  # 被 head / more 截断时不打一堆红字
        sys.exit(0)
