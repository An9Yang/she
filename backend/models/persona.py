"""
人格模型 - MongoDB版本
"""

from datetime import datetime
from typing import Optional, List, Dict
from pydantic import Field
from beanie import Document, Indexed, PydanticObjectId
from enum import Enum


class PersonaStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class Persona(Document):
    """人格文档模型"""
    
    # 关联
    user_id: Indexed(PydanticObjectId)
    
    # 基本信息
    name: str
    avatar_url: Optional[str] = None
    source_platform: Optional[str] = None  # wechat, whatsapp等
    status: PersonaStatus = PersonaStatus.PROCESSING
    
    # 统计信息
    message_count: int = 0
    date_range_start: Optional[datetime] = None
    date_range_end: Optional[datetime] = None
    
    # 人格特征 - MongoDB的灵活Schema优势
    style_features: Optional[Dict] = Field(default_factory=dict)
    emoji_profile: Optional[Dict] = Field(default_factory=dict)
    topic_preferences: Optional[List[str]] = Field(default_factory=list)
    personality_summary: Optional[str] = None
    
    # 语言模式
    frequent_words: Optional[List[str]] = Field(default_factory=list)
    sentence_patterns: Optional[Dict] = Field(default_factory=dict)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "personas"
        indexes = [
            "user_id",
            "status",
            "created_at"
        ]