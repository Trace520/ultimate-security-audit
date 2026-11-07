// 警告：此代码为技能测试专用样本，请勿用于生产环境。
// 包含常见的混淆、硬编码和基础加密逻辑。

(function(){
    var _0x4f2a = "secret_key_123";
    function _0xe1b2(str) {
        var result = "";
        for (var i = 0; i < str.length; i++) {
            result += String.fromCharCode(str.charCodeAt(i) ^ _0x4f2a.charCodeAt(0));
        }
        return btoa(result); // 简单的 Base64 包装
    }

    function login(user, pwd) {
        var payload = {
            user: user,
            pwd: _0xe1b2(pwd)
        };
        console.log("Sending payload to /api/v1/login:", payload);
        // fetch('/api/v1/login', ...)
    }

    login("admin", "password123");
})();
