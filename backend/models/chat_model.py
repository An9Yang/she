"""
对话会话模型
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from beanie import Document, Indexed, PydanticObjectId


class ChatMessage(BaseModel):
    """聊天消息"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class Chat(Document):
    """对话会话文档模型"""
    
    # 关联
    user_id: Indexed(PydanticObjectId)
    persona_id: Indexed(PydanticObjectId)
    
    # 会话信息
    title: str
    messages: List[ChatMessage] = Field(default_factory=list)
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Settings:
        name = "chats"
        
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "507f1f77bcf86cd799439011",
                "persona_id": "507f1f77bcf86cd799439012",
                "title": "与小明的对话",
                "messages": [
                    {
                        "role": "user",
                        "content": "你好！",
                        "timestamp": "2024-01-01T10:00:00"
                    },
                    {
                        "role": "assistant",
                        "content": "你好！很高兴见到你！",
                        "timestamp": "2024-01-01T10:00:05"
                    }
                ]
            }
        }