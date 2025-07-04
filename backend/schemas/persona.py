"""
人格相关Schema
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, List
from bson import ObjectId
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
    id: str
    user_id: str
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
    
    @field_validator('id', 'user_id', mode='before')
    def convert_objectid(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return v
    
    class Config:
        from_attributes = True