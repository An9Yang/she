#!/usr/bin/env python3
"""
创建测试用户脚本
"""

import asyncio
import sys
from pathlib import Path

# 添加backend到Python路径
sys.path.append(str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_user():
    """直接创建测试用户"""
    try:
        # 连接MongoDB Atlas
        mongodb_url = "mongodb+srv://ay2494:Yang0102@cluster0.f2bzcr.mongodb.net/second_self?retryWrites=true&w=majority&appName=Cluster0"
        client = AsyncIOMotorClient(mongodb_url)
        db = client.second_self
        
        # 检查连接
        await client.admin.command('ping')
        logger.info("✅ MongoDB连接成功")
        
        # 创建用户
        test_user = {
            "email": "y794847929@gmail.com",
            "username": "y794847929",
            "hashed_password": pwd_context.hash("123456"),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # 检查用户是否存在
        existing = await db.users.find_one({"email": test_user["email"]})
        if existing:
            logger.info(f"⚠️  用户已存在: {test_user['email']}")
            logger.info("🔑 登录信息：")
            logger.info(f"   邮箱: y794847929@gmail.com")
            logger.info(f"   密码: 123456")
        else:
            # 插入用户
            result = await db.users.insert_one(test_user)
            logger.info(f"✅ 创建用户成功: {test_user['email']}")
            logger.info("🔑 登录信息：")
            logger.info(f"   邮箱: y794847929@gmail.com")
            logger.info(f"   密码: 123456")
        
        # 关闭连接
        client.close()
        
    except Exception as e:
        logger.error(f"❌ 错误: {str(e)}")
        logger.info("\n💡 请确保：")
        logger.info("1. MongoDB已安装并运行")
        logger.info("2. 如果没有MongoDB，可以使用Docker快速启动：")
        logger.info("   docker run -d -p 27017:27017 --name mongodb mongo:latest")

if __name__ == "__main__":
    asyncio.run(create_test_user())