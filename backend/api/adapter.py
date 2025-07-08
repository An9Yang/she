"""
API路径适配器 - 提供兼容性路径
"""

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
import httpx

router = APIRouter()

# 登录路径适配
@router.post("/api/auth/login")
async def login_adapter(request: Request):
    """将/api/auth/login重定向到/api/auth/token"""
    body = await request.json()
    
    # 转换为OAuth2格式
    form_data = {
        "username": body.get("email", body.get("username", "")),
        "password": body.get("password", ""),
        "grant_type": "password"
    }
    
    # 调用真实的token端点
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/auth/token",
            data=form_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )

# 上传路径适配（处理末尾斜杠）
@router.post("/api/upload")
async def upload_adapter(request: Request):
    """处理不带斜杠的上传路径"""
    # 获取原始body
    body = await request.body()
    headers = dict(request.headers)
    
    # 转发到正确的路径
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/upload/",
            content=body,
            headers=headers
        )
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

# 人格路径适配
@router.get("/api/personas")
async def personas_list_adapter(request: Request):
    """处理人格列表路径"""
    headers = dict(request.headers)
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/personas/",
            headers=headers
        )
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )

@router.post("/api/personas")
async def personas_create_adapter(request: Request):
    """处理人格创建路径"""
    body = await request.json()
    headers = dict(request.headers)
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/personas/",
            json=body,
            headers=headers
        )
        
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers)
        )
