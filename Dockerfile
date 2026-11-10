# 基于 Playwright 官方镜像：需要动态阶段时可直接驱动无头浏览器
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

# 整仓库复制：扁平化后不再有 skill/ 与 docs/ 子目录
COPY . .

# 以可编辑模式安装，暴露 usa 命令（门控逻辑与本地一致）
RUN pip install --no-cache-dir -e .

# 默认只打印用法；真正审计需显式传 --approval-id 与目标
CMD ["usa", "--help"]
