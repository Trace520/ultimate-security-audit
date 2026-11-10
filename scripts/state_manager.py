"""防幻觉状态机：discovery → verify → report，跳步即 BLOCKED。

大模型在长链路审计里最常见的失败不是「不知道」，而是「跳过取证直接推演」：
扫到几个可疑点就叫它漏洞，或者反编译到一半忘了入口点从哪来。
本模块把「先登记、再验证、最后出报告」写成可断言的文件状态：

- ``discovery``：记录授权号、目标清单与候选命中（每个命中一个稳定 id）。
- ``verify``：必须逐条给出「已核实」或「明确放弃」，没交代的不许进入下一步。
- ``report``：只有在 verify 完成且无未决命中时才允许。

状态文件是明文 JSON，默认 ``.audit-state.json``（已 gitignore）。
任何一步不满足前置条件都返回 ``(False, 原因)``，由调用方转成 ``BLOCKED``。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STAGES = ("discovery", "verify", "report")
DEFAULT_STATE = ".audit-state.json"


def finding_id(f: dict) -> str:
    """命中的稳定标识：文件:行:规则。行号变动会被视为新命中。"""
    return f"{f.get('file', '?')}:{f.get('line', 0)}:{f.get('rule', '?')}"


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def load(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def advance(path: Path, stage: str, *, approval: str, targets: list[str],
            findings: list[dict] | None = None,
            verified: list[str] | None = None,
            waived: list[str] | None = None) -> tuple[bool, str, dict]:
    """推进状态机。返回 (是否允许, 原因, 最新状态)。"""
    if stage not in STAGES:
        return False, f"未知阶段: {stage}", load(path)

    state = load(path)
    if state.get("approval") and state["approval"] != approval:
        return False, (
            f"审批号与已登记状态不一致（已登记 {state['approval']}，"
            f"本次 {approval}），请换一个状态文件或重新 discovery"
        ), state

    ordered = STAGES.index(stage)

    # ---- discovery：可直接建立或刷新 ----
    if stage == "discovery":
        ids = [finding_id(f) for f in (findings or [])]
        state = {
            "approval": approval,
            "targets": targets,
            "stage": "discovery",
            "discovery_ids": ids,
            "verified": [],
            "waived": [],
            "updated": _now(),
        }
        save(path, state)
        return True, "", state

    # ---- 共同前置：必须先有 discovery ----
    if state.get("stage") is None:
        return False, "尚未 discovery：先跑 --stage discovery 登记目标与候选命中", state
    current = STAGES.index(state["stage"])
    if ordered - 1 > current:
        need = STAGES[current + 1]
        return False, (
            f"跳步：当前阶段 {state['stage']}，需先完成 {need} 才能进入 {stage}"
        ), state

    # ---- verify：每条 discovery 命中都要有交代 ----
    if stage == "verify":
        known = set(state.get("discovery_ids", []))
        done = set(verified or []) | set(waived or [])
        missing = sorted(known - done)
        if missing:
            return False, (
                f"仍有 {len(missing)} 条命中未核实也未放弃：{', '.join(missing[:5])}"
                + (" …" if len(missing) > 5 else "")
            ), state
        extra = sorted(done - known)
        if extra:
            return False, f"核实清单里有未登记过的 id：{extra[:3]}", state
        state["verified"] = sorted(set(verified or []))
        state["waived"] = sorted(set(waived or []))
        state["stage"] = "verify"
    else:  # report
        if state.get("discovery_ids") and state.get("stage") != "verify":
            return False, "尚未 verify：不能直接出报告", state
        state["stage"] = "report"

    state["updated"] = _now()
    save(path, state)
    return True, "", state


def status_line(state: dict) -> str:
    if not state:
        return "stage: none"
    return (f"stage: {state.get('stage')} | approval: {state.get('approval')} | "
            f"discovery: {len(state.get('discovery_ids', []))} | "
            f"verified: {len(state.get('verified', []))} | "
            f"waived: {len(state.get('waived', []))}")
