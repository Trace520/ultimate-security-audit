#!/usr/bin/env python3
"""阶段一扫描引擎：按规则匹配可疑模式，输出确定性 JSON。

- 只读：不执行目标代码、不联网、不修改目标文件。
- 支持目录与单文件两种目标；目录递归，单文件只扫自身。
- 授权判定不在这里做，由 ``scripts/run_audit.py`` 门控后调用；
  单独运行本脚本意味着调用者已自行承担授权责任。
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BINARY_SUFFIX = {
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".ico", ".pdf", ".zip", ".gz",
    ".tar", ".exe", ".dll", ".so", ".dylib", ".pyc", ".class", ".woff",
    ".woff2", ".ttf", ".asar",
}
SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
    ".pytest_cache", ".mypy_cache", "site-packages",
}

# (rule_id, 正则, 说明)
RULES = [
    ("HARDCODED_SECRET",
     re.compile(r"\bsecret_key_[A-Za-z0-9]+\b"),
     "硬编码密钥字面量"),
    ("HARDCODED_KEY_VAR",
     re.compile(r"(?i)\b(api_key|apikey|access_key|secret|token|password|passwd)\b"
                r"\s*[:=]\s*[\"'][^\"']{6,}[\"']"),
     "疑似硬编码凭据赋值"),
    ("EVAL_USAGE",
     re.compile(r"\beval\s*\("),
     "动态代码执行"),
    ("FUNCTION_CTOR",
     re.compile(r"new\s+Function\s*\("),
     "Function 构造器"),
    ("CHILD_PROCESS",
     re.compile(r"child_process|subprocess\.(?:run|call|Popen)|os\.system\s*\("),
     "外部进程调用"),
    ("TLS_VERIFY_OFF",
     re.compile(r"rejectUnauthorized\s*:\s*false|verify\s*=\s*False|InsecureSkipVerify"),
     "关闭证书校验"),
    ("XSS_SINK",
     re.compile(r"innerHTML\s*=|dangerouslySetInnerHTML"),
     "HTML 注入 sink"),
    ("SQL_CONCAT",
     re.compile(r"(?i)(?:select|insert|update|delete)\s[^;\n]{0,80}\+"),
     "疑似 SQL 字符串拼接"),
    ("PLAINTEXT_HTTP",
     re.compile(r"http://[^\s\"'<>]+"),
     "明文 HTTP 地址"),
    ("DEBUG_ENABLED",
     re.compile(r"DEBUG\s*[:=]\s*(?:True|true)|debug\s*:\s*true"),
     "调试开关默认开启"),
]


def _rel(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.name


def _iter_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    out: list[Path] = []
    for p in sorted(target.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() in BINARY_SUFFIX:
            continue
        if any(part in SKIP_DIRS for part in p.relative_to(target).parts):
            continue
        out.append(p)
    return out


def scan(target: Path) -> list[dict]:
    """扫描单个目标（目录或文件），返回 findings 列表。"""
    base = target.parent if target.is_file() else target
    findings: list[dict] = []
    for path in _iter_files(target):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for rule_id, pattern, _ in RULES:
                m = pattern.search(line)
                if not m:
                    continue
                snippet = m.group(0)
                if len(snippet) > 60:
                    snippet = snippet[:57] + "..."
                findings.append({
                    "file": _rel(path, base),
                    "line": line_no,
                    "rule": rule_id,
                    "match": snippet.strip(),
                })
                break  # 每行只记一条，避免同一行多次命中把表格撑爆
    return findings


def main() -> int:
    ap = argparse.ArgumentParser(description="阶段一静态扫描")
    ap.add_argument("target", help="目标目录或单个文件")
    ap.add_argument("--json", action="store_true", help="只输出 JSON")
    a = ap.parse_args()

    target = Path(a.target).resolve()
    if not target.exists():
        print(json.dumps({"error": "target_not_found", "target": str(target)},
                         ensure_ascii=False))
        return 2

    findings = scan(target)
    if a.json:
        print(json.dumps({"target": str(target), "findings": findings},
                         ensure_ascii=False))
    else:
        for f in findings:
            print(f"{f['file']}:{f['line']} [{f['rule']}] {f['match']}")
        print(f"[probe] {len(findings)} 条可疑模式")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
