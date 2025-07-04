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
    # 模拟任务完成
    if task_id not in task_status_store:
        # 模拟一个成功的任务
        return {
            "task_id": task_id,
            "status": "completed",
            "persona_id": "507f1f77bcf86cd799439011",
            "message_count": 100,
            "error": None
        }
    
    return task_status_store.get(task_id, {
        "task_id": task_id,
        "status": "processing",
        "progress": 50,
        "message": "正在分析聊天记录..."
    })