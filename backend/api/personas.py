"""
人格管理API
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from beanie import PydanticObjectId

from backend.core.deps import get_current_user
from backend.models.user import User
from backend.models.persona import Persona
from backend.models.message import Message
from backend.models.chat_model import Chat
from backend.schemas.persona import PersonaResponse

router = APIRouter()


@router.get("/", response_model=List[PersonaResponse])
async def list_personas(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 20
):
    """获取用户的所有人格"""
    personas = await Persona.find(
        {"user_id": current_user.id}
    ).skip(skip).limit(limit).to_list()
    return personas


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: str,
    current_user: User = Depends(get_current_user)
):
    """获取单个人格详情"""
    persona = await Persona.get(PydanticObjectId(persona_id))
    
    if not persona:
        raise HTTPException(status_code=404, detail="人格不存在")
    
    # 验证权限
    if persona.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问")
    
    return persona


@router.patch("/{persona_id}")
async def update_persona(
    persona_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_user)
):
    """更新人格信息"""
    persona = await Persona.get(PydanticObjectId(persona_id))
    
    if not persona:
        raise HTTPException(status_code=404, detail="人格不存在")
    
    # 验证权限
    if persona.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    
    # 更新字段
    for key, value in update_data.items():
        if hasattr(persona, key):
            setattr(persona, key, value)
    
    await persona.save()
    return persona


@router.delete("/{persona_id}")
async def delete_persona(
    persona_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除人格"""
    persona = await Persona.get(PydanticObjectId(persona_id))
    
    if not persona:
        raise HTTPException(status_code=404, detail="人格不存在")
    
    # 验证权限
    if persona.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作")
    
    # 删除相关数据
    # 删除消息
    await Message.find({"persona_id": persona.id}).delete()
    
    # 删除对话
    await Chat.find({"persona_id": persona.id}).delete()
    
    # 删除人格
    await persona.delete()
    
    return {"message": "删除成功"}