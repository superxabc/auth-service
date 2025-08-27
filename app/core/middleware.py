import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .config import settings
from .logging import RequestLogger
from .cache import get_cache

# 限流器配置
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.max_requests_per_minute}/minute", f"{settings.max_requests_per_hour}/hour"]
)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # 记录请求
        user_id = getattr(request.state, 'user_id', None)
        tenant_id = getattr(request.state, 'tenant_id', None)
        RequestLogger.log_request(
            request.method, 
            str(request.url), 
            user_id, 
            tenant_id
        )
        
        try:
            response = await call_next(request)
            processing_time = time.time() - start_time
            
            # 记录响应
            RequestLogger.log_response(response.status_code, processing_time)
            
            # 添加响应头
            response.headers["X-Process-Time"] = str(processing_time)
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            RequestLogger.log_error(e, {
                "method": request.method,
                "url": str(request.url),
                "processing_time": processing_time
            })
            raise

class CacheMiddleware(BaseHTTPMiddleware):
    """缓存中间件"""
    
    async def dispatch(self, request: Request, call_next):
        # 只对GET请求进行缓存
        if request.method != "GET":
            return await call_next(request)
        
        # 跳过健康检查等不需要缓存的接口
        if any(path in str(request.url) for path in ["/health", "/metrics", "/docs", "/openapi"]):
            return await call_next(request)
        
        cache = get_cache()
        cache_key = f"response:{request.method}:{request.url}"
        
        # 尝试从缓存获取
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(
                content=cached_response["content"],
                status_code=cached_response["status_code"],
                headers={"X-Cache": "HIT", **cached_response.get("headers", {})}
            )
        
        # 执行请求
        response = await call_next(request)
        
        # 缓存成功响应
        if response.status_code == 200:
            response_body = b""
            async for chunk in response.body_iterator:
                response_body += chunk
            
            cache.set(cache_key, {
                "content": response_body.decode(),
                "status_code": response.status_code,
                "headers": dict(response.headers)
            }, ttl=settings.cache_ttl_seconds)
            
            # 重新创建响应
            return Response(
                content=response_body,
                status_code=response.status_code,
                headers={"X-Cache": "MISS", **dict(response.headers)}
            )
        
        return response
