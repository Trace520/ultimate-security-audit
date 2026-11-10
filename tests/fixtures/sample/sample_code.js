// 安全审计示例：用于 golden test
// 以下字符串故意包含可被 SECRET_RE 命中的模式。
const config = {
  endpoint: "https://api.example.com",
  secret_key_123: "should-be-flagged-by-audit",
};
module.exports = config;
