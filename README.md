# Auth Service

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

基于FastAPI构建的可扩展用户认证微服务，支持多租户和多种认证方式。

## ✨ 功能特性

- 🔐 **多种认证方式** - 邮箱/密码、手机/短信、微信、QQ、谷歌OAuth
- 🔑 **JWT令牌管理** - 安全的基于令牌的认证和刷新机制
- 🏢 **多租户支持** - 完整的租户隔离和可配置配额
- 👤 **用户资料管理** - 全面的用户数据和兴趣画像
- ⚡ **高性能** - Redis缓存、连接池、异步操作
- 📊 **监控与健康检查** - 内置指标、日志和健康检查端点
- 🛡️ **安全特性** - 限流、CORS、输入验证、SQL注入防护

## 🚀 快速开始

### 开发环境

```bash
# 克隆并安装
git clone https://github.com/superxabc/auth-service.git
cd auth-service
pip install -r requirements.txt

# 配置环境
cp env.example .env

# 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

**访问地址:**
- API文档: http://localhost:8001/docs
- 健康检查: http://localhost:8001/api/health

### Docker部署

```bash
# 构建和运行
docker build -t auth-service .
docker run -p 8001:8001 auth-service
```

### 生产部署

```bash
cd ../deployment-scripts
./orchestration/deploy_all_services.sh --mode=production --services=auth-service
```

## 📊 架构设计

**数据模型:**
- user_core (用户核心信息，支持租户隔离)
- user_profile (用户资料和偏好设置)
- user_interests (用户兴趣画像数据)
- user_app_usage (应用使用记录)

**认证支持:**
- 🇨🇳 **中国地区**: 微信、QQ、手机+验证码
- 🌍 **海外地区**: 谷歌OAuth、邮箱+密码、苹果登录

**多租户:** 所有核心表支持`tenant_id`字段，确保数据隔离。

## 📚 API使用

### 核心接口
```bash
# 认证头
Authorization: Bearer <token>

# 用户认证
POST /api/user/auth
{
  "provider": "email|phone|wechat|qq|google",
  "credentials": {...},
  "tenant_id": "my-app",
  "region": "china|global"
}

# 用户管理
GET /api/user/profile              # 获取资料
PUT /api/user/profile              # 更新资料
POST /api/user/verify              # 令牌验证
```

**完整API文档**: http://localhost:8001/docs

## ⚙️ 配置

核心环境变量:
```bash
DATABASE_URL=postgresql://user:password@host:port/db
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
MAX_REQUESTS_PER_MINUTE=60
```

详细配置请参考 `env.example` 文件。

## 🧪 测试与开发

```bash
# 测试
pytest tests/
curl http://localhost:8001/api/health

# 数据库迁移
alembic upgrade head
alembic revision --autogenerate -m "description"

# 缓存管理
redis-cli DEL "user:tenant_id:user_id:*"
```

## 📈 监控

- **健康检查**: `/api/health` - 数据库和Redis连接状态
- **系统指标**: `/api/metrics` - 性能监控数据
- **结构化日志**: JSON格式，支持集中化收集

## 🤝 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送分支 (`git push origin feature/amazing-feature`)
5. 打开拉取请求

## 📄 许可证

本项目采用MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

- **文档**: [API文档](http://localhost:8001/docs)
- **问题反馈**: [GitHub Issues](https://github.com/superxabc/auth-service/issues)

---

**Auth Service** - 构建现代化、可扩展的用户认证微服务 🚀