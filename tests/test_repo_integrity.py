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
    "assets/audit_notes.template.md",
    "scripts/__init__.py",
    "scripts/run_audit.py",
    "scripts/project_probe.py",
    "scripts/skill_probe.py",
    "scripts/check_docs.py",
    "tests/fixtures/sample/sample_code.js",
    "tests/fixtures/expected_report.json",
    "tests/sandbox_test.py",
    "tests/test_golden.py",
    "tests/test_repo_integrity.py",
    "tests/test_skill_probe.py",
    "examples/sample_code.js",
    "examples/audit_report.md",
    "examples/verify_xor_key.py",
]


def test_declared_entrypoints_exist():
    for rel in DECLARED:
        assert (ROOT / rel).exists(), f"声明存在但缺失: {rel}"
