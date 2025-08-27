"""
多种认证方式的服务层实现
支持中国大陆和海外不同的认证提供商
"""

from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from ..models import user as user_model
from ..core.security import create_access_token
from ..core.cache import get_cache
from ..core.auth_providers import AuthProviderFactory, AUTH_PROVIDERS_CONFIG, AuthUserInfo
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """统一认证服务"""
    
    def __init__(self):
        # 延迟初始化缓存，避免循环导入问题
        self._cache = None
    
    @property
    def cache(self):
        if self._cache is None:
            self._cache = get_cache()
        return self._cache
    
    async def authenticate_user(
        self, 
        db: Session, 
        provider: str, 
        credentials: Dict[str, Any], 
        tenant_id: str = "default",
        product_id: Optional[str] = None,
        region: str = "global"
    ) -> user_model.UserLoginResponse:
        """
        统一认证入口
        
        Args:
            db: 数据库会话
            provider: 认证提供商 (wechat/qq/google/phone/email)
            credentials: 认证凭据
            tenant_id: 租户ID
            product_id: 产品ID
            region: 地区 (china/global)
        
        Returns:
            UserLoginResponse: 包含JWT token和用户信息
        """
        try:
            # 1. 获取认证提供商配置
            provider_config = self._get_provider_config(provider, region)
            
            # 2. 创建认证提供商实例并进行认证
            auth_provider = AuthProviderFactory.create_provider(provider, provider_config)
            auth_user_info = await auth_provider.authenticate(credentials)
            
            # 3. 查找或创建用户
            user = self._find_or_create_user(
                db, auth_user_info, tenant_id, product_id
            )
            
            # 4. 生成JWT token
            access_token = create_access_token(data={
                "sub": user.user_id,
                "tenant_id": tenant_id,
                "product_id": product_id,
                "provider": provider
            })
            
            # 5. 获取用户资料
            user_profile = db.query(user_model.UserProfile).filter(
                user_model.UserProfile.user_id == user.user_id
            ).first()
            
            # 6. 清理用户缓存
            self.cache.clear_user_cache(user.user_id, tenant_id)
            
            return user_model.UserLoginResponse(
                token=access_token,
                user_id=user.user_id,
                nickname=user_profile.nickname if user_profile else auth_user_info.nickname or "新用户"
            )
            
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            raise ValueError(f"认证失败: {str(e)}")
    
    def _get_provider_config(self, provider: str, region: str) -> Dict[str, Any]:
        """获取认证提供商配置"""
        # 根据地区选择不同的配置
        if region == "china":
            # 中国大陆特定配置
            china_config = AUTH_PROVIDERS_CONFIG.get(f"{provider}_china", 
                                                   AUTH_PROVIDERS_CONFIG.get(provider))
            if china_config:
                return china_config
        
        # 全球配置
        return AUTH_PROVIDERS_CONFIG.get(provider, {})
    
    def _find_or_create_user(
        self, 
        db: Session, 
        auth_info: AuthUserInfo, 
        tenant_id: str, 
        product_id: Optional[str]
    ) -> user_model.UserCore:
        """查找或创建用户"""
        
        # 1. 尝试通过第三方用户ID查找
        existing_user = db.query(user_model.UserCore).filter(
            user_model.UserCore.provider_user_id == auth_info.provider_user_id,
            user_model.UserCore.register_channel == auth_info.provider,
            user_model.UserCore.tenant_id == tenant_id
        ).first()
        
        if existing_user:
            # 更新最后登录时间
            existing_user.last_login_time = datetime.utcnow()
            db.commit()
            return existing_user
        
        # 2. 尝试通过邮箱或手机号查找（如果提供）
        if auth_info.email:
            existing_user = db.query(user_model.UserCore).filter(
                user_model.UserCore.email == auth_info.email,
                user_model.UserCore.tenant_id == tenant_id
            ).first()
            
            if existing_user:
                # 绑定第三方账号
                existing_user.provider_user_id = auth_info.provider_user_id
                existing_user.provider_data = auth_info.raw_data
                existing_user.last_login_time = datetime.utcnow()
                db.commit()
                return existing_user
        
        if auth_info.phone:
            existing_user = db.query(user_model.UserCore).filter(
                user_model.UserCore.phone == auth_info.phone,
                user_model.UserCore.tenant_id == tenant_id
            ).first()
            
            if existing_user:
                # 绑定第三方账号
                existing_user.provider_user_id = auth_info.provider_user_id
                existing_user.provider_data = auth_info.raw_data
                existing_user.last_login_time = datetime.utcnow()
                db.commit()
                return existing_user
        
        # 3. 创建新用户
        new_user = user_model.UserCore(
            tenant_id=tenant_id,
            product_id=product_id,
            email=auth_info.email,
            phone=auth_info.phone,
            register_channel=user_model.RegisterChannel(auth_info.provider),
            provider_user_id=auth_info.provider_user_id,
            provider_data=auth_info.raw_data
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # 4. 创建用户资料
        user_profile = user_model.UserProfile(
            user_id=new_user.user_id,
            tenant_id=tenant_id,
            nickname=auth_info.nickname or "新用户",
            avatar_url=auth_info.avatar_url
        )
        
        db.add(user_profile)
        db.commit()
        
        return new_user
    
    def get_supported_providers(self, region: str = "global") -> Dict[str, Any]:
        """获取支持的认证提供商列表"""
        all_providers = AuthProviderFactory.get_supported_providers()
        
        if region == "china":
            # 中国大陆推荐的认证方式
            china_providers = {
                "wechat": {
                    "name": "微信登录",
                    "icon": "wechat",
                    "priority": 1
                },
                "qq": {
                    "name": "QQ登录", 
                    "icon": "qq",
                    "priority": 2
                },
                "phone": {
                    "name": "手机号登录",
                    "icon": "phone",
                    "priority": 3
                }
            }
            return china_providers
        else:
            # 海外推荐的认证方式
            global_providers = {
                "google": {
                    "name": "Google Sign-In",
                    "icon": "google", 
                    "priority": 1
                },
                "email": {
                    "name": "Email Login",
                    "icon": "email",
                    "priority": 2
                },
                "apple": {
                    "name": "Sign in with Apple",
                    "icon": "apple",
                    "priority": 3
                }
            }
            return global_providers


# 创建全局认证服务实例
auth_service = AuthService()


def get_auth_service() -> AuthService:
    """获取认证服务实例"""
    return auth_service
