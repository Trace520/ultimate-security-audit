#!/usr/bin/env python3
"""CI 入口：授权门控 + 阶段一静态侦察（stdlib only，离线、只读、不执行目标代码）。

契约见 skill/references/ci-pipeline-mode.md 与 README「方式 D」。
退出码：0 = EXECUTE / DEGRADED，2 = BLOCKED（fail-closed）。
"""

import argparse
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

EXIT_OK = 0
EXIT_BLOCKED = 2

PLACEHOLDERS = {"", "tbd", "tbc", "none", "null", "nil", "-", "n/a", "na",
                "0000", "todo", "待定"}

SKIP_DIRS = {".git", ".hg", ".svn", "node_modules", "__pycache__",
             ".mypy_cache", ".pytest_cache", ".venv", "venv", "env",
             "dist", "build", "target", ".idea", ".vscode", ".tox",
             ".next", ".nuxt", "vendor"}

TEXT_SUFFIXES = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".vue",
                 ".svelte", ".py", ".pyw", ".java", ".kt", ".kts", ".go",
                 ".rs", ".rb", ".php", ".swift", ".dart", ".cs", ".fs",
                 ".vb", ".c", ".h", ".cc", ".cpp", ".hpp", ".m", ".mm",
                 ".scala", ".lua", ".pl", ".r", ".sql", ".json", ".jsonl",
                 ".yml", ".yaml", ".toml", ".ini", ".cfg", ".conf", ".env",
                 ".sh", ".bash", ".zsh", ".ps1", ".bat", ".cmd", ".html",
                 ".htm", ".xhtml", ".xml", ".gradle", ".properties", ".md",
                 ".txt", ".tf"}

# 规则表：命中只是「可疑模式」，等级提示用于人工排序，不构成结论。
RULES = [
    ("HARDCODED_SECRET", "高",
     r"""(?i)\b(api[_-]?key|apikey|secret|token|passwd|password|access[_-]?key|private[_-]?key|client[_-]?secret)\b\s*[:=]\s*["'][^"']{6,}["']"""),
    ("HARDCODED_KEY_VAR", "中",
     r"""(?i)\b(?:var|let|const)\s+(?:_0x[0-9a-f]{3,}|[A-Za-z_$][\w$]*(?:key|secret|token)[\w$]*)\s*=\s*["'][^"']{4,}["']"""),
    ("EVAL_USAGE", "高", r"\beval\s*\("),
    ("FUNCTION_CTOR", "中", r"\bnew\s+Function\s*\("),
    ("CHILD_PROCESS", "中",
     r"""(?i)(child_process|execSync|spawnSync|subprocess\.(?:run|call|check_output|Popen))"""),
    ("TLS_VERIFY_OFF", "高",
     r"""(?i)(rejectUnauthorized\s*:\s*false|verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*["']?0)"""),
    ("XSS_SINK", "中",
     r"""(?i)(innerHTML\s*=|outerHTML\s*=|document\.write\s*\(|dangerouslySetInnerHTML)"""),
    ("SQL_CONCAT", "中",
     r"""(?i)(execute\s*\(\s*["'][^"']*["']\s*\+|cursor\.execute\s*\(\s*f["'])"""),
    ("PLAINTEXT_HTTP", "低", r"""http://[^\s"'<>]+"""),
    ("DEBUG_ENABLED", "低", r"""(?i)\b(?:debug|DEBUG)\s*[:=]\s*(?:True|true|1)\b"""),
]
RULES = [(name, level, re.compile(pattern)) for name, level, pattern in RULES]

MAX_FILES = 500
MAX_FILE_BYTES = 512 * 1024
MAX_HITS = 200


def env(name):
    return (os.environ.get(name) or "").strip()


def split_targets(raw):
    return [item.strip() for item in re.split(r"[;\n]+", raw or "") if item.strip()]


def resolve_target(raw, root):
    """解析目标前缀并做越界检查；返回 (path, error)。"""
    if re.fullmatch(r"[A-Za-z]:[\\/]*", raw) or raw in {"/", "\\"}:
        return None, "目标越界：%s" % raw
    try:
        path = Path(raw).expanduser()
        resolved = (path if path.is_absolute() else root / path).resolve()
    except (OSError, RuntimeError) as exc:
        return None, "目标无法解析：%s（%s）" % (raw, exc)
    if not resolved.is_relative_to(root):
        return None, "目标越界：%s" % raw
    if not resolved.exists():
        return None, "目标不存在：%s" % raw
    return resolved, None


def git_head(root):
    try:
        done = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                              capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout.strip() or None if done.returncode == 0 else None


def detect_ci():
    """只读环境变量，不联网；空 dict 表示没有 CI 上下文。"""
    if env("GITHUB_ACTIONS").lower() == "true" or env("GITHUB_RUN_ID"):
        return {"platform": "github", "run": env("GITHUB_RUN_ID"),
                "sha": env("GITHUB_SHA").lower(), "repo": env("GITHUB_REPOSITORY"),
                "actor": env("GITHUB_ACTOR")}
    if env("CI").lower() == "true" and env("CI_PROJECT_PATH"):
        return {"platform": "gitlab", "run": env("CI_JOB_ID") or env("CI_PIPELINE_ID"),
                "sha": env("CI_COMMIT_SHA").lower(), "repo": env("CI_PROJECT_PATH"),
                "actor": env("GITLAB_USER_LOGIN")}
    if env("JENKINS_URL"):
        return {"platform": "jenkins", "run": env("BUILD_ID"),
                "sha": env("GIT_COMMIT").lower(), "repo": env("JOB_NAME"),
                "actor": env("BUILD_USER") or env("CHANGE_AUTHOR")}
    if env("CI") or env("BUILD_ID"):
        return {"platform": "other",
                "run": env("BUILD_ID") or env("CI_PIPELINE_ID"),
                "sha": (env("GIT_COMMIT") or env("CI_COMMIT_SHA")).lower(),
                "repo": "", "actor": ""}
    return {}


def ok_header(approval, targets, ci, status):
    run = ci.get("run") or "unknown"
    line = ("[AUDIT_MODE: CI_PIPELINE | approval: %s | targets: %d | ci: %s | run: %s]"
            % (approval, targets, ci.get("platform", "none"), run))
    if status:
        line = line[:-1] + " | status: %s]" % status
    return line


def collect_files(targets, max_files):
    stats = {"files": 0, "skipped_large": 0, "truncated": 0}
    found = []
    for target in targets:
        if target.is_file():
            if target.stat().st_size <= MAX_FILE_BYTES:
                found.append(target)
            else:
                stats["skipped_large"] += 1
            continue
        for current, dirnames, filenames in os.walk(target):
            dirnames[:] = sorted(d for d in dirnames
                                 if d not in SKIP_DIRS
                                 and not (Path(current) / d).is_symlink())
            for name in sorted(filenames):
                path = Path(current) / name
                if path.is_symlink() or path.suffix.lower() not in TEXT_SUFFIXES:
                    continue
                try:
                    if path.stat().st_size > MAX_FILE_BYTES:
                        stats["skipped_large"] += 1
                        continue
                except OSError:
                    continue
                found.append(path)
                if len(found) >= max_files:
                    stats["truncated"] = 1
                    break
            if stats["truncated"]:
                break
        if stats["truncated"]:
            break
    stats["files"] = len(found)
    return found, stats


def clean(text, limit=120):
    text = re.sub(r"[\x00-\x1f\x7f]+", " ", text).strip()
    return text.replace("`", "'").replace("|", "\\|")[:limit]


def scan(files, root):
    hits, truncated = [], 0
    for path in files:
        try:
            with path.open("r", encoding="utf-8", errors="replace") as handle:
                for lineno, line in enumerate(handle, start=1):
                    for name, level, pattern in RULES:
                        if not pattern.search(line):
                            continue
                        rel = path.relative_to(root) if path.is_relative_to(root) else path
                        hits.append({"file": rel.as_posix(),
                                     "line": str(lineno), "rule": name,
                                     "level": level, "snippet": clean(line)})
                        if len(hits) >= MAX_HITS:
                            return hits, 1
        except OSError:
            continue
    return hits, truncated


def write_notes(path, *, status, approval, raw_targets, scope, ci, head,
                verdict, hits, stats, truncated):
    now = datetime.now().astimezone().isoformat(timespec="seconds")
    ci_line = ("%s / repo=%s / sha=%s / actor=%s / run=%s"
               % (ci.get("platform"), ci.get("repo") or "-", ci.get("sha") or "-",
                  ci.get("actor") or "-", ci.get("run") or "-")) if ci else "none"
    auditor = "CI job（无人值守）" if ci else "本地 CLI（无 CI 上下文）"
    lines = [
        "# %s" % path.name, "",
        "> 由 `scripts/run_audit.py` 于 %s 自动生成；只含授权记录与阶段一可疑模式命中。" % now,
        "", "## 授权声明", "", "```",
        "授权依据：CI 流水线自动判定（AUTHORIZATION_MODE=CI_PIPELINE）",
        "审批引用：%s" % approval,
        "目标清单：%s" % raw_targets,
        "范围说明：%s" % (scope or "（未填）"),
        "CI 上下文：%s" % ci_line,
        "本地 HEAD：%s" % (head or "（读取失败）"),
        "核对结果：%s" % verdict,
        "判定时间：%s" % now,
        "审计人：%s" % auditor,
        "```", "", "## 阶段一 · 静态侦察（自动）", "",
        "- 判定：**%s**" % status,
        "- 扫描文件：%d（跳过超限文件 %d 个）" % (stats["files"], stats["skipped_large"]),
        "- 可疑模式命中：%d 条%s" % (len(hits), "（已达上限，结果截断）" if truncated else ""),
        "",
    ]
    if hits:
        lines += ["| # | 文件:行 | 规则 | 等级提示 | 片段 |", "|---|---|---|---|---|"]
        for index, hit in enumerate(hits, start=1):
            lines.append("| %d | `%s:%s` | %s | %s | `%s` |"
                         % (index, hit["file"], hit["line"], hit["rule"],
                            hit["level"], hit["snippet"]))
    else:
        lines.append("未命中任何规则。**这不等于目标干净**：只说明阶段一定性规则没有命中。")
    lines += [
        "", "## 待人工确认", "",
        "- 上表是「可疑模式」，不是缺陷定性。可达性、影响面、既有防护必须按",
        "  `skill/SKILL.md` 阶段二 / 阶段三复核后才允许写进报告。",
        "- 命中在注释或测试样本里时按 `[证据缺失]` 处理，不计入缺陷清单。",
        "", "## 证据自检", "", "| 待下结论 | 证据位置 | 核对结果 |", "|---|---|---|",
        "| 尚未下结论 | — | 本脚本只做门控与阶段一，未进入阶段二 |", "",
        "## 未执行的阶段", "",
        "- 阶段二（抓包 / 反混淆 / 反编译）与阶段三（数据流推演、PoC）未执行：",
        "  本脚本不联网、不执行目标代码，不产出伪代码级结论。",
        "- 需要完整报告时，按 `skill/references/audit-workflow.md` 继续。", "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main(argv=None):
    parser = argparse.ArgumentParser(description="CI 门控 + 阶段一静态侦察（只读、离线）")
    parser.add_argument("--targets", default=None, help="允许审计的路径，; 分隔；缺省读 AUDIT_TARGETS")
    parser.add_argument("--repo-root", default=None, help="仓库根目录，默认脚本上一级")
    parser.add_argument("--notes", default="audit_notes.md", help="证据笔记输出路径")
    parser.add_argument("--max-files", type=int, default=MAX_FILES, help="最多扫描文件数")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).expanduser().resolve() if args.repo_root \
        else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print("[AUDIT_MODE: BLOCKED | missing: repo_root 不存在]", file=sys.stderr)
        return EXIT_BLOCKED

    approval = env("AUDIT_APPROVAL_ID")
    raw_targets = args.targets if args.targets is not None else env("AUDIT_TARGETS")
    targets = split_targets(raw_targets)

    missing = []
    if env("AUTHORIZATION_MODE").upper() != "CI_PIPELINE":
        missing.append("AUTHORIZATION_MODE=CI_PIPELINE")
    if approval.lower() in PLACEHOLDERS:
        missing.append("AUDIT_APPROVAL_ID")
    if not targets:
        missing.append("AUDIT_TARGETS")
    if missing:
        print("[AUDIT_MODE: BLOCKED | missing: %s]" % ", ".join(missing))
        print("补齐方式：在 CI 配置里注入上述字段，不要写成字面量；"
              "字段说明见 skill/references/ci-pipeline-mode.md。", file=sys.stderr)
        return EXIT_BLOCKED

    resolved = []
    for raw in targets:
        path, error = resolve_target(raw, root)
        if error:
            print("[AUDIT_MODE: BLOCKED | missing: %s]" % error)
            print("BLOCKED 状态下不读取任何目标内容。", file=sys.stderr)
            return EXIT_BLOCKED
        resolved.append(path)

    ci = detect_ci()
    head = git_head(root)
    status = "EXECUTE"
    verdict = "commit 一致 / 目标均在仓库内 / 判定 EXECUTE"
    if not ci:
        status, verdict = "DEGRADED", "无 CI 上下文，来源不可追溯 / 仅执行阶段一"
    elif not ci.get("sha"):
        print("[AUDIT_MODE: BLOCKED | missing: CI 上下文存在但取不到 commit]")
        return EXIT_BLOCKED
    elif head is None:
        print("[AUDIT_MODE: BLOCKED | missing: 本地 HEAD 不可读，commit 交叉核对失败]")
        return EXIT_BLOCKED
    elif ci["sha"] != head.lower():
        status = "DEGRADED"
        verdict = ("commit 漂移：CI 声明 %s，本地 HEAD %s / 仅执行阶段一"
                   % (ci["sha"][:12], head[:12]))

    print(ok_header(approval, len(resolved), ci, None if status == "EXECUTE" else status))

    files, stats = collect_files(resolved, args.max_files)
    hits, truncated = scan(files, root)
    notes = Path(args.notes).expanduser()
    write_notes(notes, status=status, approval=approval, raw_targets=raw_targets,
                scope=env("AUDIT_SCOPE_NOTE"), ci=ci, head=head, verdict=verdict,
                hits=hits, stats=stats, truncated=truncated)

    print("[*] 扫描文件 %d 个，可疑模式命中 %d 条%s"
          % (stats["files"], len(hits), "（已截断）" if truncated else ""))
    print("[*] 证据笔记：%s" % notes.resolve())
    if status == "DEGRADED":
        print("[!] DEGRADED：只做了阶段一静态侦察，抓包 / 反混淆 / 反编译均未执行。",
              file=sys.stderr)
    print("[*] 下一步：按 skill/SKILL.md 阶段二 / 阶段三复核命中项。")
    return EXIT_OK


if __name__ == "__main__":
    raise SystemExit(main())
