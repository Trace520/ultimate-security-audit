"""SCA（软件组成分析）：解析依赖清单，向 OSV 查询已知漏洞。

只读本地产物、只调 OSV 一个只读接口，不装包、不执行目标代码。

设计约束：

- **不编造**：拿不到数据就返回 ``(None, 原因)``，由调用方标记 DEGRADED，
  绝不用「大概有漏洞」凑命中。
- **只查已锁定的版本**：``requirements.txt`` 要 ``==`` 精确版本；
  ``package-lock.json`` 取 lock 里的 ``version``。``package.json`` 里的
  ``^1.2.3`` 是范围，不属于「已知漏洞可定位」的输入，直接跳过并回报原因。
- **一次批量查询**：OSV ``querybatch`` 接受多包，避免逐包打接口被限流。
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path

OSV_ENDPOINT = "https://api.osv.dev/v1/querybatch"
TIMEOUT = 12

REQ_NAME = re.compile(r"^\s*([A-Za-z0-9_.\-]+)(?:\[[^\]]*\])?\s*==\s*([A-Za-z0-9_.+\-!]+)")
PEP508_MARK = re.compile(r"[;&]")


def _rel(path: Path, base: Path) -> str:
    try:
        return path.relative_to(base).as_posix()
    except ValueError:
        return path.name


def collect(targets: list[Path]) -> tuple[list[dict], list[str]]:
    """从目标目录 / 文件收集可查询的包，返回 (packages, notes)。"""
    packages: list[dict] = []
    notes: list[str] = []
    seen: set[tuple[str, str, str]] = set()

    def add(name: str, version: str, eco: str, src: str) -> None:
        key = (name, version, eco)
        if key in seen or not name or not version:
            return
        seen.add(key)
        packages.append({"name": name, "version": version,
                         "ecosystem": eco, "file": src})

    for target in targets:
        files: list[Path]
        if target.is_file():
            files = [target]
        else:
            files = [p for p in target.rglob("*") if p.is_file()]
        for f in files:
            name = f.name
            low = name.lower()
            if low.endswith("requirements.txt") or low.startswith("requirements"):
                base = f.parent
                for ln, line in enumerate(
                        f.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
                    if ln and line.lstrip().startswith(("#", "-")):
                        continue
                    m = REQ_NAME.match(PEP508_MARK.split(line)[0])
                    if m:
                        add(m.group(1), m.group(2), "PyPI", _rel(f, f.parent))
            elif low == "package-lock.json":
                try:
                    data = json.loads(f.read_text(encoding="utf-8", errors="ignore"))
                except (OSError, json.JSONDecodeError):
                    notes.append(f"{_rel(f, f.parent)}: 解析失败，已跳过")
                    continue
                for key, meta in (data.get("packages") or {}).items():
                    if not key or not isinstance(meta, dict):
                        continue
                    pkg_name = meta.get("name") or key.split("node_modules/")[-1]
                    if pkg_name and meta.get("version"):
                        add(pkg_name, str(meta["version"]), "npm", _rel(f, f.parent))
                for pkg_name, meta in (data.get("dependencies") or {}).items():
                    if isinstance(meta, dict) and meta.get("version"):
                        add(pkg_name, str(meta["version"]), "npm", _rel(f, f.parent))
            elif low == "package.json" and not (f.parent / "package-lock.json").exists():
                notes.append(f"{_rel(f, f.parent)}: 无 lock 文件，版本是范围值，已跳过")
    return packages, notes


def query_osv(packages: list[dict]) -> tuple[list[dict] | None, str]:
    """批量查询。返回 (findings, 错误原因)。成功时原因为空串。"""
    if not packages:
        return [], ""
    body = {"queries": [{"package": {"name": p["name"], "ecosystem": p["ecosystem"]},
                         "version": p["version"]} for p in packages]}
    req = urllib.request.Request(
        OSV_ENDPOINT,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.load(resp)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return None, f"OSV 不可达（{type(exc).__name__}），SCA 未执行"

    findings: list[dict] = []
    for pkg, result in zip(packages, data.get("results") or []):
        for vuln in (result or {}).get("vulns") or []:
            vid = vuln.get("id") or "UNKNOWN"
            alias = [a for a in vuln.get("aliases") or [] if a.startswith("CVE-")]
            summary = (vuln.get("summary") or "").strip()
            fixed = ""
            for aff in vuln.get("affected") or []:
                for rng in aff.get("ranges") or []:
                    for ev in rng.get("events") or []:
                        if ev.get("fixed"):
                            fixed = ev["fixed"]
                            break
            match = f"{pkg['name']}=={pkg['version']} {vid}"
            if alias:
                match += f" ({alias[0]})"
            if fixed:
                match += f" fix>={fixed}"
            if summary:
                match += f" — {summary[:70]}"
            findings.append({
                "file": pkg["file"],
                "line": 1,
                "rule": "DEP_VULN",
                "match": match,
                "package": pkg["name"],
                "version": pkg["version"],
                "ecosystem": pkg["ecosystem"],
                "vuln_id": vid,
            })
    return findings, ""


def scan(targets: list[Path]) -> tuple[list[dict], str, list[str]]:
    """一站式入口：收集 → 查询。返回 (findings, 降级原因, 说明)。"""
    packages, notes = collect(targets)
    if not packages:
        return [], "", notes + ["未找到带精确版本号的依赖清单（requirements.txt / package-lock.json）"]
    findings, err = query_osv(packages)
    if findings is None:
        return [], err, notes
    return findings, "", notes
