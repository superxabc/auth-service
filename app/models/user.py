import uuid
from datetime import datetime, date
from sqlalchemy import Column, String, DateTime, Integer, Float, Enum as SQLAlchemyEnum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
import enum
from typing import List, Optional
from sqlalchemy.dialects.postgresql import JSONB # For tags JSON

Base = declarative_base()

class RegisterChannel(str, enum.Enum):
    DEVICE_ID = "device_id"  # 保留原有的设备ID注册方式
    PHONE = "phone"
    WECHAT = "wechat"
    QQ = "qq"
    GOOGLE = "google"
    EMAIL = "email"
    APPLE = "apple"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    FROZEN = "frozen"
    DELETED = "deleted"

class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    PREFER_NOT_SAY = "prefer_not_say"

# SQLAlchemy 的 'user_core' 表模型
class UserCore(Base):
    __tablename__ = "user_core"

    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String, nullable=False, default="default", index=True)  # 租户隔离
    product_id = Column(String, nullable=True, index=True)  # 产品标识
    phone = Column(String, index=True, nullable=True)
    email = Column(String, index=True, nullable=True)
    password_hash = Column(String, nullable=True)
    register_channel = Column(SQLAlchemyEnum(RegisterChannel), nullable=False, default=RegisterChannel.DEVICE_ID)
    provider_user_id = Column(String, nullable=True, index=True)  # 第三方平台用户ID
    provider_data = Column(JSONB, nullable=True)  # 第三方平台原始数据
    register_time = Column(DateTime, default=datetime.utcnow)
    last_login_time = Column(DateTime, default=datetime.utcnow)
    status = Column(SQLAlchemyEnum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    device_id = Column(String, nullable=True, index=True)  # 改为可选，支持第三方登录
    
    __table_args__ = (
        # 确保同一租户内的phone/email/device_id唯一
        {'mysql_engine': 'InnoDB'}
    )

# SQLAlchemy 的 'user_profile' 表模型
class UserProfile(Base):
    __tablename__ = "user_profile"

    user_id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False, default="default", index=True)  # 租户隔离
    nickname = Column(String, nullable=False, default="新朋友")
    avatar_url = Column(String, nullable=True)
    gender = Column(SQLAlchemyEnum(Gender), default=Gender.PREFER_NOT_SAY)
    birth_year = Column(Integer, nullable=True)
    region = Column(String, nullable=True)
    language_preference = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# 通用化枚举定义
class InterestCategory(str, enum.Enum):
    EDUCATION = "education"        # 教育学习类
    PRODUCTIVITY = "productivity"  # 效率工具类
    ENTERTAINMENT = "entertainment"  # 娱乐休闲类
    SOCIAL = "social"             # 社交类
    BUSINESS = "business"         # 商务类
    HEALTH = "health"             # 健康类
    LIFESTYLE = "lifestyle"       # 生活方式类
    TECHNOLOGY = "technology"     # 科技类
    CUSTOM = "custom"             # 自定义类
    OTHER = "other"               # 其他

class ContentFormat(str, enum.Enum):
    BRIEF = "brief"               # 简洁
    DETAILED = "detailed"         # 详细
    INTERACTIVE = "interactive"   # 交互式
    STRUCTURED = "structured"     # 结构化
    CONVERSATIONAL = "conversational"  # 对话式

class DeviceType(str, enum.Enum):
    IOS = "iOS"
    ANDROID = "Android"
    WEB = "Web"



# SQLAlchemy 的 'user_interests' 表模型 - 通用化改造
class UserInterests(Base):
    __tablename__ = "user_interests"

    user_id = Column(String, ForeignKey("user_core.user_id"), primary_key=True)
    tenant_id = Column(String, nullable=False, default="default", index=True)  # 租户隔离
    primary_category = Column(SQLAlchemyEnum(InterestCategory), nullable=True)
    interest_data = Column(JSONB, nullable=True)  # 灵活的兴趣数据结构
    preferred_format = Column(SQLAlchemyEnum(ContentFormat), nullable=True)
    schema_version = Column(String, default="1.0")  # 支持schema版本演进
    collected_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# SQLAlchemy 的 'user_app_usage' 表模型
class UserAppUsage(Base):
    __tablename__ = "user_app_usage"

    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("user_core.user_id"), nullable=False)
    tenant_id = Column(String, nullable=False, default="default", index=True)  # 租户隔离
    device_type = Column(SQLAlchemyEnum(DeviceType), nullable=False)
    app_version = Column(String, nullable=True)
    session_start_time = Column(DateTime, default=datetime.utcnow)
    session_end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)





# 用于 API 交互的 Pydantic 模型 (Schemas)
class UserLoginRequest(BaseModel):
    device_id: str = Field(..., description="设备唯一标识")
    tenant_id: str = Field(default="default", description="租户标识")
    product_id: Optional[str] = Field(None, description="产品标识")

class AuthLoginRequest(BaseModel):
    """多种认证方式的登录请求"""
    provider: str = Field(..., description="认证提供商：wechat/qq/google/phone/email")
    credentials: dict = Field(..., description="认证凭据")
    tenant_id: str = Field(default="default", description="租户标识")
    product_id: Optional[str] = Field(None, description="产品标识")
    region: Optional[str] = Field(default="global", description="地区：china/global")

class UserLoginResponse(BaseModel):
    token: str
    user_id: str
    nickname: str

class TokenData(BaseModel):
    user_id: str | None = None

class UserCoreResponse(BaseModel):
    user_id: str
    tenant_id: str
    product_id: str | None
    phone: str | None
    email: str | None
    register_channel: RegisterChannel
    status: UserStatus
    device_id: str

    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    user_id: str
    nickname: str
    avatar_url: str | None
    gender: Gender | None
    birth_year: int | None
    region: str | None
    language_preference: str | None

    class Config:
        from_attributes = True

# Pydantic Models for User Interests - 通用化
class UserInterestsCreate(BaseModel):
    primary_category: Optional[InterestCategory] = None
    interest_data: Optional[dict] = None  # 灵活的JSON数据结构
    preferred_format: Optional[ContentFormat] = None
    schema_version: Optional[str] = Field(default="1.0")

class UserInterestsResponse(UserInterestsCreate):
    user_id: str
    collected_at: datetime

    class Config:
        from_attributes = True

# Pydantic Models for User App Usage
class UserAppUsageCreate(BaseModel):
    device_type: DeviceType
    app_version: Optional[str] = None
    session_start_time: Optional[datetime] = None
    session_end_time: Optional[datetime] = None
    duration_seconds: Optional[int] = None

class UserAppUsageResponse(UserAppUsageCreate):
    session_id: str
    user_id: str

    class Config:
        from_attributes = True








