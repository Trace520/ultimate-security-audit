"""状态机必须能拦住跳步与「未核实就出报告」。"""
from pathlib import Path

import state_manager


def _findings():
    return [
        {"file": "a.js", "line": 5, "rule": "HARDCODED_SECRET", "match": "x"},
        {"file": "b.py", "line": 9, "rule": "EVAL_USAGE", "match": "y"},
    ]


def test_verify_requires_discovery(tmp_path: Path):
    st = tmp_path / "state.json"
    ok, why, _ = state_manager.advance(st, "verify", approval="CHG-1", targets=["t"],
                                       verified=["a.js:5:HARDCODED_SECRET"])
    assert not ok and "discovery" in why


def test_discovery_then_verify_without_covering_all_is_blocked(tmp_path: Path):
    st = tmp_path / "state.json"
    ok, _, _ = state_manager.advance(st, "discovery", approval="CHG-1", targets=["t"],
                                     findings=_findings())
    assert ok
    ok, why, _ = state_manager.advance(st, "verify", approval="CHG-1", targets=["t"],
                                       verified=["a.js:5:HARDCODED_SECRET"])
    assert not ok and "未核实" in why


def test_full_path_and_waive(tmp_path: Path):
    st = tmp_path / "state.json"
    state_manager.advance(st, "discovery", approval="CHG-1", targets=["t"],
                          findings=_findings())
    ok, why, _ = state_manager.advance(
        st, "verify", approval="CHG-1", targets=["t"],
        verified=["a.js:5:HARDCODED_SECRET"], waived=["b.py:9:EVAL_USAGE"])
    assert ok, why
    ok, why, state = state_manager.advance(st, "report", approval="CHG-1", targets=["t"])
    assert ok, why
    assert state["stage"] == "report"


def test_report_without_verify_is_blocked(tmp_path: Path):
    st = tmp_path / "state.json"
    state_manager.advance(st, "discovery", approval="CHG-1", targets=["t"],
                          findings=_findings())
    ok, why, _ = state_manager.advance(st, "report", approval="CHG-1", targets=["t"])
    assert not ok and "verify" in why


def test_approval_mismatch_is_blocked(tmp_path: Path):
    st = tmp_path / "state.json"
    state_manager.advance(st, "discovery", approval="CHG-1", targets=["t"],
                          findings=_findings())
    ok, why, _ = state_manager.advance(st, "verify", approval="CHG-2", targets=["t"],
                                       verified=[], waived=[])
    assert not ok and "不一致" in why
