"""CLI scripts for ultimate-security-audit.

这里负责一件与业务无关但很实际的事：把 stdout/stderr 统一成 UTF-8。
Windows 控制台在“重定向/管道”场景下默认用 cp1252，打印中文提示会直接
`UnicodeEncodeError` 把命令打挂（CI 里就是这个症状）。
`usa` 与应用 `python -m scripts` 都会先导入本包，因此在这里一次性修好。
"""
from __future__ import annotations

import sys


def _init_console() -> None:
    """把标准输出/错误重设为 UTF-8，不可编码字符降级为占位符，绝不因编码中断。"""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:  # pragma: no cover - 被替换成非 TextIO 时跳过
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):  # pragma: no cover
            pass


_init_console()
