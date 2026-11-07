# 工具链配置指南

本技能本身不直接执行抓包、反混淆或反编译，而是编排底层工具。以下工具均用于**已授权**的安全审计场景（自有应用、开源项目、已获书面授权的目标、恶意样本分析环境）。

## 抓包 / 浏览器自动化

```bash
npx -y @playwright/mcp@latest
```

用于抓取前端网络请求、复现登录态、观察 API 调用链。

## 反混淆

```bash
npm install -g webcrack
```

用于解包混淆过的前端 JS（webpack 打包产物、混淆变量语义还原）。

## 反编译

- **Ghidra**（NSA 开源，二进制逆向）：https://ghidra-sre.org/
- **jadx**（Android APK 反编译）：https://github.com/skylot/jadx

## 使用边界

- 仅对自有应用、开源项目或已获书面授权的目标使用上述工具。
- 不对商业产品的 license 校验、DRM、反调试保护进行脱壳或绕过。
- 恶意样本分析请在隔离的虚拟机/沙箱中进行，避免扩散。
