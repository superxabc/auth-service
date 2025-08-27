import logging
import sys
from typing import Dict, Any
from .config import settings

def setup_logging() -> None:
    """配置日志系统"""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=settings.log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic").setLevel(logging.INFO)

def get_logger(name: str) -> logging.Logger:
    """获取指定名称的logger"""
    return logging.getLogger(name)

class RequestLogger:
    """请求日志记录器"""
    
    @staticmethod
    def log_request(method: str, url: str, user_id: str = None, tenant_id: str = None):
        """记录请求日志"""
        logger = get_logger("request")
        logger.info(f"Request: {method} {url} - User: {user_id} - Tenant: {tenant_id}")
    
    @staticmethod
    def log_response(status_code: int, processing_time: float):
        """记录响应日志"""
        logger = get_logger("response")
        logger.info(f"Response: {status_code} - Time: {processing_time:.3f}s")
    
    @staticmethod
    def log_error(error: Exception, context: Dict[str, Any] = None):
        """记录错误日志"""
        logger = get_logger("error")
        context_str = f" - Context: {context}" if context else ""
        logger.error(f"Error: {str(error)}{context_str}", exc_info=True)
