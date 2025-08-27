import json
import redis
from typing import Optional, Any
from .config import settings

class CacheService:
    """Redis缓存服务"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            settings.redis_url,
            password=settings.redis_password,
            db=settings.redis_db,
            decode_responses=True
        )
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """设置缓存值"""
        try:
            ttl = ttl or settings.cache_ttl_seconds
            serialized_value = json.dumps(value, default=str)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            print(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """删除缓存"""
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            print(f"Cache delete error: {e}")
            return False
    
    def clear_user_cache(self, user_id: str, tenant_id: str = "default") -> bool:
        """清理用户相关缓存"""
        try:
            pattern = f"user:{tenant_id}:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                return bool(self.redis_client.delete(*keys))
            return True
        except Exception as e:
            print(f"Cache clear error: {e}")
            return False
    
    def health_check(self) -> bool:
        """缓存健康检查"""
        try:
            return self.redis_client.ping()
        except Exception:
            return False

# 全局缓存实例
cache = CacheService()

def get_cache() -> CacheService:
    """获取缓存服务实例"""
    return cache