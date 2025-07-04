"""
聊天服务 - 核心RAG实现
"""

from typing import List, Optional, AsyncGenerator
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.models.persona import Persona
from backend.models.message import Message
from backend.rag_engine.hybrid_rag import HybridRAG
from backend.core.config import settings


class ChatService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.rag = HybridRAG()
    
    async def verify_persona_ownership(self, persona_id: UUID, user_id: UUID) -> bool:
        """验证用户是否拥有该人格"""
        stmt = select(Persona).where(
            Persona.id == persona_id,
            Persona.user_id == user_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    async def generate_response(
        self,
        persona_id: UUID,
        user_message: str,
        context: Optional[List[str]] = None
    ) -> str:
        """生成人格回复"""
        # 获取人格信息
        stmt = select(Persona).where(Persona.id == persona_id)
        result = await self.db.execute(stmt)
        persona = result.scalar_one_or_none()
        
        if not persona:
            raise ValueError("Persona not found")
        
        # 使用Hybrid RAG检索相关消息
        relevant_messages = await self.rag.retrieve(
            query=user_message,
            persona_id=str(persona_id),
            context=context
        )
        
        # 生成回复
        response = await self.rag.generate_response(
            user_message=user_message,
            relevant_messages=relevant_messages,
            persona_features=persona.style_features,
            persona_name=persona.name
        )
        
        # 保存对话记录
        await self._save_conversation(persona_id, user_message, response)
        
        return response
    
    async def generate_response_stream(
        self,
        persona_id: UUID,
        user_message: str,
        context: Optional[List[str]] = None
    ) -> AsyncGenerator[str, None]:
        """流式生成回复"""
        # 获取人格信息
        stmt = select(Persona).where(Persona.id == persona_id)
        result = await self.db.execute(stmt)
        persona = result.scalar_one_or_none()
        
        if not persona:
            raise ValueError("Persona not found")
        
        # 使用Hybrid RAG检索相关消息
        relevant_messages = await self.rag.retrieve(
            query=user_message,
            persona_id=str(persona_id),
            context=context
        )
        
        # 流式生成回复
        full_response = ""
        async for chunk in self.rag.generate_response_stream(
            user_message=user_message,
            relevant_messages=relevant_messages,
            persona_features=persona.style_features,
            persona_name=persona.name
        ):
            full_response += chunk
            yield chunk
        
        # 保存完整对话记录
        await self._save_conversation(persona_id, user_message, full_response)
    
    async def get_chat_history(
        self,
        persona_id: UUID,
        limit: int = 50,
        offset: int = 0
    ) -> List[Message]:
        """获取聊天历史"""
        stmt = select(Message).where(
            Message.persona_id == persona_id,
            Message.is_original == False  # 只获取对话消息，不包括原始导入的
        ).order_by(
            Message.timestamp.desc()
        ).limit(limit).offset(offset)
        
        result = await self.db.execute(stmt)
        return result.scalars().all()
    
    async def _save_conversation(
        self,
        persona_id: UUID,
        user_message: str,
        ai_response: str
    ):
        """保存对话记录"""
        # 保存用户消息
        user_msg = Message(
            persona_id=persona_id,
            content=user_message,
            sender="user",
            is_original=False
        )
        self.db.add(user_msg)
        
        # 保存AI回复
        ai_msg = Message(
            persona_id=persona_id,
            content=ai_response,
            sender="persona",
            is_original=False
        )
        self.db.add(ai_msg)
        
        await self.db.commit()