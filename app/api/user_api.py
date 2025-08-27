from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..services import user_service
from ..services.auth_service import get_auth_service
from ..models import user as user_model
from ..core.database import get_db
from ..core.security import get_current_user

router = APIRouter()

@router.post("/login", response_model=user_model.UserLoginResponse)
def login_or_register(request: user_model.UserLoginRequest, db: Session = Depends(get_db)):
    """
    根据设备ID处理用户登录或注册（支持租户隔离）

    - 如果设备ID是新的，则会创建一个新用户。
    - 如果设备ID已存在，则返回现有用户的数据。
    - 无论哪种情况，都会签发一个新的 JWT 令牌。
    - 支持多租户和产品隔离
    """
    try:
        response = user_service.login_or_register_user(
            db=db, 
            device_id=request.device_id,
            tenant_id=request.tenant_id,
            product_id=request.product_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/auth", response_model=user_model.UserLoginResponse)
async def auth_login(request: user_model.AuthLoginRequest, db: Session = Depends(get_db)):
    """
    多种认证方式的统一登录接口
    
    支持的认证方式：
    - 中国大陆：微信、QQ、手机号
    - 海外：Google、邮箱、Apple（待实现）
    """
    try:
        auth_service = get_auth_service()
        response = await auth_service.authenticate_user(
            db=db,
            provider=request.provider,
            credentials=request.credentials,
            tenant_id=request.tenant_id,
            product_id=request.product_id,
            region=request.region
        )
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/auth/providers")
async def get_auth_providers(region: str = "global"):
    """
    获取支持的认证提供商列表
    
    Args:
        region: 地区 (china/global)
    
    Returns:
        支持的认证方式列表
    """
    try:
        auth_service = get_auth_service()
        providers = auth_service.get_supported_providers(region=region)
        return {
            "region": region,
            "providers": providers
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify", response_model=user_model.UserCoreResponse)
def verify_token(current_user: user_model.UserCore = Depends(get_current_user)):
    return current_user

@router.get("/profile", response_model=user_model.UserProfileResponse)
def get_user_profile(current_user: user_model.UserCore = Depends(get_current_user), db: Session = Depends(get_db)):
    user_profile = db.query(user_model.UserProfile).filter(user_model.UserProfile.user_id == current_user.user_id).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return user_profile

@router.put("/profile", response_model=user_model.UserProfileResponse)
def update_user_profile(profile_data: user_model.UserProfileResponse, current_user: user_model.UserCore = Depends(get_current_user), db: Session = Depends(get_db)):
    user_profile = db.query(user_model.UserProfile).filter(user_model.UserProfile.user_id == current_user.user_id).first()
    if not user_profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    
    for key, value in profile_data.model_dump(exclude_unset=True).items():
        if key == "user_id":
            continue
        setattr(user_profile, key, value)
    
    db.commit()
    db.refresh(user_profile)
    return user_profile

@router.post("/interests", response_model=user_model.UserInterestsResponse)
def create_or_update_interests(interests_data: user_model.UserInterestsCreate, current_user: user_model.UserCore = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    创建或更新用户的兴趣画像。
    """
    try:
        interests = user_service.create_or_update_user_interests(db=db, user_id=current_user.user_id, interests_data=interests_data)
        return interests
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/interests", response_model=user_model.UserInterestsResponse)
def get_interests(current_user: user_model.UserCore = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    获取用户的兴趣画像。
    """
    interests = user_service.get_user_interests(db=db, user_id=current_user.user_id)
    if not interests:
        raise HTTPException(status_code=404, detail="User interests not found")
    return interests

@router.post("/app_usage", response_model=user_model.UserAppUsageResponse)
def record_app_usage(app_usage_data: user_model.UserAppUsageCreate, current_user: user_model.UserCore = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    记录用户的App使用会话。
    """
    try:
        app_usage = user_service.record_app_usage(db=db, user_id=current_user.user_id, app_usage_data=app_usage_data)
        return app_usage
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
