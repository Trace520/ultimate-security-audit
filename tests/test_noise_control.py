"""--exclude 与 --baseline：存量治理必须真的能落盘、能抑制、能只报新增。"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / "scripts" / "run_audit.py"

# 会把状态从 DEGRADED 升为 EXECUTE 的变量，测试里必须清掉
CI_ENV_KEYS = {
    "CI", "GITHUB_ACTIONS", "GITHUB_SHA", "GITHUB_RUN_ID",
    "GITLAB_CI", "CI_COMMIT_SHA", "CI_PIPELINE_ID",
    "JENKINS_URL", "JENKINS_HOME", "GIT_COMMIT", "BUILD_ID",
    "AUTHORIZATION_MODE", "AUDIT_APPROVAL_ID", "AUDIT_TARGETS",
}


def _env() -> dict:
    return {k: v for k, v in os.environ.items() if k not in CI_ENV_KEYS}


def _run(target: Path, *args: str) -> dict:
    proc = subprocess.run(
        [sys.executable, "-B", str(RUN), str(target),
         "--approval-id", "CHG-TEST-0001", "--format", "json",
         "--repo-root", str(target.parent), "--allow-findings",
         "--notes", str(target.parent / "notes.md"), *args],
        capture_output=True, encoding="utf-8", env=_env(),
    )
    assert proc.returncode == 0, proc.stderr
    line = [ln for ln in proc.stdout.splitlines() if ln.strip().startswith("{")][-1]
    return json.loads(line)


def _project(tmp_path: Path) -> Path:
    target = tmp_path / "proj"
    (target / "vendor").mkdir(parents=True)
    (target / "app.js").write_text('const a = "http://10.0.0.5/x";\n', encoding="utf-8")
    (target / "vendor" / "bundle.js").write_text(
        'const b = "http://10.0.0.6/y";\n', encoding="utf-8")
    return target


def test_exclude_removes_vendor_findings(tmp_path):
    target = _project(tmp_path)
    full = _run(target)
    filtered = _run(target, "--exclude", "vendor/**")
    assert len(full["findings"]) == 2
    assert [f["file"] for f in filtered["findings"]] == ["app.js"]


def test_baseline_suppresses_existing_and_reports_only_new(tmp_path):
    target = _project(tmp_path)
    baseline = tmp_path / "baseline.json"

    first = _run(target, "--baseline", str(baseline), "--write-baseline")
    assert baseline.exists()
    saved = json.loads(baseline.read_text(encoding="utf-8"))
    assert saved["version"] == 1
    assert len(saved["findings"]) == 2
    assert first["findings"]  # 写基线的那次仍然完整报告

    second = _run(target, "--baseline", str(baseline))
    assert second["findings"] == []
    assert any("基线抑制 2 条" in w["reason"] for w in second["warnings"])

    # 新增一个命中 → 只报这一条
    (target / "app.js").write_text(
        'const a = "http://10.0.0.5/x";\nconst b = "http://10.0.0.7/z";\n',
        encoding="utf-8")
    third = _run(target, "--baseline", str(baseline))
    assert [f["line"] for f in third["findings"]] == [2]


def test_missing_baseline_degrades_to_full_report(tmp_path):
    target = _project(tmp_path)
    report = _run(target, "--baseline", str(tmp_path / "nope.json"))
    assert len(report["findings"]) == 2
    assert any("基线文件不存在" in w["reason"] for w in report["warnings"])
