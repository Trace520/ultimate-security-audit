"""示例报告与 fixture 严格一致 —— 样本命中一变，本测试必红。"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures"


def _head() -> str:
    return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()


def test_report_matches_golden(tmp_path):
    env = {
        **os.environ,
        "AUTHORIZATION_MODE": "CI_PIPELINE",
        "AUDIT_APPROVAL_ID": "CHG-TEST-0001",
        "GITHUB_ACTIONS": "true",
        "GITHUB_SHA": _head(),
        "GITHUB_RUN_ID": "test",
    }
    proc = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / "run_audit.py"),
         "--targets", str(FIX / "sample"), "--json", "--allow-findings",
         "--notes", str(tmp_path / "audit_notes.md")],
        capture_output=True, encoding="utf-8", env=env, cwd=str(ROOT),
    )
    assert proc.returncode == 0, proc.stderr

    last = [ln for ln in (proc.stdout or "").splitlines()
            if ln.strip().startswith("{")][-1]
    actual = json.loads(last)
    expected = json.loads((FIX / "expected_report.json").read_text(encoding="utf-8"))
    assert actual == expected, (
        "示例报告与 fixture 不一致，请重新生成：\n"
        "  make regen-fixture"
    )
