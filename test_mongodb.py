"""
测试MongoDB Atlas连接
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")

async def test_mongodb_connection():
    """测试MongoDB Atlas连接"""
    print("🔍 测试MongoDB Atlas连接...\n")
    
    # 获取连接字符串
    mongodb_url = os.getenv("MONGODB_URL")
    database_name = os.getenv("DATABASE_NAME", "second_self")
    
    print(f"📍 连接URL: {mongodb_url.replace('Yang0102', '****')}")  # 隐藏密码
    print(f"📊 数据库名: {database_name}\n")
    
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from beanie import init_beanie, Document
        from pydantic import Field
        
        # 创建测试模型
        class TestDocument(Document):
            name: str
            created_at: datetime = Field(default_factory=datetime.now)
            
            class Settings:
                name = "test_collection"
        
        # 连接数据库
        print("⏳ 正在连接...")
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        
        # 初始化Beanie
        await init_beanie(database=db, document_models=[TestDocument])
        print("✅ 连接成功！")
        
        # 测试写入
        print("\n📝 测试写入数据...")
        test_doc = TestDocument(name="测试文档")
        await test_doc.save()
        print(f"✅ 写入成功，文档ID: {test_doc.id}")
        
        # 测试读取
        print("\n📖 测试读取数据...")
        found_doc = await TestDocument.find_one({"name": "测试文档"})
        if found_doc:
            print(f"✅ 读取成功: {found_doc.name} (创建时间: {found_doc.created_at})")
        
        # 清理测试数据
        print("\n🧹 清理测试数据...")
        await test_doc.delete()
        print("✅ 清理完成")
        
        # 列出集合
        print("\n📋 数据库集合列表:")
        collections = await db.list_collection_names()
        for col in collections:
            print(f"  - {col}")
        
        print("\n✨ MongoDB Atlas连接测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n可能的原因：")
        print("1. 网络连接问题")
        print("2. IP白名单未配置（需要在Atlas中添加你的IP）")
        print("3. 用户名或密码错误")
        print("4. 集群未启动")
        return False


async def test_project_models():
    """测试项目数据模型"""
    print("\n\n🧪 测试项目数据模型...\n")
    
    try:
        from backend.core.database import init_db, close_db
        from backend.models.user import User
        from backend.models.persona import Persona
        from backend.models.message import Message
        
        # 初始化数据库
        await init_db()
        print("✅ 数据库初始化成功")
        
        # 测试用户模型
        print("\n1️⃣ 测试用户模型...")
        test_user = User(
            email="test@example.com",
            name="测试用户",
            hashed_password="hashed_password_here"
        )
        # 注意：这里只是创建对象，不实际保存到数据库
        print(f"✅ 用户模型创建成功: {test_user.email}")
        
        # 测试人格模型
        print("\n2️⃣ 测试人格模型...")
        from beanie import PydanticObjectId
        test_persona = Persona(
            user_id=PydanticObjectId(),
            name="测试人格",
            message_count=0,
            status="ready"
        )
        print(f"✅ 人格模型创建成功: {test_persona.name}")
        
        # 关闭数据库连接
        await close_db()
        print("\n✅ 所有模型测试通过！")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型测试失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Second Self - MongoDB Atlas 连接测试")
    print("=" * 60)
    
    # 运行测试
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 测试基础连接
    connection_ok = loop.run_until_complete(test_mongodb_connection())
    
    # 如果连接成功，测试项目模型
    if connection_ok:
        loop.run_until_complete(test_project_models())
    
    print("\n" + "=" * 60)
    
    if connection_ok:
        print("\n✅ 数据库配置成功！现在可以启动项目了。")
        print("\n启动命令：")
        print("1. 后端: cd backend && python -m uvicorn main:app --reload")
        print("2. 前端: cd frontend && npm run dev")