"""
认证提供商配置管理
支持环境变量配置和默认配置
"""

import os
from typing import Dict, Any
from .config import settings

def get_auth_providers_config() -> Dict[str, Any]:
    """获取认证提供商配置"""
    
    return {
        # 微信登录配置
        "wechat": {
            "app_id": os.getenv("WECHAT_APP_ID", "your_wechat_app_id"),
            "app_secret": os.getenv("WECHAT_APP_SECRET", "your_wechat_app_secret"),
            "redirect_uri": os.getenv("WECHAT_REDIRECT_URI", "https://your-domain.com/auth/wechat/callback")
        },
        
        # QQ登录配置
        "qq": {
            "app_id": os.getenv("QQ_APP_ID", "your_qq_app_id"),
            "app_secret": os.getenv("QQ_APP_SECRET", "your_qq_app_secret"),
            "redirect_uri": os.getenv("QQ_REDIRECT_URI", "https://your-domain.com/auth/qq/callback")
        },
        
        # Google OAuth配置
        "google": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", "your_google_client_id"),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", "your_google_client_secret"),
            "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "https://your-domain.com/auth/google/callback")
        },
        
        # 手机号验证配置
        "phone": {
            "sms_provider": os.getenv("SMS_PROVIDER", "aliyun"),  # aliyun, tencent, etc.
            "access_key": os.getenv("SMS_ACCESS_KEY", "your_sms_access_key"),
            "access_secret": os.getenv("SMS_ACCESS_SECRET", "your_sms_access_secret"),
            "sign_name": os.getenv("SMS_SIGN_NAME", "your_app_name"),
            "template_code": os.getenv("SMS_TEMPLATE_CODE", "SMS_123456")
        },
        
        # 邮箱认证配置
        "email": {
            "password_salt": os.getenv("PASSWORD_SALT", "your_password_salt_here"),
            "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
            "smtp_port": int(os.getenv("SMTP_PORT", "587")),
            "smtp_user": os.getenv("SMTP_USER", "your_email@gmail.com"),
            "smtp_password": os.getenv("SMTP_PASSWORD", "your_email_password")
        },
        
        # Apple Sign-In配置（可选）
        "apple": {
            "client_id": os.getenv("APPLE_CLIENT_ID", "your_apple_client_id"),
            "team_id": os.getenv("APPLE_TEAM_ID", "your_apple_team_id"),
            "key_id": os.getenv("APPLE_KEY_ID", "your_apple_key_id"),
            "private_key": os.getenv("APPLE_PRIVATE_KEY", "your_apple_private_key")
        }
    }

# 中国大陆专用配置（如果需要不同的配置）
def get_china_auth_config() -> Dict[str, Any]:
    """获取中国大陆专用认证配置"""
    base_config = get_auth_providers_config()
    
    # 可以为中国大陆配置不同的API端点
    china_config = base_config.copy()
    
    # 微信登录在中国大陆可能使用不同的API端点
    if "wechat_china" in os.environ:
        china_config["wechat"].update({
            "api_base": "https://api.weixin.qq.com"  # 中国大陆API
        })
    
    return china_config
