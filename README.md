# Auth Service v0.2.0

一个可扩展的微服务，用于用户认证、管理和多租户支持。

## 🚀 快速开始

### 开发环境
1. **克隆仓库并安装依赖**:
   ```bash
   git clone <repository>
   cd auth-service
   pip install -r requirements.txt
   ```

2. **配置环境变量**:
   ```bash
   cp env.example .env
   # .env 文件包含本地开发的默认配置，通常无需修改
   ```

3. **启动服务**:
   ```bash
   # 开发模式
   uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
   ```

### 生产部署
生产环境请使用统一的微服务部署系统：
```bash
cd ../deployment-scripts
./orchestration/deploy_all_services.sh --mode=production --services=auth-service
```

## 🚀 功能特性

### 核心功能
- ✅ **多种认证方式** - 支持中国大陆和海外不同认证方式
- ✅ **用户认证与授权** - JWT令牌管理，设备ID登录
- ✅ **多租户支持** - 完整的租户隔离机制
- ✅ **用户资料管理** - 基础信息、兴趣画像、使用记录

### 架构特性
- 🔄 **Redis缓存层** - 提升查询性能，减少数据库压力
- 📊 **监控与日志** - 完整的健康检查、指标收集、请求日志
- 🛡️ **安全防护** - 限流、CORS、输入验证
- 🐳 **容器化部署** - Docker + Docker Compose
- 📈 **性能优化** - 数据库连接池、缓存策略
- 🔧 **配置管理** - 环境分离、动态配置

## 📊 数据模型

### 数据表结构（4张表）
```sql
user_core         -- 用户核心信息（支持租户隔离）
user_profile      -- 用户基础资料
user_interests    -- 用户画像数据（通用化设计）
user_app_usage    -- 应用使用记录
```

### 认证方式支持
**🇨🇳 中国大陆:**
- 微信登录 (WeChat)
- QQ登录 (QQ Connect)  
- 手机号+验证码

**🌍 海外:**
- Google OAuth 2.0
- 邮箱+密码
- Apple Sign-In (预留)

### 租户隔离支持
所有核心表都支持 `tenant_id` 字段，确保不同租户的数据完全隔离。

## 🛠️ 快速开始

### 环境要求
- Python 3.10+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### 开发环境启动

1. **克隆项目**
```bash
git clone <repository>
cd auth-service
```

2. **启动服务**
```bash
# 启动数据库和Redis
docker-compose up -d auth-db auth-redis

# 等待服务就绪后启动应用
docker-compose up auth-backend
```

3. **验证服务**
```bash
# 健康检查
curl http://localhost:8001/api/health

# API文档
open http://localhost:8001/docs

# 测试邮箱登录
curl -X POST "http://localhost:8001/api/user/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "email",
    "credentials": {
      "email": "test@example.com", 
      "password": "password123"
    },
    "tenant_id": "demo",
    "region": "global"
  }'
```

### 生产环境部署

1. **环境配置**
```bash
# 创建生产环境配置
cp .env.example .env.production
```

2. **数据库迁移**
```bash
# 运行数据库迁移
alembic upgrade head
```

3. **启动服务**
```bash
ENVIRONMENT=production docker-compose up -d
```

## 📚 API 接口

### 认证接口
```bash
# 设备ID登录/注册（兼容模式）
POST /api/user/login
{
  "device_id": "unique-device-id",
  "tenant_id": "your-tenant",
  "product_id": "your-product"
}

# 多种认证方式统一登录
POST /api/user/auth
{
  "provider": "email|phone|wechat|qq|google",
  "credentials": {
    "email": "user@example.com",
    "password": "password123"
  },
  "tenant_id": "your-tenant",
  "region": "china|global"
}

# 获取支持的认证方式
GET /api/user/auth/providers?region=china

# 令牌验证
POST /api/user/verify
Headers: Authorization: Bearer <token>
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
  "avatar_url": "https://example.com/avatar.jpg",
  "gender": "male|female|other|prefer_not_say",
  "birth_year": 1990,
  "region": "上海",
  "language_preference": "zh-CN"
}

# 获取用户兴趣画像
GET /api/user/interests
Headers: Authorization: Bearer <token>

# 创建/更新用户兴趣画像
POST /api/user/interests
Headers: Authorization: Bearer <token>
{
  "primary_category": "learning|creative|work|entertainment|other",
  "interest_data": {
    "tags": ["AI", "编程", "设计"],
    "level": "intermediate"
  },
  "preferred_format": "concise|detailed|step_by_step",
  "schema_version": "1.0"
}

# 记录应用使用情况
POST /api/user/app_usage
Headers: Authorization: Bearer <token>
{
  "device_type": "iOS|Android|Web",
  "app_version": "1.0.0",
  "session_start_time": "2025-01-01T12:00:00",
  "session_end_time": "2025-01-01T12:30:00",
  "duration_seconds": 1800
}
```

### 系统监控
```bash
# 健康检查
GET /api/health

# 就绪检查
GET /api/ready

# 存活检查
GET /api/live

# 系统指标
GET /api/metrics
```

## 📋 接口概览

### 完整接口列表

| 接口路径 | 方法 | 功能描述 | 认证要求 |
|---------|------|----------|----------|
| `/` | GET | 服务基本信息 | 无 |
| `/api/user/login` | POST | 设备ID登录/注册 | 无 |
| `/api/user/auth` | POST | 多种认证方式统一登录 | 无 |
| `/api/user/auth/providers` | GET | 获取支持的认证方式 | 无 |
| `/api/user/verify` | POST | JWT令牌验证 | Bearer Token |
| `/api/user/profile` | GET | 获取用户资料 | Bearer Token |
| `/api/user/profile` | PUT | 更新用户资料 | Bearer Token |
| `/api/user/interests` | GET | 获取用户兴趣画像 | Bearer Token |
| `/api/user/interests` | POST | 创建/更新兴趣画像 | Bearer Token |
| `/api/user/app_usage` | POST | 记录应用使用情况 | Bearer Token |
| `/api/health` | GET | 系统健康检查 | 无 |
| `/api/ready` | GET | 服务就绪检查 | 无 |
| `/api/live` | GET | 服务存活检查 | 无 |
| `/api/metrics` | GET | 系统运行指标 | 无 |

### 认证方式详细说明

#### 📱 不同地区支持的认证方式

**中国大陆 (region: china)**
```json
{
  "wechat": {
    "credentials": {"code": "wechat_auth_code"}
  },
  "qq": {
    "credentials": {"access_token": "qq_access_token"}
  },
  "phone": {
    "credentials": {"phone": "13800138000", "code": "123456"}
  }
}
```

**海外 (region: global)**
```json
{
  "google": {
    "credentials": {"id_token": "google_id_token"}
  },
  "email": {
    "credentials": {"email": "user@example.com", "password": "password123"}
  },
  "apple": {
    "credentials": {"id_token": "apple_id_token"}
  }
}
```

### 响应状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 认证失败或令牌无效 |
| 404 | 资源未找到 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |
| 503 | 服务不可用 |

## 🔧 配置说明

### 环境变量
```bash
# 基础配置
ENVIRONMENT=development        # 环境：development/staging/production
DEBUG=true                    # 调试模式

# 数据库配置
DATABASE_URL=postgresql://user:password@host:port/db
DATABASE_POOL_SIZE=10         # 连接池大小
DATABASE_MAX_OVERFLOW=20      # 最大溢出连接

# Redis配置
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=               # Redis密码（可选）
REDIS_DB=0                   # Redis数据库编号

# JWT配置
SECRET_KEY=your-secret-key   # JWT密钥
ACCESS_TOKEN_EXPIRE_MINUTES=30  # 令牌过期时间

# 限流配置
MAX_REQUESTS_PER_MINUTE=60   # 每分钟最大请求数
MAX_REQUESTS_PER_HOUR=1000   # 每小时最大请求数

# 缓存配置
CACHE_TTL_SECONDS=3600       # 缓存过期时间（秒）
```

### 租户配置
```python
# 基础租户配置
{
  "tenant_id": "default",
  "product_id": null
}
```

## 💡 使用示例

### 完整的用户认证流程

#### 1. 邮箱登录示例
```bash
# 邮箱登录
response=$(curl -s -X POST "http://localhost:8001/api/user/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "email",
    "credentials": {
      "email": "john@example.com",
      "password": "securepassword"
    },
    "tenant_id": "my-app",
    "region": "global"
  }')

echo $response
# 输出: {"token":"eyJ...","user_id":"123","nickname":"John"}

# 提取token
token=$(echo $response | jq -r '.token')
```

#### 2. 获取用户资料
```bash
curl -X GET "http://localhost:8001/api/user/profile" \
  -H "Authorization: Bearer $token"
```

#### 3. 更新用户兴趣
```bash
curl -X POST "http://localhost:8001/api/user/interests" \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "primary_category": "learning",
    "interest_data": {
      "topics": ["AI", "编程", "产品设计"],
      "level": "intermediate",
      "goals": ["提升技能", "职业发展"]
    },
    "preferred_format": "detailed"
  }'
```

#### 4. 记录使用情况
```bash
curl -X POST "http://localhost:8001/api/user/app_usage" \
  -H "Authorization: Bearer $token" \
  -H "Content-Type: application/json" \
  -d '{
    "device_type": "Web",
    "app_version": "1.0.0",
    "session_start_time": "'$(date -u +%Y-%m-%dT%H:%M:%S)'",
    "duration_seconds": 1800
  }'
```

### 不同地区认证示例

#### 中国大陆 - 手机号登录
```bash
curl -X POST "http://localhost:8001/api/user/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "phone",
    "credentials": {
      "phone": "13800138000",
      "code": "123456"
    },
    "tenant_id": "china-app",
    "region": "china"
  }'
```

#### 海外 - Google登录
```bash
curl -X POST "http://localhost:8001/api/user/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "google", 
    "credentials": {
      "id_token": "google_oauth_id_token"
    },
    "tenant_id": "global-app",
    "region": "global"
  }'
```

### 多租户使用示例

#### 为不同产品创建用户
```bash
# 产品A的用户
curl -X POST "http://localhost:8001/api/user/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "email",
    "credentials": {"email": "user@example.com", "password": "pass123"},
    "tenant_id": "company-x",
    "product_id": "product-a"
  }'

# 产品B的用户 (同一租户，不同产品)
curl -X POST "http://localhost:8001/api/user/auth" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "email", 
    "credentials": {"email": "user@example.com", "password": "pass123"},
    "tenant_id": "company-x",
    "product_id": "product-b"
  }'
```

## 🧪 测试

### 单元测试
```bash
pytest tests/
```

### 性能测试
```bash
# 使用wrk进行压力测试
wrk -t12 -c400 -d30s http://localhost:8001/api/health
```

### 健康检查测试
```bash
# 数据库连接测试
curl http://localhost:8001/api/ready

# 完整健康检查
curl http://localhost:8001/api/health

# 系统指标
curl http://localhost:8001/api/metrics
```

## 📈 监控与维护

### 日志管理
```bash
# 查看应用日志
docker-compose logs -f auth-backend

# 查看数据库日志
docker-compose logs -f auth-db

# 查看Redis日志
docker-compose logs -f auth-redis
```

### 性能监控
- **响应时间**: 所有请求都有 `X-Process-Time` 响应头
- **缓存命中率**: 响应头 `X-Cache` 显示 HIT/MISS 状态
- **数据库连接池**: `/api/metrics` 提供连接池状态

### 缓存管理
```bash
# 清理特定用户缓存
redis-cli DEL "user:tenant_id:user_id:*"

# 清理所有缓存
redis-cli FLUSHDB
```

## 🔄 数据库迁移

### 创建迁移
```bash
alembic revision --autogenerate -m "Migration description"
```

### 执行迁移
```bash
alembic upgrade head
```

### 回滚迁移
```bash
alembic downgrade -1
```

## 📊 架构设计

### 系统架构图
```
┌─────────────────┐
│   API Gateway   │ <- 统一入口、认证、限流
└─────────────────┘
         │
┌─────────────────┐
│  Auth Service   │ <- 用户认证服务
└─────────────────┘
         │
┌─────────────────┐
│   PostgreSQL    │ <- 数据持久化
└─────────────────┘
         │
┌─────────────────┐
│     Redis       │ <- 缓存层
└─────────────────┘
```

### 多租户架构
- **租户隔离**: 所有数据表支持 `tenant_id` 字段
- **配额管理**: 灵活的 JSONB 配置系统
- **功能开关**: 基于租户的功能控制

## 🔐 安全最佳实践

1. **JWT令牌管理**
   - 使用强密钥（至少32字符）
   - 设置合理的过期时间
   - 支持令牌刷新机制

2. **数据库安全**
   - 使用连接池
   - 参数化查询防止SQL注入
   - 定期备份数据

3. **API安全**
   - 请求限流
   - CORS配置
   - 输入验证

4. **缓存安全**
   - 敏感数据不缓存
   - 设置合理的TTL
   - Redis密码保护

## 🚀 性能优化

### 数据库优化
- 使用连接池管理连接
- 添加必要的索引
- 优化查询语句
- 定期清理日志数据

### 缓存策略
- **用户资料**: 缓存1小时，修改时自动清理
- **认证令牌**: 内存缓存30分钟  
- **用户兴趣画像**: 缓存2小时，更新时清理
- **系统配置**: 缓存4小时
- **API响应**: 根据接口重要性缓存5-60分钟

### 接口优化
- 响应时间监控
- 异步处理非关键操作
- 合理的分页设计

## 📋 版本历史

### v0.2.0 (当前版本)
- ✅ 多租户支持
- ✅ Redis缓存层
- ✅ 完整监控体系
- ✅ 性能优化
- ✅ 通用化数据模型

### v0.1.0
- ✅ 基础用户认证
- ✅ 数据模型设计
- ✅ Docker化部署

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持与联系

- **文档**: [API文档](http://localhost:8001/docs)
- **监控**: [健康检查](http://localhost:8001/api/health)
- **问题反馈**: 请提交 Issue

---

**Auth Service** - 构建现代化、可扩展的用户认证微服务 🚀
