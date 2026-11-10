"""冒烟测试：验证门控 + 阶段一 + 落盘最小可运行。"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _run(extra_env: dict, outs: list[str]) -> subprocess.CompletedProcess:
    env = {**os.environ, **extra_env}
    return subprocess.run(
        [sys.executable, "-B", str(ROOT / "scripts" / "run_audit.py"),
         "--targets", str(ROOT / "tests" / "fixtures" / "sample"),
         "--json", "--allow-findings", "--notes", outs[0]],
        capture_output=True, encoding="utf-8", env=env, cwd=str(ROOT),
    )


def main() -> int:
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True, check=True).stdout.strip()
    with tempfile.TemporaryDirectory() as td:
        notes = str(Path(td) / "audit_notes.md")

        # 1) 缺审批号必须 fail-closed
        proc = _run({"AUTHORIZATION_MODE": "CI_PIPELINE", "AUDIT_APPROVAL_ID": ""},
                    [notes])
        if proc.returncode != 2:
            print(f"期望 exit 2，实际 {proc.returncode}\n{proc.stderr}", file=sys.stderr)
            return 1

        # 2) 三项齐备时 EXECUTE 且有命中
        proc = _run({"AUTHORIZATION_MODE": "CI_PIPELINE",
                     "AUDIT_APPROVAL_ID": "CHG-SMOKE-0001",
                     "GITHUB_ACTIONS": "true", "GITHUB_SHA": head,
                     "GITHUB_RUN_ID": "smoke"}, [notes])
        if proc.returncode != 0:
            print(proc.stderr, file=sys.stderr)
            return 1
        last = [ln for ln in (proc.stdout or "").splitlines()
                if ln.strip().startswith("{")][-1]
        data = json.loads(last)
        assert data["status"] == "EXECUTE", data
        assert data["findings"], "应至少命中一条 finding"
        assert Path(notes).exists(), "证据笔记未落盘"
    print("sandbox_test: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
