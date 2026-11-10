import pathlib

helper = '''def _init_console() -> None:
    """Windows 控制台默认 cp1252，打印中文会 UnicodeEncodeError（CI 直接挂）。

    Linux/macOS 已经是 UTF-8，这里统一重设一遍，顺带把不可编码字符降级为占位符，
    保证输出永远不因编码问题中断审计。
    """
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (ValueError, OSError):  # pragma: no cover - 流被替换时忽略
            pass


'''

p = pathlib.Path("scripts/run_audit.py")
s = p.read_text(encoding="utf-8")
if "def _init_console" not in s:
    s = s.replace("def main() -> int:", helper + "def main() -> int:", 1)
    s = s.replace("def main() -> int:\n    ap = argparse",
                  "def main() -> int:\n    _init_console()\n    ap = argparse", 1)
    p.write_text(s, encoding="utf-8", newline="\n")
    print("run_audit patched")

c = pathlib.Path(".github/workflows/ci.yml")
t = c.read_text(encoding="utf-8")
if "PYTHONUTF8" not in t:
    t = t.replace("name: CI & Self-Audit\n\n",
                  "name: CI & Self-Audit\n\nenv:\n  PYTHONUTF8: \"1\"\n  PYTHONIOENCODING: \"utf-8\"\n\n", 1)
    t = t.replace("json.load(open('results.sarif'))",
                  "json.load(open('results.sarif', encoding='utf-8'))")
    c.write_text(t, encoding="utf-8", newline="\n")
    print("ci.yml patched")
