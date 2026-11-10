"""SARIF 输出必须是合法的 2.1.0 文档，且每条命中都能定位到文件与行。"""
import json
import os
from pathlib import Path

import report_formatter

# 会被 run_audit 当作 CI 上下文的环境变量：存在时状态从 DEGRADED 升为 EXECUTE，
# 测试里必须清掉，否则同一条用例在本地绿、在 GitHub/GitLab/Jenkins 上红。
CI_ENV_KEYS = {
    "CI", "GITHUB_ACTIONS", "GITHUB_SHA", "GITHUB_RUN_ID",
    "GITLAB_CI", "CI_COMMIT_SHA", "CI_PIPELINE_ID",
    "JENKINS_URL", "JENKINS_HOME", "GIT_COMMIT", "BUILD_ID",
    "AUTHORIZATION_MODE", "AUDIT_APPROVAL_ID", "AUDIT_TARGETS",
    "AUDIT_COMMIT_SHA", "AUDIT_RUN_ID",
}


def _clean_env() -> dict:
    return {k: v for k, v in os.environ.items() if k not in CI_ENV_KEYS}


def test_sarif_shape_and_locations():
    findings = [
        {"file": "src/a.js", "line": 5, "rule": "HARDCODED_SECRET", "match": "secret_key_123"},
        {"file": "requirements.txt", "line": 1, "rule": "DEP_VULN", "match": "urllib3==1.26.0 CVE-2021-1"},
    ]
    doc = report_formatter.to_sarif(findings, version="3.0.0")
    assert doc["version"] == "2.1.0"
    assert doc["$schema"].endswith("sarif-2.1.0.json")

    run = doc["runs"][0]
    assert run["tool"]["driver"]["name"] == "ultimate-security-audit"
    assert run["tool"]["driver"]["version"] == "3.0.0"

    rule_ids = {r["id"] for r in run["tool"]["driver"]["rules"]}
    assert rule_ids == {"HARDCODED_SECRET", "DEP_VULN"}

    assert len(run["results"]) == 2
    first = run["results"][0]
    assert first["ruleId"] == "HARDCODED_SECRET"
    assert first["level"] == "error"
    assert first["locations"][0]["physicalLocation"]["region"]["startLine"] == 5
    assert first["locations"][0]["physicalLocation"]["artifactLocation"]["uri"] == "src/a.js"


def test_empty_findings_is_valid():
    doc = report_formatter.to_sarif([], version="3.0.0")
    assert doc["runs"][0]["results"] == []
    serialized = json.dumps(doc, ensure_ascii=False)
    assert "results" in serialized


def test_cli_json_out_writes_file(tmp_path):
    """--format json --out 必须真的落盘，否则 README 的示例就是假的。"""
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[1]
    out = tmp_path / "audit.json"
    proc = subprocess.run(
        [sys.executable, "-B", str(root / "scripts" / "run_audit.py"),
         str(root / "tests" / "fixtures" / "sample"),
         "--approval-id", "CHG-TEST-0001", "--format", "json",
         "--out", str(out), "--allow-findings"],
        capture_output=True, text=True, env=_clean_env(),
    )
    assert out.exists(), proc.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["status"] == "DEGRADED"
    assert len(data["findings"]) == 1
