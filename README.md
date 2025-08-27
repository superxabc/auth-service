# Auth Service

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

A scalable microservice for user authentication, management, and multi-tenant support built with FastAPI.

一个基于FastAPI构建的可扩展用户认证微服务，支持多租户和多种认证方式。

## ✨ Features / 功能特性

- 🔐 **Multiple Authentication Methods** - Email/Password, Phone/SMS, WeChat, QQ, Google OAuth
- 🔑 **JWT Token Management** - Secure token-based authentication with refresh mechanism
- 🏢 **Multi-tenant Support** - Complete tenant isolation with configurable quotas
- 👤 **User Profile Management** - Comprehensive user data and interest profiling
- ⚡ **High Performance** - Redis caching, connection pooling, async operations
- 📊 **Monitoring & Health Checks** - Built-in metrics, logging, and health endpoints
- 🛡️ **Security Features** - Rate limiting, CORS, input validation, SQL injection protection
- 🐳 **Docker Ready** - Containerized deployment with Docker Compose support

## 🚀 Quick Start / 快速开始

### Development Environment / 开发环境

1. **Clone and install dependencies / 克隆仓库并安装依赖**:
   ```bash
   git clone https://github.com/superxabc/auth-service.git
   cd auth-service
   pip install -r requirements.txt
   ```

2. **Configure environment / 配置环境变量**:
   ```bash
   cp env.example .env
   # Edit .env file with your database and Redis settings
   # 编辑.env文件配置数据库和Redis连接
   ```

3. **Start the service / 启动服务**:
   ```bash
   # Development mode / 开发模式
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

4. **Access the API / 访问API**:
   - API Documentation: http://localhost:8001/docs
   - Health Check: http://localhost:8001/api/health

### Docker Deployment / Docker部署

```bash
# Build and run with Docker
docker build -t auth-service .
docker run -p 8001:8001 auth-service
```

### Production Deployment / 生产部署

For production deployment, use the unified microservice deployment system:
```bash
cd ../deployment-scripts
./orchestration/deploy_all_services.sh --mode=production --services=auth-service
```

## 📊 Architecture / 架构设计

### Data Models / 数据模型
- **user_core** - Core user information with tenant isolation
- **user_profile** - User profile and preferences  
- **user_interests** - User interest profiling data
- **user_app_usage** - Application usage tracking

### Authentication Methods / 认证方式

**🇨🇳 China Region:**
- WeChat Login (微信登录)
- QQ Login (QQ登录)  
- Phone + SMS (手机号+验证码)

**🌍 Global Region:**
- Google OAuth 2.0
- Email + Password (邮箱+密码)
- Apple Sign-In (预留)

### Multi-tenant Support / 多租户支持
All core tables support `tenant_id` field for complete data isolation between tenants.

## 📚 API Usage / API使用

### Authentication / 认证
```bash
# Email/Password Login
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

# Phone Login (China)
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

### User Management / 用户管理
```bash
# Get user profile
GET /api/user/profile
Headers: Authorization: Bearer <token>

# Update user profile
PUT /api/user/profile
Headers: Authorization: Bearer <token>
{
  "nickname": "新昵称",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

### Full API Documentation / 完整API文档
- Interactive API Docs: http://localhost:8001/docs
- OpenAPI Spec: http://localhost:8001/openapi.json

## ⚙️ Configuration / 配置

### Environment Variables / 环境变量
```bash
# Database
DATABASE_URL=postgresql://user:password@host:port/db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
```

See `env.example` for complete configuration options.

## 🧪 Testing / 测试

```bash
# Run tests
pytest tests/

# Health check
curl http://localhost:8001/api/health

# Load testing
wrk -t12 -c400 -d30s http://localhost:8001/api/health
```

## 📈 Monitoring / 监控

- **Health Check**: `/api/health` - Database and Redis connectivity
- **Metrics**: `/api/metrics` - System performance metrics  
- **Logs**: Application logs with structured JSON format
- **Caching**: Redis-based caching with configurable TTL

## 🔧 Development / 开发

### Database Migrations / 数据库迁移
```bash
# Create migration
alembic revision --autogenerate -m "Migration description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Cache Management / 缓存管理
```bash
# Clear user cache
redis-cli DEL "user:tenant_id:user_id:*"

# Clear all cache
redis-cli FLUSHDB
```

## 🤝 Contributing / 贡献

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support / 支持

- **Documentation**: [API Docs](http://localhost:8001/docs)
- **Issues**: [GitHub Issues](https://github.com/superxabc/auth-service/issues)
- **Health Check**: [Service Health](http://localhost:8001/api/health)

---

**Auth Service** - Building modern, scalable authentication microservices 🚀