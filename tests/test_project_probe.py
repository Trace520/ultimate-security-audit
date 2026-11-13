"""阶段一规则与降噪：命中要准，噪声要能被排除。"""
from pathlib import Path

import project_probe


def _write(root: Path, rel: str, text: str) -> None:
    target = root / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


def test_secret_key_with_underscore_is_flagged(tmp_path):
    """旧正则 \\bsecret_key_[A-Za-z0-9]+\\b 会漏掉带下划线的密钥名。"""
    _write(tmp_path, "conf.py", 'secret_key_abc_def = "x"\n')
    findings = project_probe.scan(tmp_path)
    assert [f["rule"] for f in findings] == ["HARDCODED_SECRET"]
    assert findings[0]["match"].startswith("secret_key_abc_def")


def test_plain_http_noise_hosts_are_skipped(tmp_path):
    """localhost / 示例域名不算命中，内网真实地址仍要报。"""
    _write(tmp_path, "urls.js", (
        'a = "http://localhost:3000/api"\n'
        'b = "http://127.0.0.1/dev"\n'
        'c = "http://api.example.com/v1"\n'
        'd = "http://demo.test/ping"\n'
        'f = "http://example.com/ping"\n'
        'e = "http://10.0.0.5/internal"\n'
    ))
    findings = project_probe.scan(tmp_path)
    assert [f["line"] for f in findings] == [6]  # 只有内网真实地址这一条
    assert findings[0]["match"].startswith("http://10.0.0.5")


def test_https_is_not_plaintext(tmp_path):
    _write(tmp_path, "ok.js", 'const u = "https://api.corp.example.org/x"\n')
    assert project_probe.scan(tmp_path) == []


def test_exclude_glob_skips_whole_file(tmp_path):
    """被 --exclude 命中的文件整份跳过，里面的真实命中也不出现。"""
    _write(tmp_path, "bundle.min.js", 'x = "http://10.0.0.5/a"\n')
    _write(tmp_path, "app.js", 'y = "http://10.0.0.9/b"\n')
    findings = project_probe.scan(tmp_path, exclude=("bundle.min.js",))
    assert [f["file"] for f in findings] == ["app.js"]
    assert findings[0]["match"].startswith("http://10.0.0.9")


def test_exclude_matches_nested_relative_glob(tmp_path):
    _write(tmp_path, "vendor/deep/lib.js", 'z = "http://10.0.0.7/c"\n')
    _write(tmp_path, "src/app.js", 'w = "http://10.0.0.8/d"\n')
    findings = project_probe.scan(tmp_path, exclude=("vendor/**",))
    assert {f["file"] for f in findings} == {"src/app.js"}
