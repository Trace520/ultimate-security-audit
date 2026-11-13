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
from fnmatch import fnmatchcase
from pathlib import Path
from urllib.parse import urlsplit

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
     re.compile(r"\bsecret_key_\w*[A-Za-z0-9]\b"),
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


# 明文 HTTP 的噪声源：回环地址与示例域名。它们几乎必然出现在测试、
# 文档与脚手架里，报出来只会把真实命中淹没（一个 Juice Shop 量级的前端
# 光 localhost 就能刷出几百条），因此在阶段一直接丢弃。
_NOISE_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1",
                "example.com", "example.org", "example.net", "example.local"}
_NOISE_SUFFIXES = (".example.com", ".example.org", ".example.net",
                   ".example.local", ".test", ".invalid", ".localhost")


def _is_noise_http(snippet: str) -> bool:
    """判断命中里的主机名是否属于「回环 / 示例」噪声。"""
    try:
        host = (urlsplit(snippet.strip()).hostname or "").lower()
    except ValueError:
        return False
    if not host:
        return False
    return host in _NOISE_HOSTS or host.endswith(_NOISE_SUFFIXES)


def _rel(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.name


def _iter_files(target: Path, exclude: tuple[str, ...] = ()) -> list[Path]:
    """枚举待扫文件；``exclude`` 是相对路径 glob（用 fnmatch 语义）。

    第三方 bundle（如打包后的 three.js）一条文件就能刷出上千条明文 HTTP 命中，
    必须能在网关层整体排除，否则报告等于不可读。
    """
    if target.is_file():
        rel, name = _rel(target, target.parent), target.name
        return [] if _excluded(rel, name, exclude) else [target]
    out: list[Path] = []
    for p in sorted(target.rglob("*")):
        if not p.is_file():
            continue
        if p.suffix.lower() in BINARY_SUFFIX:
            continue
        rel = p.relative_to(target)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        if _excluded(rel.as_posix(), p.name, exclude):
            continue
        out.append(p)
    return out


def _excluded(rel: str, name: str, exclude: tuple[str, ...]) -> bool:
    return any(fnmatchcase(rel, pat) or fnmatchcase(name, pat) for pat in exclude)


def scan(target: Path, *, exclude: tuple[str, ...] = ()) -> list[dict]:
    """扫描单个目标（目录或文件），返回 findings 列表。

    ``exclude``：相对路径 glob 黑名单，命中的文件整份跳过（不读取）。
    """
    base = target.parent if target.is_file() else target
    findings: list[dict] = []
    for path in _iter_files(target, exclude):
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
                if rule_id == "PLAINTEXT_HTTP" and _is_noise_http(snippet):
                    continue  # 回环 / 示例域名：降噪，不算命中
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
    ap.add_argument("--exclude", action="append", default=None, metavar="GLOB",
                    help="跳过相对路径匹配该 glob 的文件（可重复）")
    a = ap.parse_args()

    target = Path(a.target).resolve()
    if not target.exists():
        print(json.dumps({"error": "target_not_found", "target": str(target)},
                         ensure_ascii=False))
        return 2

    findings = scan(target, exclude=tuple(a.exclude or ()))
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
