#!/usr/bin/env python3
"""一次性迁移脚本：把 skill/ 与 docs/ 扁平化到仓库根。

由 .github/workflows/migrate-flat-layout.yml 在服务端执行一次，
完成提交后本脚本与工作流都会被删除。本地可用 ``--no-push`` 演练。
"""
from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys

README_OLD_TREE = """ultimate-security-audit/
├── README.md
├── LICENSE                  # MIT + 安全工具附加条款
├── Dockerfile
├── skill/
│   ├── SKILL.md             # 主控指令（V2.3.0，渐进披露）
│   ├── references/          # 按需加载的执行细则
│   │   ├── audit-workflow.md
│   │   ├── audit-report.md
│   │   ├── authorization-and-handling.md
│   │   └── ci-pipeline-mode.md
│   └── assets/
│       └── audit_notes.template.md
├── prompt/
│   └── system_prompt.txt    # 网页端系统提示词（V2.0 对齐）
├── api/
│   └── openai_compatible.py # OpenAI 兼容 Python 客户端
├── docs/
│   ├── toolchain.md         # Playwright / webcrack / Ghidra / jadx
│   └── CAPABILITIES.md      # 一页速查：三个相关产物的能力边界
├── examples/
│   ├── sample_code.js       # 演示样本
│   ├── audit_notes.md       # 证据链笔记示例（已填好）
│   └── audit_report.md      # 六段式审计报告示例
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/ci.yml"""

README_NEW_TREE = """ultimate-security-audit/
├── README.md
├── LICENSE                  # MIT + 安全工具附加条款
├── Dockerfile
├── SKILL.md                 # 主控指令（V2.3.0，渐进披露）
├── CAPABILITIES.md          # 一页速查：四个入口的能力边界
├── audit_notes.md           # 仓库级变更记录
├── Makefile                 # make check：文档 + 测试 + 门控
├── pyproject.toml
├── references/              # 按需加载的执行细则
│   ├── audit-workflow.md
│   ├── audit-report.md
│   ├── authorization-and-handling.md
│   ├── ci-pipeline-mode.md
│   └── toolchain.md         # Playwright / webcrack / Ghidra / jadx
├── assets/
│   └── audit_notes.template.md
├── scripts/
│   ├── run_audit.py         # 门控入口（fail-closed）
│   ├── project_probe.py     # 阶段一扫描引擎
│   ├── skill_probe.py       # 外部能力探测
│   └── check_docs.py        # 文档死链校验
├── tests/
│   ├── sandbox_test.py
│   ├── test_golden.py
│   ├── test_repo_integrity.py
│   ├── test_skill_probe.py
│   └── fixtures/            # sample/ 与 expected_report.json
├── prompt/
│   └── system_prompt.txt    # 网页端系统提示词（V2.0 对齐）
├── api/
│   └── openai_compatible.py # OpenAI 兼容 Python 客户端
├── examples/
│   ├── sample_code.js       # 演示样本
│   ├── audit_notes.md       # 证据链笔记示例（已填好）
│   └── audit_report.md      # 六段式审计报告示例
└── .github/
    ├── ISSUE_TEMPLATE/
    └── workflows/ci.yml"""

PATH_SUBS = [
    ("skill/references/", "references/"),
    ("skill/assets/", "assets/"),
    ("skill/SKILL.md", "SKILL.md"),
    ("docs/CAPABILITIES.md", "CAPABILITIES.md"),
    ("docs/toolchain.md", "references/toolchain.md"),
]

SKILL_SEC_32 = """### 3.2 能力探测（`scripts/skill_probe.py`）

阶段一开始前跑 `python scripts/skill_probe.py`，输出一行 JSON（`rea-leanrea-router`、`context-mode`、`rg`、`grep` 四项布尔），按结果为 3.1 选定本地等价做法。降级时把结构化标记写进报告 `warnings`：

```json
{"code": "DEGRADED", "missing": ["context-mode"], "fallback": "rg -n"}
```

需要「全量引擎才算合格」的流水线可加 `--strict`：任一能力缺失即 `BLOCKED`，退出码 `2`。

"""

SKILL_RES_EXTRA = (
    "\n- `scripts/project_probe.py` — 阶段一扫描引擎：10 条规则、确定性输出、只读不执行。"
    "\n- `scripts/skill_probe.py` — 外部能力探测，对应 3.1 / 3.2 的降级矩阵。"
    "\n- `scripts/check_docs.py` — 文档死链校验，`make check` 与 CI 都会跑。"
)


def git(*args: str) -> None:
    subprocess.run(["git", *args], check=True)


def _sub_files() -> list[pathlib.Path]:
    return [pathlib.Path(n) for n in
            ("README.md", "AGENTS.md", "SECURITY.md", "DISCLAIMER.md")]


def migrate() -> None:
    if not pathlib.Path("skill").exists():
        print("already migrated, skip")
        return

    pathlib.Path("references").mkdir(exist_ok=True)
    pathlib.Path("assets").mkdir(exist_ok=True)

    for f in sorted(pathlib.Path("skill/references").glob("*.md")):
        git("mv", str(f), "references/" + f.name)
    git("mv", "skill/assets/audit_notes.template.md", "assets/audit_notes.template.md")
    git("mv", "skill/SKILL.md", "SKILL.md")

    git("mv", "docs/toolchain.md", "references/toolchain.md")
    git("mv", "docs/CAPABILITIES.md", "CAPABILITIES.md")

    # 空目录不入 git，直接清掉工作区残留
    shutil.rmtree("skill", ignore_errors=True)
    shutil.rmtree("docs", ignore_errors=True)

    for p in _sub_files():
        text = p.read_text(encoding="utf-8")
        for old, new in PATH_SUBS:
            text = text.replace(old, new)
        p.write_text(text, encoding="utf-8", newline="\n")

    skill = pathlib.Path("SKILL.md")
    text = skill.read_text(encoding="utf-8")
    text = text.replace("| `leanrea` CLI / `project_probe.py` |",
                        "| `leanrea` CLI / `scripts/project_probe.py` |")
    anchor = "## 4. 防幻觉与本地记忆 (Anti-Hallucination)"
    text = text.replace(anchor, SKILL_SEC_32 + anchor, 1)
    marker = "- `scripts/run_audit.py` —"
    end = text.index("\n", text.index(marker))
    text = text[:end] + SKILL_RES_EXTRA + text[end:]
    skill.write_text(text, encoding="utf-8", newline="\n")

    readme = pathlib.Path("README.md")
    text = readme.read_text(encoding="utf-8")
    if README_OLD_TREE in text:
        text = text.replace(README_OLD_TREE, README_NEW_TREE)
        readme.write_text(text, encoding="utf-8", newline="\n")
    else:
        print("WARN: README 目录树区块未匹配，跳过替换")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-push", action="store_true")
    a = ap.parse_args()

    migrate()
    git("add", "-A")
    git("-c", "user.name=github-actions[bot]",
        "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
        "commit", "-m", "refactor: 扁平化目录（skill/ docs/ -> 根目录）")
    if not a.no_push:
        git("push", "origin", "HEAD:main")
    return 0


if __name__ == "__main__":
    sys.exit(main())
