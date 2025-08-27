from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime
from typing import Dict, Any

from ..core.database import get_db
from ..core.cache import get_cache, CacheService
from ..core.config import settings

router = APIRouter()

@router.get("/health")
def health_check(
    db: Session = Depends(get_db),
    cache: CacheService = Depends(get_cache)
) -> Dict[str, Any]:
    """
    系统健康检查接口
    """
    health_status = {
        "service": "auth-service",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "status": "healthy",
        "checks": {}
    }
    
    # 数据库健康检查
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        health_status["checks"]["database"] = {
            "status": "unhealthy",
            "message": f"Database connection failed: {str(e)}"
        }
        health_status["status"] = "unhealthy"
    
    # Redis缓存健康检查
    try:
        if cache.health_check():
            health_status["checks"]["cache"] = {
                "status": "healthy", 
                "message": "Redis connection successful"
            }
        else:
            health_status["checks"]["cache"] = {
                "status": "unhealthy",
                "message": "Redis ping failed"
            }
            health_status["status"] = "degraded"  # 缓存失败不完全影响服务
    except Exception as e:
        health_status["checks"]["cache"] = {
            "status": "unhealthy",
            "message": f"Redis connection failed: {str(e)}"
        }
        health_status["status"] = "degraded"
    
    # 根据整体状态决定HTTP状态码
    if health_status["status"] == "unhealthy":
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@router.get("/ready")
def readiness_check(db: Session = Depends(get_db)) -> Dict[str, str]:
    """
    就绪检查 - 用于K8s readiness probe
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready"}
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail={"status": "not ready", "reason": str(e)}
        )

@router.get("/live")
def liveness_check() -> Dict[str, str]:
    """
    存活检查 - 用于K8s liveness probe
    """
    return {"status": "alive"}

@router.get("/metrics")
def get_metrics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    基础指标接口
    """
    try:
        # 数据库连接池状态
        engine = db.get_bind()
        pool = engine.pool
        
        metrics = {
            "database": {
                "pool_size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow()
            },
            "service": {
                "version": settings.app_version,
                "environment": settings.environment
            }
        }
        
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Failed to collect metrics", "message": str(e)}
        )
