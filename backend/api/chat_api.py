"""
聊天对话API - MongoDB版本
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from beanie import PydanticObjectId
from backend.core.deps import get_current_user
from backend.models.user import User
from backend.services.chat_service import ChatService

router = APIRouter()


class CreateChatRequest(BaseModel):
    persona_id: str
    title: Optional[str] = None


class SendMessageRequest(BaseModel):
    content: str


@router.get("/")
async def list_chats(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """获取用户的对话列表"""
    chat_service = ChatService()
    chats = await chat_service.get_user_chats(
        user_id=str(current_user.id),
        skip=skip,
        limit=limit
    )
    return chats


@router.post("/")
async def create_chat(
    data: CreateChatRequest,
    current_user: User = Depends(get_current_user)
):
    """创建新对话"""
    chat_service = ChatService()
    chat = await chat_service.create_chat(
        user_id=str(current_user.id),
        persona_id=data.persona_id,
        title=data.title
    )
    return chat


@router.get("/{chat_id}")
async def get_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取对话详情"""
    chat_service = ChatService()
    chat = await chat_service.get_chat(chat_id)
    
    if not chat:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 验证权限
    if str(chat.user_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="无权访问")
    
    return chat


@router.post("/{chat_id}/messages")
async def send_message(
    chat_id: str,
    data: SendMessageRequest,
    current_user: User = Depends(get_current_user)
):
    """发送消息"""
    chat_service = ChatService()
    
    # 验证权限
    chat = await chat_service.get_chat(chat_id)
    if not chat or str(chat.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="对话不存在")
    
    try:
        result = await chat_service.send_message(
            chat_id=chat_id,
            content=data.content,
            generate_response=True
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{chat_id}/messages/{message_index}/regenerate")
async def regenerate_message(
    chat_id: str,
    message_index: int,
    current_user: User = Depends(get_current_user)
):
    """重新生成消息"""
    chat_service = ChatService()
    
    # 验证权限
    chat = await chat_service.get_chat(chat_id)
    if not chat or str(chat.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="对话不存在")
    
    try:
        message = await chat_service.regenerate_response(
            chat_id=chat_id,
            message_index=message_index
        )
        return message
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{chat_id}")
async def delete_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除对话"""
    chat_service = ChatService()
    
    # 验证权限
    chat = await chat_service.get_chat(chat_id)
    if not chat or str(chat.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="对话不存在")
    
    success = await chat_service.delete_chat(chat_id)
    if success:
        return {"message": "删除成功"}
    else:
        raise HTTPException(status_code=500, detail="删除失败")


@router.get("/{chat_id}/export")
async def export_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user)
):
    """导出对话"""
    chat_service = ChatService()
    
    # 验证权限
    chat = await chat_service.get_chat(chat_id)
    if not chat or str(chat.user_id) != str(current_user.id):
        raise HTTPException(status_code=404, detail="对话不存在")
    
    try:
        export_data = await chat_service.export_chat(chat_id)
        return export_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))