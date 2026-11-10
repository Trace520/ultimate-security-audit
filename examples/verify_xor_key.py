#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""示例报告配套的 PoC：证明 sample_code.js 的 XOR 密钥是硬编码的。

只读本地文件，不联网，不含破坏性载荷。运行：

    python examples/verify_xor_key.py
"""

import pathlib
import re
import sys

SRC = pathlib.Path(__file__).with_name("sample_code.js")
KEY_PATTERN = re.compile(r'var\s+_0x4f2a\s*=\s*"([^"]+)"')


def main() -> int:
    if not SRC.exists():
        print(f"[-] 找不到样本：{SRC}", file=sys.stderr)
        return 1

    src = SRC.read_text(encoding="utf-8")
    match = KEY_PATTERN.search(src)
    if not match:
        print("[-] 密钥变量未找到：样本结构已变，需重新定位", file=sys.stderr)
        return 1

    key = match.group(1)
    line = src[: match.start()].count("\n") + 1
    print(f"[+] extracted key: {key!r} (len={len(key)})")
    print(f"[+] 行号：{line}")
    print("[+] 判定：硬编码密钥可从源码直接提取 — 验证通过")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
