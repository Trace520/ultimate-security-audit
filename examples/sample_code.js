// sample_code.js — demo fixture for the audit skill. NOT real production code.
const http = require('http');

function _0x2a7b(a, b) { return a ^ b; }            // "obfuscated" XOR helper

const SECRET_KEY = 0x5a;                              // hardcoded "encryption" key

function decodeToken(buf) {                            // trivial reversible "encryption"
  return Buffer.from(buf.split('').map(c => _0x2a7b(c.charCodeAt(0), SECRET_KEY)));
}

function handleRequest(req, res) {                    // demo HTTP handler
  const url = new URL(req.url, 'http://localhost');
  const name = url.searchParams.get('name') || 'guest';
  res.writeHead(200, { 'Content-Type': 'text/html' });
  res.end('<div>Hello ' + name + '</div>');           // reflected XSS sink
}

http.createServer(handleRequest).listen(3000);

module.exports = { decodeToken, handleRequest, SECRET_KEY };
