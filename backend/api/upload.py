"""
文件上传API - 简化版
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import aiofiles
import os
from uuid import uuid4
import asyncio

from backend.core.deps import get_current_user
from backend.models.user import User
from backend.core.config import settings
from backend.services.data_processor import DataProcessorService

router = APIRouter()


@router.post("/")
async def upload_chat_data(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """上传聊天记录文件"""
    
    # 检查文件大小 (100MB)
    MAX_SIZE = 100 * 1024 * 1024
    if file.size and file.size > MAX_SIZE:
        raise HTTPException(
            status_code=400,
            detail="文件大小不能超过100MB"
        )
    
    # 检查文件类型
    allowed_extensions = ['.zip', '.db', '.txt', '.json', '.html']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型 {file_ext}"
        )
    
    # 保存文件
    file_id = str(uuid4())
    upload_dir = "uploads"
    file_path = os.path.join(upload_dir, f"{file_id}{file_ext}")
    
    # 确保目录存在
    os.makedirs(upload_dir, exist_ok=True)
    
    # 异步写入文件
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    # 创建处理任务（使用asyncio而不是Celery）
    task_id = str(uuid4())
    
    # 在后台处理文件
    processor = DataProcessorService()
    asyncio.create_task(
        processor.process_chat_data(
            file_path=file_path,
            user_id=str(current_user.id),
            task_id=task_id
        )
    )
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "文件上传成功，正在处理中..."
    }


# 简单的任务状态存储（生产环境应使用Redis）
task_status_store = {}

@router.get("/status/{task_id}")
async def check_upload_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """检查上传任务状态"""
    # 检查任务存储中的状态
    if task_id in task_status_store:
        return task_status_store[task_id]
    
    # 如果不在存储中，尝试从数据库查找最新创建的persona
    # 这是一个临时解决方案，实际应该在处理完成时更新task_status_store
    from backend.models.persona import Persona
    
    # 查找用户最新创建的处理中或已完成的persona
    latest_persona = await Persona.find(
        {"user_id": current_user.id}
    ).sort("-created_at").limit(1).to_list()
    
    if latest_persona:
        persona = latest_persona[0]
        # 如果找到了persona，返回成功状态
        return {
            "task_id": task_id,
            "status": "completed" if persona.status == "ready" else "processing",
            "persona_id": str(persona.id),
            "message_count": persona.message_count,
            "error": None
        }
    
    # 默认返回处理中状态
    return {
        "task_id": task_id,
        "status": "processing",
        "progress": 50,
        "message": "正在分析聊天记录..."
    }