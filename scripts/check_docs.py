#!/usr/bin/env python3
"""扫描 Markdown 行内代码里的相对路径，校验其真实存在。

设计要点（上一版按仓库根解析、把所有带点的 token 都当路径，实测误报 60 处）：

- **相对当前 md 所在目录解析**，其次才按仓库根解析 —— ``SKILL.md`` 里写的
  ``references/audit-workflow.md`` 是相对 ``references/`` 的兄弟目录。
- 只校验**看起来像仓库内文件**的 token：带已知后缀，或以 ``/`` 结尾的目录。
  像 ``console.log`` / ``String.fromCharCode`` / ``vars.AUDIT_APPROVAL_ID``
  这类标识符直接跳过。
- 跳过运行时产物、外部路径、命令、版本号、通配符与 URL。
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INLINE = re.compile(r"`([^`\n]+)`")

KNOWN_SUFFIXES = {
    ".md", ".py", ".js", ".json", ".yml", ".yaml", ".toml", ".txt",
    ".sh", ".cfg", ".ini", ".jsx", ".ts", ".tmpl",
}
SKIP_PARTS = {".git", "node_modules", ".pytest_cache", "build", "dist",
              "__pycache__", ".venv", "venv", "site-packages"}
# 运行时产物 / 外部仓库路径 / 已知非本仓库文件
SKIP_EXACT = {
    "audit_notes.md", "audit_notes.local.md", "notes-exec.md",
    "references/decision-matrix.md",
    # 运行产物 / 被测对象的依赖清单：真实存在但不在本仓库
    "results.sarif", "audit.json", ".audit-state.json",
    "requirements.txt", "requirements-dev.txt", "package-lock.json", "package.json",
}
BAD_CHARS = set(' ;<>{}()|*$\\"\'')
COMMANDS = ("pip", "pip3", "python", "python3", "git", "make", "npm", "npx",
            "docker", "bash", "sh", "cd", "export", "pytest", "rg", "grep",
            "ls", "cat", "echo", "curl", "chmod", "chown")
VERSION = re.compile(r"^v?\d+(?:\.\d+)+(?:[a-z]\d*)?$")


def _is_candidate(tok: str) -> bool:
    if not tok or tok in SKIP_EXACT:
        return False
    if any(c in BAD_CHARS for c in tok):
        return False
    if tok.startswith(("http", "~", "/", "#", "-", "!")):
        return False
    head = tok.split("/", 1)[0]
    if head.split(" ", 1)[0] in COMMANDS:
        return False
    if VERSION.match(tok):
        return False
    if tok.endswith("/"):
        return True
    return Path(tok).suffix in KNOWN_SUFFIXES


def check_file(md: Path) -> int:
    bad = 0
    in_fence = False
    for ln, line in enumerate(md.read_text(encoding="utf-8").splitlines(), 1):
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for tok in INLINE.findall(line):
            tok = tok.strip()
            if not _is_candidate(tok):
                continue
            rel = tok.rstrip("/")
            if not rel:
                continue
            if (md.parent / rel).exists() or (ROOT / rel).exists():
                continue
            print(f"{md.relative_to(ROOT)}:{ln}: 引用了不存在的路径 `{tok}`")
            bad += 1
    return bad


def main() -> int:
    bad = 0
    for md in sorted(ROOT.rglob("*.md")):
        if any(part in SKIP_PARTS for part in md.relative_to(ROOT).parts):
            continue
        bad += check_file(md)
    if bad:
        print(f"\n[check_docs] 共 {bad} 处死链，请修复后重试。")
        return 1
    print("[check_docs] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
