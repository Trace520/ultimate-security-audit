# Audit Notes

本文件是**仓库级**记录，写设计决策与历史变更；某次审计的**证据笔记**由
`scripts/run_audit.py` 在运行时生成到工作目录，两者不是一回事。

旧版本中曾用 reverse_notes 作为笔记文件名，该文件已废弃并从仓库移除。

## 变更记录

- 初始版本：引入 `scripts/run_audit.py` 与 `scripts/project_probe.py`。
- 修复：示例数据与 golden fixture 对齐，由 `tests/test_golden.py` 保证。
- 修复：文档路径由 `scripts/check_docs.py` 校验。
- 修复：外部技能降级由 `scripts/skill_probe.py` 探测，`SKILL.md` 3.1 提供降级矩阵。
- 重构：把 skill 与 docs 两个目录扁平化到根目录，SKILL.md、CAPABILITIES.md、references、assets 各就各位。
- 修复：`scripts/run_audit.py` 保留授权门控（缺审批号 `exit 2`），`scripts/project_probe.py` 只做扫描，不再自称「审计完成」。
