# Capabilities

一页速查。每个入口只回答一件事，互不替代；判据细则在 `references/`，运行证据落在 `audit_notes.local.md`。

## 1. 入口

| 入口 | 回答什么问题 | 怎么用 |
|---|---|---|
| `usa`（= `scripts/run_audit.py`） | 这次运行有没有授权依据、扫到了什么 | `usa tests/fixtures/sample --approval-id CHG-001` |
| `scripts/project_probe.py` | 单个目录 / 文件里有哪些可疑模式 | `python scripts/project_probe.py <target>` |
| `scripts/dep_scanner.py` | 依赖清单里有没有已知漏洞 | `usa <target> --sca` |
| `scripts/state_manager.py` | 这轮审计走到哪一步、还差什么 | `usa <target> --stage verify` |
| `scripts/report_formatter.py` | 结果怎么变成 SARIF | `usa <target> --format sarif` |
| `scripts/skill_probe.py` | 外部引擎装没装，要不要降级 | `python scripts/skill_probe.py` |
| `scripts/check_docs.py` | 文档里写的路径是不是真的存在 | `python scripts/check_docs.py` |

三入口等价：`usa` / `python -m scripts` / `python scripts/run_audit.py`，共用同一套门控。

## 2. 门控三态

| 判定 | 条件 | 行为 |
|---|---|---|
| `EXECUTE` | 模式开关 + 审批号 + 目标清单齐备，目标在根内，CI commit 与 HEAD 一致 | 静默执行 |
| `DEGRADED` | 三项齐备但无 CI 上下文 / commit 漂移 / SCA 离线 | 只做已落盘部分，报告写原因 |
| `BLOCKED` | 缺字段 / 占位值 / 目标越界或不存在 / 读不到 HEAD | 退出码 `2`，**不打开目标文件** |

交互式必须同时给 `--approval-id` 与目标；只给一个直接 `BLOCKED`。

## 3. 状态机

`discovery → verify → report`。`verify` 要求每条命中都被 `--verify` 或 `--waive` 覆盖；
跳步、漏项、换审批号一律 `BLOCKED`。详见 `references/state-machine.md`。

## 4. 阶段一能答什么

- 10 条规则的可疑模式：硬编码凭据、`eval`、`Function` 构造器、进程调用、关闭证书校验、HTML 注入 sink、SQL 拼接、明文 HTTP、调试开关、混淆变量名赋字符串。
- SCA：只查锁定版本（`requirements.txt` 的 `==`、`package-lock.json` 的 `version`），走 OSV `querybatch`。
- 每条命中带 `文件:行`、规则 ID、片段；输出确定性，`tests/test_golden.py` 守着。

## 5. 故意不答

- 不下漏洞定性。命中只是「可疑模式」，可达性与影响面要走阶段二 / 三。
- 不抓包、不反混淆、不反编译、不构造 PoC。
- 不执行目标代码、不装依赖、不改目标文件；唯一联网动作是 OSV 查询（由 `--sca` 控制）。
- 依赖清单里是范围版本（`^1.2.3`）时不去猜，直接跳过并说明。
- 目标清单里有一项不存在就整体 `BLOCKED`，不「先跑一部分」。

## 6. 报告格式

| 格式 | 用途 | 命令 |
|---|---|---|
| text | 终端阅读 | 默认 |
| json | 机器消费 / 存档 | `--format json --out audit.json` |
| sarif | GitHub Code Scanning | `--format sarif --out results.sarif` |

SARIF 等级映射：硬编码凭据 / `eval` / 关证书校验 → `error`；其余 → `warning` / `note`。

## 7. 不该用的时候

- 没有授权凭证、也不在自有资产范围 —— 门控会中断，不要用环境变量绕。
- 想绕过许可证、DRM、付费墙、访问控制。
- 想直接拿可批量利用的成品工具 —— 只给最小验证脚本。
- 只想问一个概念 —— 直接答，不接管工程。

## 8. 本仓库不含的东西

`rea-leanrea-router`、`leanrea` CLI、`dev-god`、沙箱报告目录、打包产物都不在本仓库，照旧路径访问会 404。
需要那类能力时走 `references/fallback-matrix.md` 的本地等价做法。

## 9. 自检

```bash
make check     # 文档校验 + pytest + 门控冒烟 + SARIF 冒烟
```
