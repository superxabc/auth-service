# Auth Service

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

一个基于FastAPI构建的可扩展用户认证微服务，支持多租户和多种认证方式。

## ✨ 功能特性

- 🔐 **多种认证方式** - 邮箱/密码、手机/短信、微信、QQ、谷歌OAuth
- 🔑 **JWT令牌管理** - 安全的基于令牌的认证和刷新机制
- 🏢 **多租户支持** - 完整的租户隔离和可配置配额
- 👤 **用户资料管理** - 全面的用户数据和兴趣画像
- ⚡ **高性能** - Redis缓存、连接池、异步操作
- 📊 **监控与健康检查** - 内置指标、日志和健康检查端点
- 🛡️ **安全特性** - 限流、CORS、输入验证、SQL注入防护
- 🐳 **容器化就绪** - 支持Docker Compose的容器化部署

## 🚀 快速开始

### 开发环境

1. **克隆仓库并安装依赖**:
   ```bash
   git clone https://github.com/superxabc/auth-service.git
   cd auth-service
   pip install -r requirements.txt
   ```

2. **配置环境变量**:
   ```bash
   cp env.example .env
   # 编辑.env文件配置数据库和Redis连接
   ```

3. **启动服务**:
   ```bash
   # 开发模式
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

4. **访问API**:
   - API文档: http://localhost:8001/docs
   - 健康检查: http://localhost:8001/api/health

### Docker部署

```bash
# 使用Docker构建和运行
docker build -t auth-service .
docker run -p 8001:8001 auth-service
```

### 生产部署

生产环境请使用统一的微服务部署系统：
```bash
cd ../deployment-scripts
./orchestration/deploy_all_services.sh --mode=production --services=auth-service
```

## 📊 架构设计

### 数据模型
- **user_core** - 用户核心信息，支持租户隔离
- **user_profile** - 用户资料和偏好设置
- **user_interests** - 用户兴趣画像数据
- **user_app_usage** - 应用使用记录

### 认证方式

**🇨🇳 中国地区:**
- 微信登录
- QQ登录
- 手机号+验证码

**🌍 海外地区:**
- 谷歌OAuth 2.0
- 邮箱+密码
- 苹果登录 (预留)

### 多租户支持
所有核心表都支持`tenant_id`字段，确保租户间的完整数据隔离。

## 📚 API使用

### 认证
```bash
# 邮箱/密码登录
POST /api/user/auth
{
  "provider": "email",
  "credentials": {
    "email": "user@example.com",
    "password": "password123"
  },
  "tenant_id": "my-app",
  "region": "global"
}

# 手机登录（中国）
POST /api/user/auth
{
  "provider": "phone",
  "credentials": {
    "phone": "13800138000",
    "code": "123456"
  },
  "tenant_id": "my-app",
  "region": "china"
}
```

### 用户管理
```bash
# 获取用户资料
GET /api/user/profile
Headers: Authorization: Bearer <token>

# 更新用户资料
PUT /api/user/profile
Headers: Authorization: Bearer <token>
{
  "nickname": "新昵称",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

### 完整API文档
- 交互式API文档: http://localhost:8001/docs
- OpenAPI规范: http://localhost:8001/openapi.json

## ⚙️ 配置

### 环境变量
```bash
# 数据库
DATABASE_URL=postgresql://user:password@host:port/db

# Redis缓存
REDIS_URL=redis://localhost:6379

# JWT令牌
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 限流配置
MAX_REQUESTS_PER_MINUTE=60
```

完整配置选项请参考`env.example`文件。

## 🧪 测试

```bash
# 运行测试
pytest tests/

# 健康检查
curl http://localhost:8001/api/health

# 负载测试
wrk -t12 -c400 -d30s http://localhost:8001/api/health
```

## 📈 监控

- **健康检查**: `/api/health` - 数据库和Redis连接状态
- **指标**: `/api/metrics` - 系统性能指标
- **日志**: 结构化JSON格式的应用日志
- **缓存**: 基于Redis的可配置TTL缓存

## 🔧 开发

### 数据库迁移
```bash
# 创建迁移
alembic revision --autogenerate -m "Migration description"

# 应用迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

### 缓存管理
```bash
# 清理用户缓存
redis-cli DEL "user:tenant_id:user_id:*"

# 清理所有缓存
redis-cli FLUSHDB
```

## 🤝 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开拉取请求

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

- **文档**: [API文档](http://localhost:8001/docs)
- **问题反馈**: [GitHub Issues](https://github.com/superxabc/auth-service/issues)
- **健康检查**: [服务健康状态](http://localhost:8001/api/health)

---

**Auth Service** - 构建现代化、可扩展的用户认证微服务 🚀