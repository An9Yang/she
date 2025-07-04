"""
聊天历史模型 - 用户与AI的对话记录
"""

from datetime import datetime
from typing import Optional
from pydantic import Field
from beanie import Document, Indexed, PydanticObjectId


class ChatHistory(Document):
    """聊天历史文档模型"""
    
    # 关联
    user_id: Indexed(PydanticObjectId)
    persona_id: Indexed(PydanticObjectId)
    
    # 对话内容
    user_message: str
    ai_response: str
    
    # 会话信息
    session_id: Optional[str] = None
    
    # 时间戳
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # 反馈
    rating: Optional[int] = None  # 1-5星评价
    feedback: Optional[str] = None
    
    class Settings:
        name = "chat_history"
        indexes = [
            "user_id",
            "persona_id",
            "timestamp",
            "session_id"
        ]