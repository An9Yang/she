"""
用户模型 - MongoDB版本
"""

from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field
from beanie import Document, Indexed


class User(Document):
    """用户文档模型"""
    
    # 基本信息
    email: Indexed(EmailStr, unique=True)
    username: Indexed(str, unique=True)
    hashed_password: str
    
    # 状态
    is_active: bool = True
    is_superuser: bool = False
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # 用户配置
    settings: Optional[dict] = None
    
    class Settings:
        name = "users"
        
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "username": "john_doe",
                "is_active": True
            }
        }