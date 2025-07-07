"""数据库连接测试"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from motor.motor_asyncio import AsyncIOMotorClient

from backend.core.database import Database
from backend.core.config import settings


class TestDatabase:
    """数据库测试类"""
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_database_singleton(self):
        """测试数据库单例模式"""
        db1 = Database()
        db2 = Database()
        
        assert db1 is db2
        assert id(db1) == id(db2)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_database_connection(self):
        """测试数据库连接"""
        db = Database()
        
        assert db.client is not None
        assert db.db is not None
        assert isinstance(db.client, AsyncIOMotorClient)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_init_collections(self):
        """测试初始化集合"""
        db = Database()
        
        # Mock数据库和集合
        mock_db = MagicMock()
        mock_db.list_collection_names = AsyncMock(return_value=[])
        mock_db.create_collection = AsyncMock()
        db.db = mock_db
        
        await db.init_collections()
        
        # 验证创建了必要的集合
        expected_collections = ['users', 'personas', 'chats', 'messages', 'chat_messages']
        assert mock_db.create_collection.call_count == len(expected_collections)
        
        for collection in expected_collections:
            mock_db.create_collection.assert_any_call(collection)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_init_collections_already_exist(self):
        """测试集合已存在时的初始化"""
        db = Database()
        
        # Mock数据库，返回已存在的集合
        mock_db = MagicMock()
        mock_db.list_collection_names = AsyncMock(
            return_value=['users', 'personas', 'chats']
        )
        mock_db.create_collection = AsyncMock()
        db.db = mock_db
        
        await db.init_collections()
        
        # 验证只创建了不存在的集合
        assert mock_db.create_collection.call_count == 2  # messages 和 chat_messages
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_create_indexes(self):
        """测试创建索引"""
        db = Database()
        
        # Mock集合
        mock_users = MagicMock()
        mock_users.create_index = AsyncMock()
        
        mock_personas = MagicMock()
        mock_personas.create_index = AsyncMock()
        
        mock_messages = MagicMock()
        mock_messages.create_index = AsyncMock()
        
        db.users = mock_users
        db.personas = mock_personas
        db.messages = mock_messages
        
        await db.create_indexes()
        
        # 验证创建了必要的索引
        mock_users.create_index.assert_any_call("username", unique=True)
        mock_users.create_index.assert_any_call("email", unique=True)
        mock_personas.create_index.assert_any_call("user_id")
        mock_messages.create_index.assert_any_call([("persona_id", 1), ("timestamp", -1)])
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_collection_properties(self):
        """测试集合属性"""
        db = Database()
        
        # 验证所有集合属性都存在
        assert hasattr(db, 'users')
        assert hasattr(db, 'personas')
        assert hasattr(db, 'chats')
        assert hasattr(db, 'messages')
        assert hasattr(db, 'chat_messages')
        
        # 验证集合类型
        assert db.users is not None
        assert db.personas is not None
        assert db.chats is not None
        assert db.messages is not None
        assert db.chat_messages is not None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_database_name(self):
        """测试数据库名称"""
        db = Database()
        
        # 验证使用了正确的数据库名称
        assert db.db.name == settings.DATABASE_NAME
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_connection_error_handling(self):
        """测试连接错误处理"""
        # Mock连接失败
        with patch('motor.motor_asyncio.AsyncIOMotorClient') as mock_client:
            mock_client.side_effect = Exception("Connection failed")
            
            # 重置单例
            Database._instance = None
            
            with pytest.raises(Exception, match="Connection failed"):
                Database()
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_ping_database(self):
        """测试ping数据库"""
        db = Database()
        
        # Mock admin命令
        mock_admin = MagicMock()
        mock_admin.command = AsyncMock(return_value={'ok': 1})
        db.db.client.admin = mock_admin
        
        # 执行ping
        result = await db.db.client.admin.command('ping')
        
        assert result['ok'] == 1
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_vector_search_index(self):
        """测试向量搜索索引"""
        db = Database()
        
        # Mock消息集合
        mock_messages = MagicMock()
        mock_messages.create_index = AsyncMock()
        db.messages = mock_messages
        
        # 创建向量索引
        await db.create_vector_index()
        
        # 验证创建了向量索引
        mock_messages.create_index.assert_called()
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_cleanup_old_data(self):
        """测试清理旧数据"""
        db = Database()
        
        # Mock集合
        mock_chat_messages = MagicMock()
        mock_chat_messages.delete_many = AsyncMock(
            return_value=MagicMock(deleted_count=10)
        )
        db.chat_messages = mock_chat_messages
        
        # 执行清理
        from datetime import datetime, timedelta
        cutoff_date = datetime.now() - timedelta(days=30)
        result = await db.cleanup_old_messages(cutoff_date)
        
        assert result == 10
        mock_chat_messages.delete_many.assert_called_once()