"""
聊天对话API
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import json

from backend.core.database import get_db
from backend.services.auth import get_current_user
from backend.models.user import User
from backend.schemas.chat import ChatMessage, ChatResponse
from backend.services.chat import ChatService

router = APIRouter()


@router.post("/{persona_id}/message")
async def send_message(
    persona_id: UUID,
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """发送消息并获取回复"""
    chat_service = ChatService(db)
    
    # 验证用户是否拥有该人格
    if not await chat_service.verify_persona_ownership(persona_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # 生成回复
    response = await chat_service.generate_response(
        persona_id=persona_id,
        user_message=message.content,
        context=message.context
    )
    
    return ChatResponse(
        content=response,
        persona_id=persona_id,
        timestamp=response.timestamp
    )


@router.post("/{persona_id}/message/stream")
async def send_message_stream(
    persona_id: UUID,
    message: ChatMessage,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """发送消息并流式获取回复"""
    chat_service = ChatService(db)
    
    # 验证用户是否拥有该人格
    if not await chat_service.verify_persona_ownership(persona_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    async def generate():
        async for chunk in chat_service.generate_response_stream(
            persona_id=persona_id,
            user_message=message.content,
            context=message.context
        ):
            yield f"data: {json.dumps({'content': chunk})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )


@router.get("/{persona_id}/history")
async def get_chat_history(
    persona_id: UUID,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取聊天历史"""
    chat_service = ChatService(db)
    
    # 验证用户是否拥有该人格
    if not await chat_service.verify_persona_ownership(persona_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    messages = await chat_service.get_chat_history(
        persona_id=persona_id,
        limit=limit,
        offset=offset
    )
    
    return {"messages": messages, "total": len(messages)}