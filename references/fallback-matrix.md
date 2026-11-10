# 外部依赖与本地降级矩阵

阶段一开始前跑一次 `python scripts/skill_probe.py`（只看当前环境挂载了什么，不联网、不安装）。
任何一项缺失都不终止审计，只降低结论上限。

| 项目 | 探测方式 | 承担的角色 | 缺失时的本地等价做法 | 降级后的结论上限 |
|---|---|---|---|---|
| `rea-leanrea-router` | Python 模块 `rea_leanrea_router` | 阶段一 / 三的引擎选型 | 按目标特征自行选型，理由写进笔记 | 选型可能不是最优，但不影响证据 |
| `leanrea` CLI | `which leanrea` | 资产摸底、清单 | `usa` + `file` + `strings` + `grep -rn` | 拿不到开箱即用的资产画像 |
| REA 深度引擎（Ghidra / Hopper） | 由 router 报 | 伪代码还原 | 只交付已落盘的静态事实 | 不出伪代码级结论，标 `[证据缺失]` |
| `context-mode` | `which context-mode` | 大文件降维 | `rg -n` / `grep -n` 定位 + `sed -n` 分段 | 大文件容易撑爆上下文，需更细的手工切片 |
| Playwright MCP / Fetch MCP | 工具目录 | 抓包、登录态复现 | 退化为纯静态分析 | 无动态证据，`[DYNAMIC]` 条目标注原因 |
| `webcrack` | `which webcrack` | JS 反混淆 | 手工按调用关系还原 | 复杂混淆可能只还原一部分 |

## 报告里怎么写

报告头下方**单独一行**：

```text
[DEGRADED: external_skills_missing] missing: context-mode, REA
```

不要塞进 `[AUDIT_MODE: ...]` 那一行（那是授权判定，两者互不覆盖），也不要只写在正文里让人翻。

## 两条禁令

- **不假装**：禁止写「已调用 Ghidra 分析」「已播放器抓包」这类没发生的事。
- **不推荐安装**：缺工具不要主动建议用户装 MCP/引擎——安装会写全局配置，需单独确认。
