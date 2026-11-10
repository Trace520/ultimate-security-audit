# Audit Notes

本文件是**仓库级**记录，写设计决策与历史变更；某次审计的**证据笔记**由
`scripts/run_audit.py` 在运行时生成到工作目录，两者不是一回事。

运行时的证据笔记默认写 `audit_notes.local.md`（已 gitignore），避免冲掉本文件。

旧版本中曾用 reverse_notes 作为笔记文件名，该文件已废弃并从仓库移除。

## 变更记录

- 初始版本：引入 `scripts/run_audit.py` 与 `scripts/project_probe.py`。
- 修复：示例数据与 golden fixture 对齐，由 `tests/test_golden.py` 保证。
- 修复：文档路径由 `scripts/check_docs.py` 校验。
- 修复：外部技能降级由 `scripts/skill_probe.py` 探测，`SKILL.md` 3.1 提供降级矩阵。
- 重构：把 skill 与 docs 两个目录扁平化到根目录，SKILL.md、CAPABILITIES.md、references、assets 各就各位。
- 修复：`SKILL.md` 的 `name` 对齐仓库名 `ultimate-security-audit`（此前叫 `enterprise-security-audit`，按名字加载会找不到目录）。
- 新增：`usa` 控制台入口（`pip install -e .` 后可用）与 `python -m scripts`，支持 `usa <target> --approval-id <ID>`；门控不变。
- 修复：`scripts/run_audit.py` 保留授权门控（缺审批号 `exit 2`），`scripts/project_probe.py` 只做扫描，不再自称「审计完成」。
- 3.0：新增防幻觉状态机 `scripts/state_manager.py`（`discovery → verify → report`，漏项 / 跳步 / 换审批号均 BLOCKED）。
- 3.0：新增 SCA `scripts/dep_scanner.py`（锁版本 → OSV `querybatch`；离线降级，不编造命中）。
- 3.0：新增 `scripts/report_formatter.py`，`--format sarif` 输出 SARIF 2.1.0，可上传 Code Scanning。
- 3.0：`usa` 增加 `--format/--out/--stage/--verify/--waive/--state/--sca`，版本号统一为 3.0.0。
- 3.0：CI 增加自我审计并上传 SARIF；`make check` 增加 SARIF 冒烟。
- 2.x 遗留说明：`README` 与 `SKILL.md` 的版本徽章此前指向 v2.x，本版一并对齐。
