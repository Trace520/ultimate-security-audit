"""SCA 只认精确版本，且离线时必须降级而不是编造命中。"""
import json
from pathlib import Path

import dep_scanner


def test_collect_requirements_and_lock(tmp_path: Path):
    (tmp_path / "requirements.txt").write_text(
        "# comment\nrequests==2.19.0\nflask>=2.0  # 范围，不该被当成精确版本\n"
        "-r other.txt\nurllib3==1.26.5 ; python_version>='3.8'\n", encoding="utf-8")
    (tmp_path / "package-lock.json").write_text(json.dumps({
        "packages": {"node_modules/lodash": {"version": "4.17.15"}},
        "dependencies": {"minimist": {"version": "1.2.5"}},
    }), encoding="utf-8")
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "package.json").write_text(
        '{"dependencies": {"express": "^4.0.0"}}', encoding="utf-8")

    pkgs, notes = dep_scanner.collect([tmp_path])
    got = {(p["name"], p["version"], p["ecosystem"]) for p in pkgs}
    assert ("requests", "2.19.0", "PyPI") in got
    assert ("urllib3", "1.26.5", "PyPI") in got
    assert ("lodash", "4.17.15", "npm") in got
    assert ("minimist", "1.2.5", "npm") in got
    assert not any(p["name"] == "flask" for p in pkgs)      # 范围版不查
    assert not any(p["name"] == "express" for p in pkgs)    # 无 lock 不查
    assert any("package.json" in n for n in notes)


def test_offline_degrades_without_findings(tmp_path: Path, monkeypatch):
    (tmp_path / "requirements.txt").write_text("requests==2.19.0\n", encoding="utf-8")

    def boom(*args, **kwargs):
        raise OSError("no network")

    monkeypatch.setattr(dep_scanner.urllib.request, "urlopen", boom)
    findings, err, notes = dep_scanner.scan([tmp_path])
    assert findings == []
    assert "OSV 不可达" in err


def test_no_pinned_dependency_means_no_query(tmp_path: Path):
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    findings, err, notes = dep_scanner.scan([tmp_path])
    assert findings == [] and err == ""
    assert any("未找到" in n for n in notes)
