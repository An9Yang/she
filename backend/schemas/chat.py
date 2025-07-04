"""
聊天相关Schema
"""

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import List, Optional


class ChatMessage(BaseModel):
    content: str
    context: Optional[List[str]] = None


class ChatResponse(BaseModel):
    content: str
    persona_id: UUID
    timestamp: datetime = datetime.utcnow()


class MessageHistory(BaseModel):
    id: UUID
    content: str
    sender: str  # 'user' or 'persona'
    timestamp: datetime
    
    class Config:
        from_attributes = True