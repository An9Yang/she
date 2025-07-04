#!/usr/bin/env python3
"""
完整项目测试脚本
"""

import asyncio
import sys
import os
import json
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

# 测试结果
test_results = {
    "backend": {"status": "pending", "errors": []},
    "frontend": {"status": "pending", "errors": []},
    "integration": {"status": "pending", "errors": []},
}


async def test_imports():
    """测试所有必要的导入"""
    print("🔍 测试Python导入...")
    
    try:
        # 测试基础导入
        import fastapi
        import motor
        import beanie
        from jose import jwt
        from passlib.hash import bcrypt
        print("✅ 基础包导入成功")
        
        # 测试后端模块
        from backend.core.config import settings
        from backend.models.user import User
        from backend.models.persona import Persona
        from backend.models.message import Message
        from backend.models.chat import Chat
        print("✅ 后端模型导入成功")
        
        # 测试服务
        from backend.services.data_processor import DataProcessorService
        from backend.services.rag_service import RAGService
        from backend.services.chat_service import ChatService
        print("✅ 服务模块导入成功")
        
        return True
    except ImportError as e:
        print(f"❌ 导入错误: {e}")
        test_results["backend"]["errors"].append(str(e))
        return False


async def test_config():
    """测试配置文件"""
    print("\n📋 检查配置...")
    
    try:
        from backend.core.config import settings
        
        # 检查必要配置
        required_configs = [
            "MONGODB_URL",
            "SECRET_KEY",
            "ALGORITHM",
            "ACCESS_TOKEN_EXPIRE_MINUTES"
        ]
        
        missing = []
        for config in required_configs:
            if not hasattr(settings, config):
                missing.append(config)
        
        if missing:
            print(f"❌ 缺少配置: {', '.join(missing)}")
            test_results["backend"]["errors"].append(f"Missing configs: {missing}")
            return False
        
        print("✅ 配置检查通过")
        return True
    except Exception as e:
        print(f"❌ 配置错误: {e}")
        test_results["backend"]["errors"].append(str(e))
        return False


async def test_mongodb_connection():
    """测试MongoDB连接"""
    print("\n🗄️ 测试MongoDB连接...")
    
    try:
        from backend.core.database import init_db, close_db
        
        # 测试连接
        await init_db()
        print("✅ MongoDB连接成功")
        
        # 关闭连接
        await close_db()
        return True
    except Exception as e:
        print(f"❌ MongoDB连接失败: {e}")
        test_results["backend"]["errors"].append(f"MongoDB: {e}")
        return False


async def test_auth_service():
    """测试认证服务"""
    print("\n🔐 测试认证服务...")
    
    try:
        from backend.services.auth import AuthService
        from backend.schemas.user import UserCreate
        
        auth_service = AuthService()
        
        # 测试密码哈希
        hashed = auth_service.get_password_hash("testpassword")
        verified = auth_service.verify_password("testpassword", hashed)
        
        if not verified:
            raise Exception("密码验证失败")
        
        print("✅ 认证服务正常")
        return True
    except Exception as e:
        print(f"❌ 认证服务错误: {e}")
        test_results["backend"]["errors"].append(f"Auth: {e}")
        return False


async def test_data_processor():
    """测试数据处理器"""
    print("\n📄 测试数据处理器...")
    
    try:
        from backend.services.data_processor import DataProcessorService
        
        processor = DataProcessorService()
        
        # 测试编码检测
        test_file = "test_file.txt"
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("测试内容")
        
        encoding = processor._detect_encoding(test_file)
        os.remove(test_file)
        
        print(f"✅ 编码检测: {encoding}")
        
        # 测试时间解析
        test_times = ["2024/1/1, 10:30:45", "2024-01-01 10:30:45"]
        for t in test_times:
            parsed = processor._parse_timestamp(t)
            print(f"✅ 时间解析: {t} -> {parsed}")
        
        return True
    except Exception as e:
        print(f"❌ 数据处理器错误: {e}")
        test_results["backend"]["errors"].append(f"DataProcessor: {e}")
        return False


async def test_frontend_structure():
    """测试前端结构"""
    print("\n🎨 检查前端文件...")
    
    frontend_files = [
        "frontend/package.json",
        "frontend/src/app/page.tsx",
        "frontend/src/app/layout.tsx",
        "frontend/src/components/ChatInterface.tsx",
        "frontend/src/components/PersonaCard.tsx",
        "frontend/src/components/FileUpload.tsx",
        "frontend/src/services/api.ts",
    ]
    
    missing_files = []
    for file in frontend_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少前端文件: {missing_files}")
        test_results["frontend"]["errors"].append(f"Missing files: {missing_files}")
        return False
    
    print("✅ 前端文件结构完整")
    return True


async def test_api_endpoints():
    """测试API端点定义"""
    print("\n🔌 检查API端点...")
    
    try:
        from backend.main import app
        
        routes = []
        for route in app.routes:
            if hasattr(route, "path"):
                routes.append(f"{route.methods} {route.path}")
        
        required_endpoints = [
            "/api/auth/register",
            "/api/auth/token",
            "/api/personas",
            "/api/chat",
            "/api/upload"
        ]
        
        missing = []
        for endpoint in required_endpoints:
            found = any(endpoint in str(route) for route in routes)
            if not found:
                missing.append(endpoint)
        
        if missing:
            print(f"❌ 缺少端点: {missing}")
            test_results["integration"]["errors"].append(f"Missing endpoints: {missing}")
            return False
        
        print(f"✅ 找到 {len(routes)} 个API端点")
        return True
    except Exception as e:
        print(f"❌ API检查错误: {e}")
        test_results["integration"]["errors"].append(f"API: {e}")
        return False


async def create_test_env_files():
    """创建测试用的环境文件"""
    print("\n🔧 创建测试环境文件...")
    
    # 后端 .env
    backend_env = """# MongoDB
MONGODB_URL=mongodb://localhost:27017/second_self_test
DATABASE_NAME=second_self_test

# Security
SECRET_KEY=test-secret-key-please-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Azure OpenAI
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=your-api-key
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-35-turbo
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

# CORS
CORS_ORIGINS=["http://localhost:3000"]
"""
    
    # 前端 .env.local
    frontend_env = """NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_NAME=Second Self
"""
    
    try:
        # 创建后端环境文件
        if not os.path.exists("backend/.env"):
            with open("backend/.env", "w") as f:
                f.write(backend_env)
            print("✅ 创建 backend/.env")
        
        # 创建前端环境文件
        if not os.path.exists("frontend/.env.local"):
            with open("frontend/.env.local", "w") as f:
                f.write(frontend_env)
            print("✅ 创建 frontend/.env.local")
        
        return True
    except Exception as e:
        print(f"❌ 创建环境文件失败: {e}")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("🚀 开始完整项目测试\n")
    
    # 创建环境文件
    await create_test_env_files()
    
    # 后端测试
    print("=== 后端测试 ===")
    backend_ok = True
    
    if not await test_imports():
        backend_ok = False
    
    if not await test_config():
        backend_ok = False
    
    if not await test_auth_service():
        backend_ok = False
    
    if not await test_data_processor():
        backend_ok = False
    
    if not await test_api_endpoints():
        backend_ok = False
    
    # MongoDB连接测试（可选）
    # if not await test_mongodb_connection():
    #     backend_ok = False
    
    test_results["backend"]["status"] = "passed" if backend_ok else "failed"
    
    # 前端测试
    print("\n=== 前端测试 ===")
    frontend_ok = await test_frontend_structure()
    test_results["frontend"]["status"] = "passed" if frontend_ok else "failed"
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果总结\n")
    
    all_passed = True
    for component, result in test_results.items():
        status_icon = "✅" if result["status"] == "passed" else "❌"
        print(f"{status_icon} {component}: {result['status']}")
        if result["errors"]:
            for error in result["errors"]:
                print(f"   - {error}")
        if result["status"] != "passed":
            all_passed = False
    
    print("\n" + "="*50)
    
    if all_passed:
        print("\n🎉 所有测试通过！项目可以运行。\n")
        print("启动命令：")
        print("1. 后端: cd backend && python -m uvicorn main:app --reload")
        print("2. 前端: cd frontend && npm install && npm run dev")
    else:
        print("\n⚠️ 有些测试失败，需要修复以下问题：")
        
        # 提供修复建议
        if test_results["backend"]["errors"]:
            print("\n后端修复建议：")
            for error in test_results["backend"]["errors"]:
                if "No module named" in error:
                    print(f"- 安装缺失的包: pip install {error.split()[-1]}")
                elif "MongoDB" in error:
                    print("- 确保MongoDB正在运行: brew services start mongodb-community")
                elif "Missing configs" in error:
                    print("- 检查并更新 backend/.env 文件")
        
        if test_results["frontend"]["errors"]:
            print("\n前端修复建议：")
            print("- 运行: cd frontend && npm install")
    
    return all_passed


if __name__ == "__main__":
    asyncio.run(run_all_tests())