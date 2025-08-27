from sqlalchemy.orm import Session
from typing import Optional
from ..models import user as user_model
from ..core.security import create_access_token
from ..core.cache import get_cache
from datetime import datetime

def login_or_register_user(
    db: Session, 
    device_id: str, 
    tenant_id: str = "default", 
    product_id: Optional[str] = None
) -> user_model.UserLoginResponse:
    """处理用户的登录或注册逻辑（支持租户隔离）"""
    cache = get_cache()
    
    # 检查该 device_id 的用户是否已存在（支持租户隔离）
    db_user_core = db.query(user_model.UserCore).filter(
        user_model.UserCore.device_id == device_id,
        user_model.UserCore.tenant_id == tenant_id
    ).first()

    if db_user_core is None:
        # 用户不存在，创建一个新用户（注册）
        db_user_core = user_model.UserCore(
            device_id=device_id,
            tenant_id=tenant_id,
            product_id=product_id
        )
        db.add(db_user_core)
        db.commit()
        db.refresh(db_user_core)

        db_user_profile = user_model.UserProfile(
            user_id=db_user_core.user_id,
            tenant_id=tenant_id
        )
        db.add(db_user_profile)
        db.commit()
        db.refresh(db_user_profile)
    else:
        # 更新最后登录时间
        db_user_core.last_login_time = datetime.utcnow()
        db.commit()

    db_user_profile = db.query(user_model.UserProfile).filter(
        user_model.UserProfile.user_id == db_user_core.user_id
    ).first()

    # 清理用户缓存
    cache.clear_user_cache(db_user_core.user_id, tenant_id)

    # 用户已存在或刚刚被创建（登录）
    access_token = create_access_token(data={
        "sub": db_user_core.user_id,
        "tenant_id": tenant_id,
        "product_id": product_id
    })

    return user_model.UserLoginResponse(
        token=access_token,
        user_id=db_user_core.user_id,
        nickname=db_user_profile.nickname,
    )

def get_user_interests(db: Session, user_id: str):
    return db.query(user_model.UserInterests).filter(user_model.UserInterests.user_id == user_id).first()

def create_or_update_user_interests(db: Session, user_id: str, interests_data: user_model.UserInterestsCreate):
    db_interests = db.query(user_model.UserInterests).filter(user_model.UserInterests.user_id == user_id).first()
    if db_interests:
        for key, value in interests_data.model_dump(exclude_unset=True).items():
            setattr(db_interests, key, value)
        db_interests.collected_at = datetime.utcnow()
    else:
        db_interests = user_model.UserInterests(user_id=user_id, **interests_data.model_dump())
    db.add(db_interests)
    db.commit()
    db.refresh(db_interests)
    return db_interests

def record_app_usage(db: Session, user_id: str, app_usage_data: user_model.UserAppUsageCreate):
    db_app_usage = user_model.UserAppUsage(user_id=user_id, **app_usage_data.model_dump())
    db.add(db_app_usage)
    db.commit()
    db.refresh(db_app_usage)
    return db_app_usage






