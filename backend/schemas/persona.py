"""
人格相关Schema
"""

from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, List
from backend.models.persona import PersonaStatus


class PersonaBase(BaseModel):
    name: str
    avatar_url: Optional[str] = None


class PersonaCreate(PersonaBase):
    source_platform: Optional[str] = None


class PersonaUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class PersonaResponse(PersonaBase):
    id: UUID
    user_id: UUID
    status: PersonaStatus
    source_platform: Optional[str]
    message_count: int
    date_range_start: Optional[datetime]
    date_range_end: Optional[datetime]
    style_features: Optional[Dict]
    emoji_profile: Optional[Dict]
    topic_preferences: Optional[List[str]]
    personality_summary: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True