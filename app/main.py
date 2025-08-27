from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .core.config import settings
from .core.database import engine
from .core.logging import setup_logging
from .core.middleware import RequestLoggingMiddleware, CacheMiddleware, limiter
from .models import user as user_model
from .api import user_api, health

# 设置日志
setup_logging()

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    description="A scalable microservice for user authentication and management.",
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# 添加限流器
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加自定义中间件
app.add_middleware(RequestLoggingMiddleware)
if settings.environment == "production":
    app.add_middleware(CacheMiddleware)

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    # 只在开发环境自动创建表，生产环境使用Alembic
    if settings.environment == "development":
        user_model.UserCore.metadata.create_all(bind=engine)
        user_model.UserProfile.metadata.create_all(bind=engine)
        user_model.UserInterests.metadata.create_all(bind=engine)
        user_model.UserAppUsage.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    pass

# 注册路由
app.include_router(health.router, prefix=settings.api_prefix, tags=["系统监控"])
app.include_router(user_api.router, prefix=f"{settings.api_prefix}/user", tags=["用户管理"])

@app.get("/")
def read_root():
    """根路径信息"""
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running"
    }
