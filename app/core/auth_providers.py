"""
认证提供商模块 - 支持多种第三方认证方式
支持中国大陆（微信、QQ、手机号）和海外（Google、邮箱）认证
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pydantic import BaseModel
import httpx
from datetime import datetime

class AuthUserInfo(BaseModel):
    """统一的认证用户信息格式"""
    provider_user_id: str  # 第三方平台的用户ID
    provider: str          # 认证提供商 (wechat/qq/google/phone/email)
    email: Optional[str] = None
    phone: Optional[str] = None
    nickname: Optional[str] = None
    avatar_url: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None  # 原始数据


class BaseAuthProvider(ABC):
    """认证提供商基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthUserInfo:
        """认证用户并返回用户信息"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """获取提供商名称"""
        pass


class WeChatAuthProvider(BaseAuthProvider):
    """微信登录提供商"""
    
    def get_provider_name(self) -> str:
        return "wechat"
    
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthUserInfo:
        """
        微信认证流程
        credentials: {"code": "微信授权码"}
        """
        code = credentials.get("code")
        if not code:
            raise ValueError("WeChat auth code is required")
        
        # 1. 通过code获取access_token
        token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        token_params = {
            "appid": self.config["app_id"],
            "secret": self.config["app_secret"],
            "code": code,
            "grant_type": "authorization_code"
        }
        
        async with httpx.AsyncClient() as client:
            token_response = await client.get(token_url, params=token_params)
            token_data = token_response.json()
            
            if "errcode" in token_data:
                raise ValueError(f"WeChat auth error: {token_data}")
            
            access_token = token_data["access_token"]
            openid = token_data["openid"]
            
            # 2. 获取用户信息
            userinfo_url = "https://api.weixin.qq.com/sns/userinfo"
            userinfo_params = {
                "access_token": access_token,
                "openid": openid,
                "lang": "zh_CN"
            }
            
            userinfo_response = await client.get(userinfo_url, params=userinfo_params)
            userinfo_data = userinfo_response.json()
            
            if "errcode" in userinfo_data:
                raise ValueError(f"WeChat userinfo error: {userinfo_data}")
            
            return AuthUserInfo(
                provider_user_id=openid,
                provider="wechat",
                nickname=userinfo_data.get("nickname"),
                avatar_url=userinfo_data.get("headimgurl"),
                raw_data=userinfo_data
            )


class QQAuthProvider(BaseAuthProvider):
    """QQ登录提供商"""
    
    def get_provider_name(self) -> str:
        return "qq"
    
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthUserInfo:
        """
        QQ认证流程
        credentials: {"access_token": "QQ访问令牌"}
        """
        access_token = credentials.get("access_token")
        if not access_token:
            raise ValueError("QQ access token is required")
        
        async with httpx.AsyncClient() as client:
            # 1. 获取OpenID
            openid_url = "https://graph.qq.com/oauth2.0/me"
            openid_params = {"access_token": access_token}
            
            openid_response = await client.get(openid_url, params=openid_params)
            openid_text = openid_response.text
            
            # 解析JSONP格式响应
            if "callback" in openid_text:
                import json
                json_str = openid_text.split("(")[1].split(")")[0]
                openid_data = json.loads(json_str)
                openid = openid_data["openid"]
            else:
                raise ValueError("Failed to get QQ OpenID")
            
            # 2. 获取用户信息
            userinfo_url = "https://graph.qq.com/user/get_user_info"
            userinfo_params = {
                "access_token": access_token,
                "oauth_consumer_key": self.config["app_id"],
                "openid": openid
            }
            
            userinfo_response = await client.get(userinfo_url, params=userinfo_params)
            userinfo_data = userinfo_response.json()
            
            if userinfo_data.get("ret") != 0:
                raise ValueError(f"QQ userinfo error: {userinfo_data}")
            
            return AuthUserInfo(
                provider_user_id=openid,
                provider="qq",
                nickname=userinfo_data.get("nickname"),
                avatar_url=userinfo_data.get("figureurl_qq_1"),
                raw_data=userinfo_data
            )


class GoogleAuthProvider(BaseAuthProvider):
    """Google OAuth认证提供商"""
    
    def get_provider_name(self) -> str:
        return "google"
    
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthUserInfo:
        """
        Google认证流程
        credentials: {"id_token": "Google ID Token"}
        """
        id_token = credentials.get("id_token")
        if not id_token:
            raise ValueError("Google ID token is required")
        
        # 验证Google ID Token
        verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(verify_url)
            user_data = response.json()
            
            if response.status_code != 200 or "error" in user_data:
                raise ValueError(f"Google token verification failed: {user_data}")
            
            # 验证audience
            if user_data.get("aud") != self.config["client_id"]:
                raise ValueError("Invalid Google client ID")
            
            return AuthUserInfo(
                provider_user_id=user_data["sub"],
                provider="google",
                email=user_data.get("email"),
                nickname=user_data.get("name"),
                avatar_url=user_data.get("picture"),
                raw_data=user_data
            )


class PhoneAuthProvider(BaseAuthProvider):
    """手机号认证提供商"""
    
    def get_provider_name(self) -> str:
        return "phone"
    
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthUserInfo:
        """
        手机号认证流程
        credentials: {"phone": "手机号", "code": "验证码"}
        """
        phone = credentials.get("phone")
        code = credentials.get("code")
        
        if not phone or not code:
            raise ValueError("Phone and verification code are required")
        
        # TODO: 实际项目中需要：
        # 1. 验证码存储在Redis中
        # 2. 验证手机号格式
        # 3. 验证码防刷机制
        # 4. 集成短信服务商（阿里云、腾讯云等）
        
        # 简化验证逻辑（实际应从Redis验证）
        if code != "123456":  # 临时验证码
            raise ValueError("Invalid verification code")
        
        return AuthUserInfo(
            provider_user_id=phone,
            provider="phone",
            phone=phone,
            nickname=f"用户{phone[-4:]}"  # 手机号后4位作为昵称
        )


class EmailAuthProvider(BaseAuthProvider):
    """邮箱认证提供商"""
    
    def get_provider_name(self) -> str:
        return "email"
    
    async def authenticate(self, credentials: Dict[str, Any]) -> AuthUserInfo:
        """
        邮箱认证流程 - 极简版本
        """
        return AuthUserInfo(
            provider_user_id="test@example.com",
            provider="email",
            email="test@example.com",
            nickname="test"
        )


class AuthProviderFactory:
    """认证提供商工厂类"""
    
    _providers = {
        "wechat": WeChatAuthProvider,
        "qq": QQAuthProvider,
        "google": GoogleAuthProvider,
        "phone": PhoneAuthProvider,
        "email": EmailAuthProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str, config: Dict[str, Any]) -> BaseAuthProvider:
        """创建认证提供商实例"""
        if provider_name not in cls._providers:
            raise ValueError(f"Unsupported auth provider: {provider_name}")
        
        provider_class = cls._providers[provider_name]
        return provider_class(config)
    
    @classmethod
    def get_supported_providers(cls) -> list:
        """获取支持的认证提供商列表"""
        return list(cls._providers.keys())


from .auth_config import get_auth_providers_config

# 获取认证提供商配置
AUTH_PROVIDERS_CONFIG = get_auth_providers_config()
