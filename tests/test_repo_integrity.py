"""文档里声明的入口必须真实存在。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DECLARED = [
    "SKILL.md",
    "CAPABILITIES.md",
    "CONTRIBUTING.md",
    "README.md",
    "audit_notes.md",
    "pyproject.toml",
    "Makefile",
    "references/audit-workflow.md",
    "references/audit-report.md",
    "references/authorization-and-handling.md",
    "references/ci-pipeline-mode.md",
    "references/toolchain.md",
    "references/state-machine.md",
    "references/fallback-matrix.md",
    "assets/audit_notes.template.md",
    "scripts/__init__.py",
    "scripts/__main__.py",
    "scripts/run_audit.py",
    "scripts/project_probe.py",
    "scripts/skill_probe.py",
    "scripts/check_docs.py",
    "scripts/dep_scanner.py",
    "scripts/state_manager.py",
    "scripts/report_formatter.py",
    "tests/fixtures/sample/sample_code.js",
    "tests/fixtures/expected_report.json",
    "tests/sandbox_test.py",
    "tests/test_golden.py",
    "tests/test_repo_integrity.py",
    "tests/test_skill_probe.py",
    "tests/test_state_machine.py",
    "tests/test_report_formatter.py",
    "tests/test_dep_scanner.py",
    "examples/sample_code.js",
    "examples/audit_report.md",
    "examples/verify_xor_key.py",
]


def test_declared_entrypoints_exist():
    for rel in DECLARED:
        assert (ROOT / rel).exists(), f"声明存在但缺失: {rel}"


def test_version_consistent_across_three_places():
    """版本号三处必须一致：pyproject / SKILL.md frontmatter / run_audit.VERSION。"""
    import re

    py = re.search(r'^version = "(\d+\.\d+\.\d+)"', (ROOT / "pyproject.toml").read_text(encoding="utf-8"), re.M)
    sk = re.search(r"^version: (\S+)$", (ROOT / "SKILL.md").read_text(encoding="utf-8"), re.M)
    code = re.search(r'VERSION = "(\S+)"', (ROOT / "scripts/run_audit.py").read_text(encoding="utf-8"))
    assert py and sk and code, "版本号声明缺失"
    assert {py.group(1), sk.group(1), code.group(1)} == {py.group(1)}, "版本号不一致"


def test_skill_name_matches_repo():
    """SKILL.md 的 name 必须等于仓库名，否则按名字加载会找不到目录。"""
    import re

    text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    name = re.search(r"^name: (\S+)$", text, re.M)
    assert name and name.group(1) == "ultimate-security-audit"
