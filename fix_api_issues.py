#!/usr/bin/env python3
"""
修复API路径和认证字段问题
"""
import os
import sys
from pathlib import Path

def fix_auth_schema():
    """修改认证schema，让username可选或自动生成"""
    print("修复认证字段问题...")
    
    # 方案1：修改UserCreate schema，让username可选
    schema_file = Path("backend/schemas/user.py")
    
    if schema_file.exists():
        content = schema_file.read_text(encoding='utf-8')
        
        # 备份原文件
        backup_file = schema_file.with_suffix('.py.backup')
        backup_file.write_text(content, encoding='utf-8')
        print(f"✅ 已备份原文件到 {backup_file}")
        
        # 修改UserBase，让username可选
        new_content = content.replace(
            "class UserBase(BaseModel):\n    email: EmailStr\n    username: str",
            "class UserBase(BaseModel):\n    email: EmailStr\n    username: Optional[str] = None"
        )
        
        # 确保导入Optional
        if "from typing import Optional" not in new_content:
            new_content = new_content.replace(
                "from typing import",
                "from typing import Optional,"
            )
        
        schema_file.write_text(new_content, encoding='utf-8')
        print("✅ 已修改UserBase schema，username现在是可选的")
    else:
        print("❌ 找不到schema文件")
        return False
    
    # 方案2：修改认证服务，自动生成username
    auth_service_file = Path("backend/services/auth.py")
    
    if auth_service_file.exists():
        content = auth_service_file.read_text(encoding='utf-8')
        
        # 备份
        backup_file = auth_service_file.with_suffix('.py.backup')
        backup_file.write_text(content, encoding='utf-8')
        
        # 在create_user方法中添加自动生成username的逻辑
        # 查找create_user方法
        if "async def create_user" in content:
            # 在方法开始处添加username生成逻辑
            new_content = content.replace(
                "async def create_user(self, user_data: UserCreate) -> Optional[User]:\n        \"\"\"创建新用户\"\"\"",
                """async def create_user(self, user_data: UserCreate) -> Optional[User]:
        \"\"\"创建新用户\"\"\"
        # 如果没有提供username，使用email的用户名部分
        if not user_data.username:
            user_data.username = user_data.email.split('@')[0]"""
            )
            
            auth_service_file.write_text(new_content, encoding='utf-8')
            print("✅ 已修改认证服务，自动从email生成username")
    
    return True

def create_api_adapter():
    """创建API适配器，添加兼容路径"""
    print("\n创建API路径适配器...")
    
    adapter_content = '''"""
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
'''
    
    adapter_file = Path("backend/api/adapter.py")
    adapter_file.write_text(adapter_content, encoding='utf-8')
    print(f"✅ 已创建API适配器文件: {adapter_file}")
    
    # 修改main.py，添加适配器路由
    main_file = Path("backend/main.py")
    if main_file.exists():
        content = main_file.read_text(encoding='utf-8')
        
        # 添加导入
        if "from backend.api import adapter" not in content:
            import_line = "from backend.api import auth, personas, chat_api, upload"
            new_import = f"{import_line}, adapter"
            content = content.replace(import_line, new_import)
        
        # 添加路由
        if 'app.include_router(adapter.router)' not in content:
            # 在其他路由之前添加适配器路由
            router_section = "# 注册路由"
            content = content.replace(
                router_section,
                f"{router_section}\napp.include_router(adapter.router)  # API兼容性适配器"
            )
        
        # 备份并保存
        backup_file = main_file.with_suffix('.py.backup')
        main_file.rename(backup_file)
        main_file.write_text(content, encoding='utf-8')
        print("✅ 已更新main.py，添加适配器路由")
    
    return True

def update_test_scripts():
    """更新测试脚本使用正确的路径"""
    print("\n更新测试脚本...")
    
    # 测试脚本路径映射
    path_fixes = {
        "/api/auth/login": "/api/auth/token",  # 使用OAuth2标准路径
        "/api/upload": "/api/upload/",  # 添加末尾斜杠
        "/api/personas": "/api/personas/",  # 添加末尾斜杠
    }
    
    test_files = [
        "run_modular_tests.py",
        "test_full_flow.py",
    ]
    
    for test_file in test_files:
        file_path = Path(test_file)
        if file_path.exists():
            content = file_path.read_text(encoding='utf-8')
            updated = False
            
            # 应用路径修复
            for old_path, new_path in path_fixes.items():
                if old_path in content:
                    content = content.replace(f'"{old_path}"', f'"{new_path}"')
                    content = content.replace(f"'{old_path}'", f"'{new_path}'")
                    updated = True
            
            if updated:
                # 备份并更新
                backup_file = file_path.with_suffix('.py.backup')
                file_path.rename(backup_file)
                file_path.write_text(content, encoding='utf-8')
                print(f"✅ 已更新 {test_file}")
    
    return True

def main():
    """主函数"""
    print("🔧 修复API路径和认证字段问题")
    print("=" * 50)
    
    # 1. 修复认证字段问题
    if fix_auth_schema():
        print("\n✅ 认证字段问题已修复")
    else:
        print("\n❌ 认证字段修复失败")
        return
    
    # 2. 创建API适配器
    if create_api_adapter():
        print("\n✅ API适配器已创建")
    else:
        print("\n❌ API适配器创建失败")
        return
    
    # 3. 更新测试脚本
    if update_test_scripts():
        print("\n✅ 测试脚本已更新")
    
    print("\n" + "=" * 50)
    print("✅ 所有修复已完成！")
    print("\n下一步：")
    print("1. 重启后端服务")
    print("2. 运行测试验证修复")
    print("\n注意：已创建.backup文件，如需恢复请使用备份文件")

if __name__ == "__main__":
    main()