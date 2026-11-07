# reverse_notes.md — 审查笔记（示例）

> 这是 skill 分析 `examples/sample_code.js` 时应产出的笔记样式。按时间倒序累积。

## 静态资产发现

- 语言：Node.js，依赖内置 `http`、`Buffer`
- 入口：`http.createServer(handleRequest).listen(3000)`
- 导出：`decodeToken`、`handleRequest`、`SECRET_KEY`
- 可疑点：
  - 第 4 行 `_0x2a7b(a, b)` 函数名混淆
  - 第 6 行 `SECRET_KEY = 0x5a` 硬编码常量
  - 第 13 行 `res.end('<div>Hello ' + name + ...)` 字符串拼接进 HTML

## 中间层降维

- `_0x2a7b(a, b)` 还原：`return a ^ b`（纯 XOR，无其他运算）
- `decodeToken(buf)` 还原：对每个字符做 `charCode ^ 0x5a`，再包成 Buffer
- “加密”结论：对称 XOR，密钥硬编码在源码里 → 任何人拿到源码即可逆，不构成真实保护
- 数据流：
  - `url.searchParams.get('name')` → `name`
  - `name` 直接拼到 HTML 响应里（未转义）

## 深度推演

- 外部输入路径：`GET /?name=<attacker-controlled>`
- Sink：`res.end(...)` 直接回写 HTML
- 缺失：未做 HTML 转义、未设置 CSP、未做输入白名单
- 待确认：是否对 `name` 长度做了限制？当前文件无法判断。
