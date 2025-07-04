"""
MongoDB数据库配置
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from backend.core.config import settings
from backend.models.user import User
from backend.models.persona import Persona
from backend.models.message import Message
from backend.models.chat import ChatHistory
from backend.models.chat_model import Chat

# MongoDB客户端
motor_client = None
database = None


async def init_db():
    """初始化MongoDB连接"""
    global motor_client, database
    
    # 创建MongoDB客户端
    motor_client = AsyncIOMotorClient(settings.MONGODB_URL)
    database = motor_client[settings.DATABASE_NAME]
    
    # 初始化Beanie ODM
    await init_beanie(
        database=database,
        document_models=[
            User,
            Persona,
            Message,
            ChatHistory,
            Chat
        ]
    )
    
    # 创建索引
    await create_indexes()


async def create_indexes():
    """创建必要的索引"""
    # 用户邮箱唯一索引
    await User.get_motor_collection().create_index("email", unique=True)
    await User.get_motor_collection().create_index("username", unique=True)
    
    # 人格索引
    await Persona.get_motor_collection().create_index("user_id")
    
    # 消息索引 - 支持向量搜索
    await Message.get_motor_collection().create_index("persona_id")
    await Message.get_motor_collection().create_index("timestamp")
    
    # 如果使用MongoDB Atlas，可以创建向量搜索索引
    # 这需要在Atlas UI中配置或使用特定API


async def close_db():
    """关闭数据库连接"""
    global motor_client
    if motor_client:
        motor_client.close()