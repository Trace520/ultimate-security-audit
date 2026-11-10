# 三个产物能干什么

一页速查。三个产物各管一段，互不替代；判据细则在 `skill/references/`，跑起来的证据落在 `audit_notes.md`。

## 1. 一句话分工

| 产物 | 回答什么问题 | 怎么用 | 交付物 |
|---|---|---|---|
| `skill/SKILL.md`（V2.3.0） | 「这个自有 / 已授权目标有没有问题，怎么证明」 | 放进客户端技能目录原生加载（Clone 到 `~/.claude/skills/ultimate-security-audit`） | 六段式审计报告 + 最小验证脚本 + 证据链 |
| `prompt/system_prompt.txt` | 「网页版怎么复现同一套流程」 | 整段粘贴为系统提示词 | 同格式报告，但**不落盘**，证据链靠对话保留 |
| `api/openai_compatible.py` | 「怎么用脚本 / 自有模型批量跑」 | `python api/openai_compatible.py`，注入 `OPENAI_API_KEY` 与 `OPENAI_BASE_URL` | 同格式报告，走 Chat Completions 兼容端点 |

三者共用同一套判据。改判据只改 `skill/references/`，不要三处各写一份——那是文档漂移的起点。

## 2. `scripts/run_audit.py` 具体能答什么

README「方式 D」的 CI 入口，也是 `skill/references/ci-pipeline-mode.md` 的参考实现。

```bash
python scripts/run_audit.py --targets "src/;dist/app.asar"
```

环境变量：`AUTHORIZATION_MODE=CI_PIPELINE`、`AUDIT_APPROVAL_ID`、`AUDIT_TARGETS`，可选 `AUDIT_SCOPE_NOTE`。分隔符 `;` 或换行。

**能答**

- 这次运行有没有授权依据：三态判定 `EXECUTE` / `BLOCKED` / `DEGRADED`，缺字段、目标越界、目标不存在一律 `BLOCKED`，退出码 `2`。
- 审计对象是不是流水线所指的那份代码：比对 CI 声明的 commit 与本地 `git rev-parse HEAD`，不一致降 `DEGRADED` 并把漂移写进笔记。
- 阶段一的可疑模式：10 条规则（硬编码凭据、`eval`、`Function` 构造器、进程调用、关闭证书校验、HTML 注入 sink、SQL 拼接、明文 HTTP、调试开关、混淆变量名赋字符串），命中带 `文件:行` 与原始片段。
- 授权段与命中表落盘到 `audit_notes.md`，字段与交互模式一致（谁批的、审什么、依据是什么）。

**不能答 / 故意不答**

- 不下漏洞定性。命中只是「可疑模式」，可达性、影响面要按阶段二 / 三复核。
- 不抓包、不反混淆、不反编译、不构造 PoC —— 那是阶段二 / 三，脚本只到阶段一。
- 不执行任何候选命令、不装依赖、不联网、不改目标文件。
- 不猜：目标清单里有一项不存在就整体 `BLOCKED`，不会「先跑一部分看看」。
- 扫描有上限（500 文件、单文件 512 KiB），命中或超限会在笔记里标 `truncated` / `skipped_large`。

## 3. 三道防线，各自管什么

| 层 | 做法 | 挡什么 | 挡不住什么 |
|---|---|---|---|
| 授权门控 | 判定先于读取，`BLOCKED` 时连目标目录都不打开 | 无审批编号、无目标清单、越界路径的静默执行 | 有人伪造审批号（只能靠 CI 环境保护变量与分支保护） |
| 证据链落盘 | 授权段、命中表、未执行阶段全部写进 `audit_notes.md` | 多轮对话丢上下文、结论无出处 | 笔记本身写错（仍需证据自检） |
| 证据自检 | 下结论前回读笔记，找不到支撑写 `[证据缺失]` | 把推断写成事实 | 模型自己跳过这一步 |

**明确没有做的**：自动给漏洞定级、自动生成「已验证」结论、把命中数当风险分。样本里 `secret_key_123` 会被命中，但它是演示占位值——这种「命中但不成立」的情况必须由人判断，脚本不做背书。

## 4. 审计技能的合规映射，什么时候有

只在**目标本身是 LLM / Agent 应用**时才贴标签（prompt 模板、tool schema、向量库、agent 编排、`openai`/`langchain`/`mcp` 等依赖）。映射表见 `skill/references/audit-report.md` 第 2 节，编号钉死 2025 版：LLM01 注入、LLM02 敏感信息泄露、LLM03 供应链、LLM05 输出处理、LLM06 过度代理、LLM07 系统提示词泄露、LLM08 向量与嵌入弱点。

三条硬规则：标签必须能指回一条证据；编号必须带年份（2023 与 2025 编号不同，混用即错）；拿不准写 `未映射（标准条目待核）`，不猜。非 LLM 目标写 `[compliance: N/A — 非 LLM 目标]`，不硬套。

## 5. 不该用它们的时候

- 没有授权凭证、也不在自有资产范围 → 门控会中断（`BLOCKED`），不要试图用环境变量绕开门控。
- 想绕过许可证、DRM、付费墙、访问控制 → 三个产物都不做。
- 想直接拿到可批量利用的成品工具 → 只给最小验证脚本，不含破坏性载荷。
- 只想问一个概念 → 直接答，不接管工程、不跑脚本。
- 引擎（leanrea / REA / Ghidra / jadx）没装 → 只交付阶段一、二的已落盘事实，不产出伪代码级结论，也不替你安装（安装会写 MCP 配置，需要单独确认）。

## 6. 自检与验收

```bash
python -m py_compile api/openai_compatible.py scripts/run_audit.py examples/verify_xor_key.py
python examples/verify_xor_key.py                     # 预期：extracted key 'secret_key_123'，行号 5
AUTHORIZATION_MODE=CI_PIPELINE python scripts/run_audit.py --targets examples/sample_code.js
                                                      # 预期：exit 2，BLOCKED（缺 AUDIT_APPROVAL_ID）
AUTHORIZATION_MODE=CI_PIPELINE AUDIT_APPROVAL_ID=CHG-2026-0417 \
  python scripts/run_audit.py --targets examples/sample_code.js --notes audit_notes.local.md
                                                      # 预期：DEGRADED（无 CI 上下文），命中 1 条
docker build -t ultimate-security-audit .
```

CI（`.github/workflows/ci.yml`）会跑上面第 1 条与第 3、4 条的门控冒烟：缺审批号必须 `exit 2`，这正是「fail-closed」的可执行证据。

## 7. 本仓库不含的东西

`rea-leanrea-router`、`dev-god`、`project_probe.py`、`tests/`、`reports/`、`dist/` 都不在本仓库，引用它们会 404。这些是早期文档从另一套产物里带进来的残留。

需要那些能力时按 [`skill/SKILL.md`](../skill/SKILL.md) 第 3.1 节降级：用 `scripts/run_audit.py` + `grep -rn` + `strings` 顶住阶段一，报告头标 `[DEGRADED: external_skills_missing]`，不中断、不假装已调用。
