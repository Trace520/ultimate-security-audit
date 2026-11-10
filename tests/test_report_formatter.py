"""SARIF 输出必须是合法的 2.1.0 文档，且每条命中都能定位到文件与行。"""
import json

import report_formatter


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
