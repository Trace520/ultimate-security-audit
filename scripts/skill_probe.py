#!/usr/bin/env python3
"""探测外部 MCP 技能与本地等价能力是否可用。

输出一行 JSON，供 SKILL.md 3.1 / 3.2 的降级矩阵使用：
缺失项不必中断，按 references/audit-workflow.md 的本地等价命令继续。
"""
from __future__ import annotations

import importlib.util
import json
import shutil


def _has_module(module: str) -> bool:
    try:
        return importlib.util.find_spec(module) is not None
    except (ImportError, ValueError):
        return False


def probe() -> dict:
    return {
        "rea-leanrea-router": _has_module("rea_leanrea_router"),
        "context-mode": shutil.which("context-mode") is not None,
        "rg": shutil.which("rg") is not None,
        "grep": shutil.which("grep") is not None,
    }


if __name__ == "__main__":
    print(json.dumps(probe(), ensure_ascii=False))
