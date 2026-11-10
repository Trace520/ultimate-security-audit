"""能力探测脚本冒烟。"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_skill_probe_runs():
    proc = subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / "skill_probe.py")],
        capture_output=True, encoding="utf-8", check=True, cwd=str(ROOT),
    )
    data = json.loads(proc.stdout)
    assert set(data) >= {"rea-leanrea-router", "context-mode", "rg", "grep"}
    assert all(isinstance(v, bool) for v in data.values())
