# Auth Service Dockerfile  
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录和设置权限
RUN mkdir -p /app/data /app/logs \
    && chmod 755 /app/data /app/logs

# 创建非root用户
RUN groupadd -r auth && useradd --no-log-init -r -g auth auth \
    && chown -R auth:auth /app

# 切换到非root用户
USER auth

# 暴露端口
EXPOSE 8001

# 健康检查
HEALTHCHECK --interval=60s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8001/api/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]