# Capabilities

一页速查。每个入口对应一件事，互不替代；判据细则在 `references/`，跑起来的证据落在运行时生成的 `audit_notes.local.md`。

## 1. 四个入口

| 入口 | 回答什么问题 | 怎么用 |
|---|---|---|
| `usa`（= `scripts/run_audit.py`） | 这次运行有没有授权依据，扫到了什么 | `pip install -e .` 后 `usa tests/fixtures/sample --approval-id CHG-001`；等价 `python scripts/run_audit.py --targets ...`、`python -m scripts ...` |
| `scripts/project_probe.py` | 单个目录 / 文件里有哪些可疑模式 | `python scripts/project_probe.py <target>` |
| `scripts/skill_probe.py` | 外部引擎装没装，要不要降级 | `python scripts/skill_probe.py` |
| `scripts/check_docs.py` | 文档里写的路径是不是真的存在 | `python scripts/check_docs.py` |

## 2. 门控三态（`scripts/run_audit.py`）

| 判定 | 条件 | 行为 |
|---|---|---|
| `EXECUTE` | 模式开关 + 审批编号 + 目标清单齐备，目标全在仓库根内，CI commit 与本地 HEAD 一致 | 静默跑阶段一并落盘 |
| `DEGRADED` | 三项齐备但无 CI 上下文，或 commit 漂移 | 只做阶段一，笔记里写原因 |
| `BLOCKED` | 缺字段 / 占位值 / 目标越界或不存在 / 读不到 HEAD | 退出码 `2`，**不打开任何目标文件** |

`AUTHORIZATION_MODE` 单独存在不算授权：它证明的是运行形态，不是目标归属。交互式命令行必须同时给 `--approval-id` 与目标，否则直接 `BLOCKED`。

## 2.1 三个入口，同一套门控

```bash
usa tests/fixtures/sample --approval-id CHG-001      # 装成命令后
python -m scripts tests/fixtures/sample --approval-id CHG-001
python scripts/run_audit.py --targets tests/fixtures/sample --approval-id CHG-001
```

命中即返回 `1`（`--allow-findings` 可压回 `0`），`BLOCKED` 恒为 `2`。笔记默认写 `audit_notes.local.md`（已在 `.gitignore`），仓库根的 `audit_notes.md` 是变更记录，两者不要混。

## 3. 阶段一能答什么

- 10 条规则的可疑模式：硬编码凭据、`eval`、`Function` 构造器、进程调用、关闭证书校验、HTML 注入 sink、SQL 拼接、明文 HTTP、调试开关、混淆变量名赋字符串。
- 每条命中带 `文件:行`、规则 ID 与原始片段；输出确定性，`tests/test_golden.py` 守着。

## 4. 故意不答

- 不下漏洞定性。命中只是「可疑模式」，可达性与影响面要走阶段二 / 三。
- 不抓包、不反混淆、不反编译、不构造 PoC。
- 不执行目标代码、不装依赖、不联网、不改目标文件。
- 目标清单里有一项不存在就整体 `BLOCKED`，不会「先跑一部分看看」。

## 5. 外部能力缺失时

`scripts/skill_probe.py` 报 `false` 的项按 `SKILL.md` 3.1 的降级矩阵处理：不中断，报告里标 `DEGRADED`，并写明缺哪一项、对结论可信度的影响。`scripts/run_audit.py --strict` 会在能力缺失时直接 `BLOCKED`。

## 6. 不该用的时候

- 没有授权凭证、也不在自有资产范围 —— 门控会中断，不要用环境变量绕。
- 想绕过许可证、DRM、付费墙、访问控制。
- 想直接拿可批量利用的成品工具 —— 只给最小验证脚本。
- 只想问一个概念 —— 直接答，不接管工程。

## 7. 本仓库不含的东西

`rea-leanrea-router`、`leanrea` CLI、`dev-god`、沙箱报告目录、打包产物，都不在本仓库，照旧路径访问会 404 —— 那是早期文档从另一套产物里带进来的残留。需要那类能力时走 `SKILL.md` 3.1 的本地等价做法。

## 8. 自检

```bash
make check     # 文档校验 + pytest + 门控冒烟
```
