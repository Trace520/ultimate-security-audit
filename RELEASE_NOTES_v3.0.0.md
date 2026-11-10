# 🛡️ Ultimate Security Audit (USA) v3.0.0

## 💥 Breaking Changes（破坏性更新）
- **目录结构扁平化**：废弃旧版嵌套的 skill 与 docs 目录，统一采用根目录 `SKILL.md` + `references/` 的 Agent Skills 标准扁平结构。
- **统一 CLI 入口**：`usa`（`pip install -e .`）/ `python -m scripts` / `python scripts/run_audit.py` 三入口等价，共用同一套门控。
- **强制性授权门控**：默认开启 Fail-Closed 机制，缺少 `--approval-id` 的 CI/CD 流水线将被直接拦截（退出码 2）。

## ✨ New Features（重磅新特性）
- **🧠 防幻觉状态机 (State Machine)**：强制先登记入口点证据（`--stage discovery`）才能解锁深度推演（`--stage verify`）；漏项、跳步、换审批号一律 `BLOCKED`。
- **📦 供应链漏洞扫描 (SCA)**：新增 `scripts/dep_scanner.py`，读取 `requirements.txt` / `package-lock.json` 的锁定版本，调用 OSV API 拉取已知漏洞；离线自动降级，绝不编造命中。
- **📊 SARIF 标准输出**：新增 `--format sarif`，报告可直通 GitHub Code Scanning、GitLab 与 VS Code 安全插件，实现 DevSecOps 闭环。
- **🔄 外部能力降级 (Fallback)**：新增 `scripts/skill_probe.py`。探测到环境缺失高级检索工具时，按 `references/fallback-matrix.md` 降级使用本地 `grep`，绝不中断任务。
- **⚙️ CI 自审计 (Dogfooding)**：CI 新增 `self-audit` job，用 `usa . --format sarif` 扫描自身并把结果上传到 Security 面板。

## 🛠️ Improvements（工程化增强）
- **文档死链校验**：`scripts/check_docs.py` 校验 Markdown 行内路径，CI 强制拦截引用了不存在文件的提交。
- **Golden Test 对齐**：`tests/fixtures/` + `tests/test_golden.py` 确保示例报告与实际运行结果一致；新增状态机 / SARIF / SCA 共 16 个测试。
- **版本一致性断言**：`pyproject.toml`、`SKILL.md` frontmatter、`run_audit.VERSION` 三处不一致时 CI 直接红。
- **跨平台矩阵**：CI 覆盖 ubuntu / windows × Python 3.10 / 3.12。

## 📦 如何升级
```bash
git pull origin main
pip install -e .
python -B tests/sandbox_test.py  # 验证本地环境
usa --help
```

> 提示：`examples/` 与 `tests/fixtures/` 里带演示用密钥，自我审计扫到属于预期结果。
