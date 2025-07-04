#!/usr/bin/env python3
"""
自动修复MongoDB索引冲突问题
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys
from pathlib import Path

# 添加backend到Python路径
sys.path.append(str(Path(__file__).parent))

async def fix_mongodb_index():
    """修复MongoDB索引问题"""
    # MongoDB连接
    mongodb_url = "mongodb+srv://ay2494:Yang0102@cluster0.f2bzcr.mongodb.net/second_self?retryWrites=true&w=majority&appName=Cluster0"
    
    try:
        # 连接数据库
        client = AsyncIOMotorClient(mongodb_url)
        db = client.second_self
        
        print("🔍 检查MongoDB连接...")
        await client.admin.command('ping')
        print("✅ MongoDB连接成功")
        
        # 1. 检查当前索引
        print("\n📋 当前索引：")
        indexes = await db.users.list_indexes().to_list(None)
        for idx in indexes:
            print(f"  - {idx['name']}: {idx.get('key', {})}")
        
        # 2. 检查是否已有username索引
        has_username_index = any(idx['name'] == 'username_1' for idx in indexes)
        
        if not has_username_index:
            print("\n✅ 没有username索引，可以直接使用main.py启动！")
            client.close()
            return
        
        # 3. 如果有索引，检查null值
        print("\n🔍 查找username为null的记录...")
        null_users = await db.users.count_documents({"username": None})
        print(f"  找到 {null_users} 个username为null的用户")
        
        # 4. 删除username索引
        print("\n🔧 删除username索引以解决冲突...")
        try:
            await db.users.drop_index("username_1")
            print("  ✅ 已删除username索引")
            
            # 5. 创建sparse索引（允许null但要求非null唯一）
            print("\n🔧 创建新的sparse索引...")
            await db.users.create_index(
                "username",
                unique=True,
                sparse=True
            )
            print("  ✅ 新索引创建成功（允许null值）")
            
        except Exception as e:
            print(f"  ❌ 索引操作失败: {str(e)}")
        
        # 6. 验证结果
        print("\n📊 最终状态：")
        indexes = await db.users.list_indexes().to_list(None)
        for idx in indexes:
            if 'username' in str(idx.get('key', {})):
                print(f"  - {idx['name']}: {idx.get('key', {})} (sparse: {idx.get('sparse', False)})")
        
        print("\n✅ 修复完成！现在可以使用main.py正常启动了")
        
        # 关闭连接
        client.close()
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")

if __name__ == "__main__":
    print("=== MongoDB索引自动修复工具 ===\n")
    asyncio.run(fix_mongodb_index())