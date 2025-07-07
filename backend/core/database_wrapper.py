"""
数据库包装类，用于测试和统一接口
"""
from motor.motor_asyncio import AsyncIOMotorClient
from backend.core.config import settings
from typing import Optional


class Database:
    """数据库包装类"""
    _instance: Optional['Database'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.db = self.client[settings.DATABASE_NAME]
            
            # 集合引用
            self.users = self.db.users
            self.personas = self.db.personas
            self.chats = self.db.chats
            self.messages = self.db.messages
            self.chat_messages = self.db.chat_messages
            
            self.initialized = True
    
    async def init_collections(self):
        """初始化集合（如果不存在则创建）"""
        existing_collections = await self.db.list_collection_names()
        
        collections_to_create = ['users', 'personas', 'chats', 'messages', 'chat_messages']
        
        for collection in collections_to_create:
            if collection not in existing_collections:
                await self.db.create_collection(collection)
    
    async def create_indexes(self):
        """创建索引"""
        # 用户索引
        await self.users.create_index("username", unique=True)
        await self.users.create_index("email", unique=True)
        
        # 人格索引
        await self.personas.create_index("user_id")
        
        # 消息索引
        await self.messages.create_index("persona_id")
        await self.messages.create_index([("persona_id", 1), ("timestamp", -1)])
        
        # 聊天索引
        await self.chats.create_index("user_id")
        await self.chats.create_index([("user_id", 1), ("created_at", -1)])
    
    async def create_vector_index(self):
        """创建向量搜索索引"""
        # MongoDB Atlas Vector Search需要通过Atlas UI或API创建
        # 这里只是占位符
        pass
    
    async def cleanup_old_messages(self, cutoff_date):
        """清理旧消息"""
        result = await self.chat_messages.delete_many({
            "timestamp": {"$lt": cutoff_date}
        })
        return result.deleted_count