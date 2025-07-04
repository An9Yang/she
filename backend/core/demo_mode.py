"""
演示模式 - 无需数据库的快速体验
"""

from datetime import datetime
from typing import Dict, List, Optional
from backend.models.user import User
from backend.models.persona import Persona
from backend.models.message import Message

# 模拟数据存储
demo_users: Dict[str, User] = {}
demo_personas: Dict[str, List[Persona]] = {}
demo_messages: Dict[str, List[Message]] = {}

# 演示账号
DEMO_USER = User(
    id="demo-user-001",
    email="demo@example.com",
    name="演示用户",
    hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN4LCmdusKPzfltkFJNC",  # password: demo123
    is_active=True,
    created_at=datetime.utcnow(),
    updated_at=datetime.utcnow()
)

# 演示人格
DEMO_PERSONAS = [
    Persona(
        id="persona-001",
        user_id="demo-user-001",
        name="小雨",
        avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=rain",
        description="温柔体贴的朋友，总是能理解你的心情",
        traits=["温柔", "体贴", "善解人意", "幽默"],
        speaking_style="语气温和，喜欢用可爱的表情，经常鼓励别人",
        message_count=142,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_chat_at=datetime.utcnow()
    ),
    Persona(
        id="persona-002", 
        user_id="demo-user-001",
        name="阳阳",
        avatar="https://api.dicebear.com/7.x/avataaars/svg?seed=sunny",
        description="充满活力的同学，总能带来快乐",
        traits=["活泼", "开朗", "积极", "爱开玩笑"],
        speaking_style="语气活泼，喜欢用流行语，充满正能量",
        message_count=89,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_chat_at=datetime.utcnow()
    )
]

# 初始化演示数据
demo_users[DEMO_USER.email] = DEMO_USER
demo_personas[DEMO_USER.id] = DEMO_PERSONAS

class DemoMode:
    """演示模式管理器"""
    
    @staticmethod
    def is_demo_user(email: str) -> bool:
        """检查是否是演示用户"""
        return email == "demo@example.com"
    
    @staticmethod
    def get_demo_user() -> User:
        """获取演示用户"""
        return DEMO_USER
    
    @staticmethod
    def get_demo_personas() -> List[Persona]:
        """获取演示人格列表"""
        return DEMO_PERSONAS
    
    @staticmethod
    def get_demo_persona(persona_id: str) -> Optional[Persona]:
        """获取指定演示人格"""
        for persona in DEMO_PERSONAS:
            if persona.id == persona_id:
                return persona
        return None