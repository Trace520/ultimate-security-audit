# Contributing

感谢你对 `ultimate-security-audit` 的兴趣。以下是参与贡献的流程。

## 两条铁律（先读完再动手）

1. **提交前必须本地全绿**：`make check` 通过，且 `usa . --approval-id CHG-LOCAL --format sarif --out results.sarif --allow-findings` 能生成可解析的 SARIF。
2. **新增检测规则必须配套 Golden Test**：只加正则不加 `tests/fixtures/` 里的样本与期望结果，PR 直接关闭。没有测试的规则等于没有规则。

## 开发流程

1. **Fork** 本仓库到你自己的 GitHub 账号。
2. **Clone**：
   ```bash
   git clone https://github.com/<your-name>/ultimate-security-audit.git
   cd ultimate-security-audit
   ```
3. **建分支**：基于 `main` 建功能或修复分支。
4. **装依赖**：
   ```bash
   pip install -e ".[dev]"
   ```
5. **提交前自检**：必须全绿。
   ```bash
   make check
   ```
   装了命令行的顺带确认入口没断：
   ```bash
   pip install -e . && usa --help > /dev/null && python -m scripts --help > /dev/null
   ```
   它包含四步：文档死链校验、pytest、门控冒烟（缺审批号必须 `exit 2`）、SARIF 冒烟。
6. **改到 fixture** 时同步重新生成期望报告，否则 `tests/test_golden.py` 会红：
   ```bash
   make regen-fixture
   ```
7. **提交并签署 DCO**：每个 commit 末尾必须有一行 `Signed-off-by`：
   ```bash
   git commit -s -m "feat: your change"
   ```
   这行签名代表你声明该提交符合 [Developer Certificate of Origin](https://developercertificate.org/) v1.1。
8. **Push** 到你的 fork，再向 `Trace520/ultimate-security-audit` 的 `main` 提 Pull Request。

## PR 审查标准

- 一个 PR 只做一件事，不要混改。
- 必须通过 CI（`.github/workflows/ci.yml`）。
- **文档里不要引用不存在的文件**：反引号里的相对路径由 `scripts/check_docs.py` 校验，它按当前 md 所在目录解析，运行时产物（如 `audit_notes.md`）已在白名单里。
- 涉及示例（`examples/sample_code.js`）的改动，请同时更新 `examples/audit_notes.md` 与 `examples/audit_report.md`，保证密钥值、行号、函数名三者与样本一致。
- 涉及 `tests/fixtures/sample/sample_code.js` 的改动，必须跑 `make regen-fixture`。
- 新增外部依赖时，在 `SKILL.md` 第 3 节的降级表与 `references/fallback-matrix.md` 中补本地等价做法，并在 `scripts/skill_probe.py` 里登记探测项。
- 改状态机语义时，同步更新 `references/state-machine.md` 与 `tests/test_state_machine.py`；宁可加断言，不要放宽前置条件。
- 新增输出格式时，在 `references/audit-report.md` 补示例，并确保 `--format json` 的 stdout 只有 JSON。
- 关键入口变更后，在 `tests/test_repo_integrity.py` 的 `DECLARED` 列表里同步增删。
- 版本号三处必须一致：`pyproject.toml`、`SKILL.md` frontmatter、`scripts/run_audit.py` 的 `VERSION`。

## 安全相关贡献

- 不要在 PR 或 Issue 中泄露真实目标的 IP、域名、凭证或未公开漏洞细节。
- 发现本仓库自身的安全问题，请走 [SECURITY.md](SECURITY.md) 里的私密通道，不要公开提 Issue。
- 不要把门控改成可被环境变量单点绕过的形态。任何「先跑起来再说」的改动都会被拒。
