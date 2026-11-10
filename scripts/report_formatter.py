"""把命中输出成 SARIF 2.1.0，供 GitHub Code Scanning / 其它 SAST 平台消费。

SARIF 的价值在于「让机器也能读懂审计结果」：同一个 finding 在 PR 里是一条
带行号的注释，在 Security 标签页是一个可跟踪的告警，而不是一段只有人能看的文字。

只做格式转换，不改变判定：命中仍然是「可疑模式」，不等价于漏洞成立。
"""
from __future__ import annotations

import json
from pathlib import Path

SARIF_VERSION = "2.1.0"
SCHEMA = "https://json.schemastore.org/sarif-2.1.0.json"
TOOL_NAME = "ultimate-security-audit"
TOOL_URI = "https://github.com/Trace520/ultimate-security-audit"

# 规则 → SARIF level。硬编码凭据与代码执行类给 error，其余给 warning；
# 依赖漏洞单独给 warning：命中真实 CVE，但可利用性仍需人工确认。
LEVELS = {
    "HARDCODED_SECRET": "error",
    "HARDCODED_KEY_VAR": "error",
    "EVAL_USAGE": "error",
    "FUNCTION_CTOR": "warning",
    "CHILD_PROCESS": "warning",
    "TLS_VERIFY_OFF": "error",
    "XSS_SINK": "warning",
    "SQL_CONCAT": "warning",
    "PLAINTEXT_HTTP": "note",
    "DEBUG_ENABLED": "note",
    "DEP_VULN": "warning",
}

RULE_TITLES = {
    "HARDCODED_SECRET": "硬编码密钥字面量",
    "HARDCODED_KEY_VAR": "疑似硬编码凭据赋值",
    "EVAL_USAGE": "动态代码执行（eval）",
    "FUNCTION_CTOR": "Function 构造器",
    "CHILD_PROCESS": "外部进程调用",
    "TLS_VERIFY_OFF": "关闭证书校验",
    "XSS_SINK": "HTML 注入 sink",
    "SQL_CONCAT": "疑似 SQL 字符串拼接",
    "PLAINTEXT_HTTP": "明文 HTTP 地址",
    "DEBUG_ENABLED": "调试开关默认开启",
    "DEP_VULN": "第三方依赖已知漏洞（OSV）",
}


def _rule(rule_id: str) -> dict:
    return {
        "id": rule_id,
        "name": rule_id,
        "shortDescription": {"text": RULE_TITLES.get(rule_id, rule_id)},
        "defaultConfiguration": {"level": LEVELS.get(rule_id, "warning")},
        "properties": {"tags": ["security", "static-analysis"]},
    }


def to_sarif(findings: list[dict], *, version: str, warnings: list[str] | None = None,
             invocation_uri: str = "") -> dict:
    """生成 SARIF 文档。findings 为空也是合法文档（results 为空数组）。"""
    rule_ids = sorted({f.get("rule", "UNKNOWN") for f in findings})
    results = []
    for f in findings:
        rule_id = f.get("rule", "UNKNOWN")
        results.append({
            "ruleId": rule_id,
            "level": LEVELS.get(rule_id, "warning"),
            "message": {"text": f"{RULE_TITLES.get(rule_id, rule_id)}：{f.get('match', '')}"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f.get("file", "?")},
                    "region": {"startLine": max(1, int(f.get("line", 1)))},
                }
            }],
            "properties": {
                "findingId": f"{f.get('file', '?')}:{f.get('line', 0)}:{rule_id}",
            },
        })

    run = {
        "tool": {"driver": {
            "name": TOOL_NAME,
            "version": version,
            "informationUri": TOOL_URI,
            "rules": [_rule(r) for r in rule_ids],
        }},
        "results": results,
        "invocations": [{
            "executionSuccessful": True,
            "commandLine": invocation_uri or "usa --format sarif",
        }],
    }
    if warnings:
        run["invocations"][0]["toolExecutionNotifications"] = [
            {"level": "warning", "message": {"text": w}} for w in warnings
        ]
    return {"$schema": SCHEMA, "version": SARIF_VERSION, "runs": [run]}


def summarize(findings: list[dict]) -> dict[str, int]:
    """按 level 统计，供文本模式尾行使用。"""
    out: dict[str, int] = {"error": 0, "warning": 0, "note": 0}
    for f in findings:
        out[LEVELS.get(f.get("rule", ""), "warning")] += 1
    return out


def write(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
