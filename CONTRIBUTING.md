# Contributing

感谢你对 `ultimate-security-audit` 的兴趣。以下是参与贡献的流程。

## 开发流程

1. **Fork** 本仓库到你自己的 GitHub 账号。
2. **Clone** 你 fork 出来的仓库到本地：
   ```bash
   git clone https://github.com/<your-name>/ultimate-security-audit.git
   cd ultimate-security-audit
   ```
3. **建分支**：基于 `main` 建一个功能或修复分支：
   ```bash
   git checkout -b feat/your-feature
   # 或
   git checkout -b fix/your-bugfix
   ```
4. **改代码**：遵循仓库现有的代码风格与目录结构。
5. **本地自检**：
   - Markdown 文件确认链接可打开、Mermaid 可渲染；**文中出现的路径必须真实存在**，能在终端里 Tab 补全。
   - Python 文件确认能编译：
     ```bash
     python -m py_compile api/openai_compatible.py scripts/run_audit.py examples/verify_xor_key.py
     ```
   - 改到 `examples/` 时，跑一遍示例链路，确认样本、笔记、报告三者对得上：
     ```bash
     python examples/verify_xor_key.py
     ```
   - 改到 `scripts/run_audit.py` 时，确认门控仍然 fail-closed（缺审批号必须 `exit 2`）：
     ```bash
     AUTHORIZATION_MODE=CI_PIPELINE python scripts/run_audit.py --targets examples/sample_code.js; echo "exit=$?"
     ```
   - 不要提交 `.env`、`__pycache__/`、密钥或私有靶场数据。
6. **提交并签署 DCO**：每个 commit 必须在末尾加一行 `Signed-off-by`：
   ```bash
   git commit -s -m "feat: your change"
   ```
   `-s` 参数会自动加上：
   ```text
   Signed-off-by: Your Name <your.email@example.com>
   ```
   这行签名代表你声明该提交符合 [Developer Certificate of Origin](https://developercertificate.org/) v1.1，即你有权利提交这段代码且同意开源许可。
7. **Push** 到你的 fork：
   ```bash
   git push origin feat/your-feature
   ```
8. **开 PR**：在 GitHub 上向 `Trace520/ultimate-security-audit` 的 `main` 分支提 Pull Request，填写描述模板。

## PR 审查标准

- 一个 PR 只做一件事，不要混改。
- 必须通过 CI（`.github/workflows/ci.yml`）与代码审查。
- 涉及示例（`examples/`）的改动，请同时更新对应的 `examples/audit_notes.md` 与 `examples/audit_report.md`，保证密钥值、行号、函数名三者与 `examples/sample_code.js` 一致。
- 文档里不要引用不存在的文件。若某个能力依赖外部技能或引擎，在 `skill/SKILL.md` 第 3.1 节登记降级做法，而不是假定用户已安装。

## 安全相关贡献

- 不要在 PR 或 Issue 中泄露真实目标的 IP、域名、凭证或未公开漏洞细节。
- 发现本仓库自身的安全问题，请走 [SECURITY.md](SECURITY.md) 里的私密通道，不要公开提 Issue。
