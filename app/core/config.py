import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 环境配置
    environment: str = "development"
    debug: bool = False
    
    # 服务配置
    app_name: str = "Auth Service"
    app_version: str = "0.2.0"
    api_prefix: str = "/api"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./auth.db"
    database_pool_size: int = 10
    database_max_overflow: int = 20
    
    # Redis配置
    redis_url: str = "redis://localhost:6379"
    redis_password: Optional[str] = None
    redis_db: int = 0
    
    # JWT认证配置
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天
    
    # 安全配置
    cors_origins: list = ["*"]
    trusted_hosts: list = ["*"]
    
    # 限流配置
    rate_limit_enabled: bool = True
    max_requests_per_minute: int = 60
    max_requests_per_hour: int = 1000
    
    # 日志配置
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 缓存配置
    cache_ttl_seconds: int = 3600  # 1小时
    session_cache_ttl: int = 1800  # 30分钟
    
    # 健康检查配置
    health_check_timeout: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

def get_settings() -> Settings:
    """获取配置单例"""
    return Settings()

settings = get_settings()
