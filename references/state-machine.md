# 防幻觉状态机契约

## 为什么有这东西

安全审计的失败模式里，最常见的一条不是「没看到」，而是**跳步**：
扫到几个可疑字符串就直接写成「高危漏洞」，或者反编译到一半忘了入口点从哪来，
于是后半段开始编。状态机不解决「能力不足」，但能保证**没核实的东西不会出现在报告里**。

## 三个阶段

| 阶段 | 命令 | 写入 | 进入下一阶段的条件 |
|---|---|---|---|
| `discovery` | `usa <target> --approval-id <ID> --stage discovery` | 审批号、目标清单、候选命中 id | 无需前置 |
| `verify` | `usa ... --stage verify`（`--verify` / `--waive` / `--verify-all`） | 已核实 / 已放弃的 id | 每条 discovery 命中都有交代 |
| `report` | `usa ... --stage report --format sarif` | 阶段标记 | 已完成 `verify` |

跳步、漏项、换审批号都会被拒：返回 `BLOCKED`、退出码 `2`，并打印具体原因。

## 命中 id

稳定格式：`文件:行:规则`，例如 `sample_code.js:5:HARDCODED_SECRET`。
行号变了就是新命中——这是故意的：改了代码就得重新核实。

## 状态文件

默认 `.audit-state.json`（已 gitignore），明文 JSON：

```json
{
  "approval": "CHG-2026-0417",
  "targets": ["tests/fixtures/sample"],
  "stage": "report",
  "discovery_ids": ["sample_code.js:5:HARDCODED_SECRET"],
  "verified": ["sample_code.js:5:HARDCODED_SECRET"],
  "waived": [],
  "updated": "2026-11-10T15:40:00+08:00"
}
```

用 `--state <path>` 换文件，便于一次审计一个状态、互不串味。

## 什么时候可以「放弃」一条命中

`--waive <id>` 是合法的，但含义必须是**已看过并判定不成立**，例如演示用的占位密钥、
框架内部已做转义的 sink。把它当成「跳过」用，等于自己拆掉了这道闸。

## 与授权门控的关系

状态机在门控之后执行：`BLOCKED` 时根本不会写状态文件。
反过来，状态文件存在不代表当前这次已授权——每次都按本次审批号重新判定。
