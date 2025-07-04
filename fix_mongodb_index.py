#!/usr/bin/env python3
"""
修复MongoDB索引冲突问题
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
        
        # 2. 查找问题记录
        print("\n🔍 查找username为null的记录...")
        null_users = await db.users.count_documents({"username": None})
        print(f"  找到 {null_users} 个username为null的用户")
        
        if null_users > 0:
            # 3. 修复null记录
            print("\n🔧 修复null记录...")
            cursor = db.users.find({"username": None})
            count = 0
            async for user in cursor:
                # 使用email前缀作为username
                email = user.get('email', '')
                if email:
                    new_username = email.split('@')[0] + f"_{count}"
                    await db.users.update_one(
                        {"_id": user["_id"]},
                        {"$set": {"username": new_username}}
                    )
                    print(f"  ✅ 更新用户 {email} 的username为: {new_username}")
                    count += 1
        
        # 4. 删除并重建索引（可选）
        print("\n❓ 是否重建索引？(y/n): ", end='')
        if input().lower() == 'y':
            print("🔧 删除旧索引...")
            try:
                await db.users.drop_index("username_1")
                print("  ✅ 已删除username索引")
            except:
                print("  ⚠️  索引不存在或删除失败")
            
            print("🔧 创建新索引（带sparse选项）...")
            await db.users.create_index(
                "username",
                unique=True,
                sparse=True  # 允许null值，但非null值必须唯一
            )
            print("  ✅ 索引创建成功")
        
        # 5. 验证修复
        print("\n✅ 修复完成！验证结果：")
        null_count = await db.users.count_documents({"username": None})
        total_count = await db.users.count_documents({})
        print(f"  - 总用户数: {total_count}")
        print(f"  - username为null的用户数: {null_count}")
        
        # 关闭连接
        client.close()
        
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        print("\n💡 可能的解决方案：")
        print("1. 检查MongoDB连接字符串")
        print("2. 确认数据库权限")
        print("3. 手动在MongoDB Atlas控制台操作")

if __name__ == "__main__":
    print("=== MongoDB索引修复工具 ===\n")
    asyncio.run(fix_mongodb_index())