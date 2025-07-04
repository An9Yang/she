"""
人格服务
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.models.persona import Persona
from backend.schemas.persona import PersonaUpdate


class PersonaService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_personas(self, user_id: UUID) -> List[Persona]:
        """获取用户的所有人格"""
        stmt = select(Persona).where(
            Persona.user_id == user_id
        ).order_by(Persona.created_at.desc())
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def get_persona(self, persona_id: UUID, user_id: UUID) -> Optional[Persona]:
        """获取单个人格"""
        stmt = select(Persona).where(
            Persona.id == persona_id,
            Persona.user_id == user_id
        )
        
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def update_persona(
        self,
        persona_id: UUID,
        user_id: UUID,
        update_data: PersonaUpdate
    ) -> Optional[Persona]:
        """更新人格信息"""
        persona = await self.get_persona(persona_id, user_id)
        if not persona:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(persona, field, value)
        
        await self.db.commit()
        await self.db.refresh(persona)
        return persona
    
    async def delete_persona(self, persona_id: UUID, user_id: UUID) -> bool:
        """删除人格"""
        persona = await self.get_persona(persona_id, user_id)
        if not persona:
            return False
        
        await self.db.delete(persona)
        await self.db.commit()
        return True