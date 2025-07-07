"""共享的 pytest fixtures 和配置"""
import os
import sys
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from pathlib import Path

# 将项目根目录添加到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
import jwt

from backend.main import app
from backend.core.config import settings
from backend.core.database_wrapper import Database
from backend.models.user import User
from backend.models.persona import Persona
from backend.models.chat_model import Chat
from backend.models.message import Message


@pytest.fixture(scope="session")
def event_loop():
    """创建异步事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_db() -> AsyncGenerator[Database, None]:
    """测试数据库连接"""
    # 使用测试数据库
    test_db_name = f"{settings.DATABASE_NAME}_test"
    db = Database()
    db.db = AsyncIOMotorClient(settings.DATABASE_URL)[test_db_name]
    
    # 初始化集合
    await db.init_collections()
    
    yield db
    
    # 清理测试数据库
    client = AsyncIOMotorClient(settings.DATABASE_URL)
    await client.drop_database(test_db_name)


@pytest.fixture
async def clean_db(test_db: Database):
    """每个测试前清空数据库"""
    collections = await test_db.db.list_collection_names()
    for collection_name in collections:
        await test_db.db[collection_name].delete_many({})
    yield test_db


@pytest.fixture
def client() -> TestClient:
    """FastAPI 测试客户端"""
    return TestClient(app)


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """异步 HTTP 客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_user_data() -> dict:
    """测试用户数据"""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "Test123!@#"
    }


@pytest.fixture
async def test_user(clean_db: Database, test_user_data: dict) -> User:
    """创建测试用户"""
    from backend.services.auth_service import AuthService
    auth_service = AuthService(clean_db)
    user = await auth_service.register_user(**test_user_data)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """认证头部"""
    from backend.core.security import create_access_token
    token = create_access_token(data={"sub": test_user.username})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def test_persona(clean_db: Database, test_user: User) -> Persona:
    """创建测试人格"""
    from backend.services.persona_service import PersonaService
    persona_service = PersonaService(clean_db)
    
    persona_data = {
        "name": "Test Persona",
        "description": "A test persona",
        "user_id": str(test_user.id),
        "source_type": "whatsapp",
        "message_count": 100,
        "metadata": {
            "created_from": "test"
        }
    }
    
    persona = await persona_service.create_persona(**persona_data)
    return persona


@pytest.fixture
async def test_chat(clean_db: Database, test_user: User, test_persona: Persona) -> Chat:
    """创建测试聊天"""
    from backend.services.chat_service import ChatService
    chat_service = ChatService(clean_db)
    
    chat = await chat_service.create_chat(
        user_id=str(test_user.id),
        persona_id=str(test_persona.id),
        title="Test Chat"
    )
    return chat


@pytest.fixture
def mock_openai_client():
    """模拟 OpenAI 客户端"""
    mock_client = AsyncMock()
    
    # 模拟 embeddings
    mock_embeddings = AsyncMock()
    mock_embeddings.create.return_value = AsyncMock(
        data=[AsyncMock(embedding=[0.1] * 1536)]
    )
    mock_client.embeddings = mock_embeddings
    
    # 模拟 chat completions
    mock_chat = AsyncMock()
    mock_chat.completions.create.return_value = AsyncMock(
        choices=[
            AsyncMock(
                message=AsyncMock(
                    content="This is a test response",
                    role="assistant"
                )
            )
        ]
    )
    mock_client.chat = mock_chat
    
    return mock_client


@pytest.fixture
def sample_messages() -> list[dict]:
    """示例消息数据"""
    return [
        {
            "sender": "Alice",
            "content": "Hey, how are you?",
            "timestamp": datetime.now() - timedelta(days=1),
            "metadata": {"platform": "whatsapp"}
        },
        {
            "sender": "Bob",
            "content": "I'm good! Just working on some code.",
            "timestamp": datetime.now() - timedelta(hours=23),
            "metadata": {"platform": "whatsapp"}
        },
        {
            "sender": "Alice",
            "content": "That's great! What are you working on?",
            "timestamp": datetime.now() - timedelta(hours=22),
            "metadata": {"platform": "whatsapp"}
        }
    ]


@pytest.fixture
def sample_chat_file(tmp_path: Path) -> Path:
    """创建示例聊天文件"""
    chat_content = """[2025-07-01 10:00:00] Alice: Hello!
[2025-07-01 10:01:00] Bob: Hi there!
[2025-07-01 10:02:00] Alice: How's your day going?
[2025-07-01 10:03:00] Bob: Pretty good, thanks for asking!
"""
    file_path = tmp_path / "sample_chat.txt"
    file_path.write_text(chat_content)
    return file_path


@pytest.fixture
def mock_rag_service():
    """模拟 RAG 服务"""
    mock_service = AsyncMock()
    mock_service.search.return_value = [
        {
            "content": "Similar message 1",
            "score": 0.95,
            "metadata": {"sender": "Alice", "timestamp": "2025-07-01"}
        },
        {
            "content": "Similar message 2",
            "score": 0.88,
            "metadata": {"sender": "Bob", "timestamp": "2025-07-02"}
        }
    ]
    return mock_service


@pytest.fixture(autouse=True)
def reset_singletons():
    """重置单例模式的实例"""
    # 重置数据库单例
    Database._instance = None
    yield
    Database._instance = None


@pytest.fixture
def mock_env_vars(monkeypatch):
    """模拟环境变量"""
    test_env = {
        "SECRET_KEY": "test-secret-key-for-testing-only",
        "DATABASE_URL": "mongodb://localhost:27017",
        "DATABASE_NAME": "secondself_test",
        "AZURE_OPENAI_API_KEY": "test-api-key",
        "AZURE_OPENAI_ENDPOINT": "https://test.openai.azure.com",
        "AZURE_OPENAI_DEPLOYMENT": "test-deployment",
        "AZURE_OPENAI_API_VERSION": "2024-02-15-preview"
    }
    
    for key, value in test_env.items():
        monkeypatch.setenv(key, value)
    
    return test_env