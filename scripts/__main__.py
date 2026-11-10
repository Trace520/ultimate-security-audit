"""支持 python -m scripts 直接跑 ``usa`` 等价入口。"""
import sys

from .run_audit import main

if __name__ == "__main__":
    sys.exit(main())
