"""RAG服务测试"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

from backend.services.rag_service import RAGService
from backend.core.database import Database


class TestRAGService:
    """RAG服务测试类"""
    
    @pytest.fixture
    async def rag_service(self, clean_db: Database) -> RAGService:
        """创建RAG服务实例"""
        return RAGService(clean_db)
    
    @pytest.fixture
    def mock_embeddings(self):
        """模拟嵌入向量"""
        return [0.1] * 1536  # Azure OpenAI text-embedding-ada-002 维度
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_init_rag_service(self, rag_service: RAGService):
        """测试RAG服务初始化"""
        assert rag_service is not None
        assert rag_service.db is not None
        assert hasattr(rag_service, 'search')
        assert hasattr(rag_service, 'index_messages')
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_index_messages(self, rag_service: RAGService, sample_messages, mock_embeddings):
        """测试索引消息"""
        persona_id = "test_persona_123"
        
        with patch.object(rag_service, '_generate_embedding', return_value=mock_embeddings):
            result = await rag_service.index_messages(persona_id, sample_messages)
            
            assert result is True
            
            # 验证消息被正确存储
            messages = await rag_service.db.messages.find(
                {"persona_id": persona_id}
            ).to_list(None)
            
            assert len(messages) == len(sample_messages)
            for msg, original in zip(messages, sample_messages):
                assert msg["content"] == original["content"]
                assert msg["sender"] == original["sender"]
                assert msg["persona_id"] == persona_id
                assert "embedding" in msg
                assert msg["embedding"] == mock_embeddings
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_index_empty_messages(self, rag_service: RAGService):
        """测试索引空消息列表"""
        result = await rag_service.index_messages("test_persona", [])
        assert result is True
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_search_similar_messages(self, rag_service: RAGService, mock_embeddings):
        """测试搜索相似消息"""
        persona_id = "search_test_persona"
        
        # 先索引一些消息
        test_messages = [
            {
                "sender": "Alice",
                "content": "I love programming in Python",
                "timestamp": datetime.now(),
                "metadata": {}
            },
            {
                "sender": "Bob",
                "content": "Python is great for data science",
                "timestamp": datetime.now(),
                "metadata": {}
            },
            {
                "sender": "Alice",
                "content": "Let's go for a walk",
                "timestamp": datetime.now(),
                "metadata": {}
            }
        ]
        
        with patch.object(rag_service, '_generate_embedding', return_value=mock_embeddings):
            await rag_service.index_messages(persona_id, test_messages)
            
            # 搜索相似消息
            query = "programming with Python"
            results = await rag_service.search(persona_id, query, k=2)
            
            assert len(results) <= 2
            # 由于使用了mock embeddings，所有消息的相似度都相同
            # 在实际情况下，前两个消息应该更相似
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_search_with_no_messages(self, rag_service: RAGService, mock_embeddings):
        """测试在没有消息的情况下搜索"""
        with patch.object(rag_service, '_generate_embedding', return_value=mock_embeddings):
            results = await rag_service.search("empty_persona", "any query")
            assert results == []
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_generate_embedding_mock(self, rag_service: RAGService):
        """测试生成嵌入向量（使用mock）"""
        text = "Test text for embedding"
        
        # 当前实现返回mock向量
        embedding = await rag_service._generate_embedding(text)
        
        assert embedding is not None
        assert isinstance(embedding, list)
        assert len(embedding) == 1536
        assert all(isinstance(x, (int, float)) for x in embedding)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_delete_persona_messages(self, rag_service: RAGService, mock_embeddings):
        """测试删除人格的所有消息"""
        persona_id = "delete_test_persona"
        
        # 先索引一些消息
        test_messages = [
            {
                "sender": "User",
                "content": f"Message {i}",
                "timestamp": datetime.now(),
                "metadata": {}
            }
            for i in range(5)
        ]
        
        with patch.object(rag_service, '_generate_embedding', return_value=mock_embeddings):
            await rag_service.index_messages(persona_id, test_messages)
        
        # 验证消息已存储
        count = await rag_service.db.messages.count_documents({"persona_id": persona_id})
        assert count == 5
        
        # 删除消息
        result = await rag_service.delete_persona_messages(persona_id)
        assert result is True
        
        # 验证消息已删除
        count = await rag_service.db.messages.count_documents({"persona_id": persona_id})
        assert count == 0
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_message_context(self, rag_service: RAGService, mock_embeddings):
        """测试获取消息上下文"""
        persona_id = "context_test_persona"
        
        # 索引一些有时间顺序的消息
        test_messages = [
            {
                "sender": "Alice",
                "content": "Hello!",
                "timestamp": datetime(2025, 7, 1, 10, 0),
                "metadata": {}
            },
            {
                "sender": "Bob",
                "content": "Hi Alice!",
                "timestamp": datetime(2025, 7, 1, 10, 1),
                "metadata": {}
            },
            {
                "sender": "Alice",
                "content": "How are you?",
                "timestamp": datetime(2025, 7, 1, 10, 2),
                "metadata": {}
            },
            {
                "sender": "Bob",
                "content": "I'm doing great!",
                "timestamp": datetime(2025, 7, 1, 10, 3),
                "metadata": {}
            }
        ]
        
        with patch.object(rag_service, '_generate_embedding', return_value=mock_embeddings):
            await rag_service.index_messages(persona_id, test_messages)
            
            # 获取上下文
            query = "How are you doing?"
            context = await rag_service.get_message_context(persona_id, query, k=2)
            
            assert context is not None
            assert isinstance(context, str)
            assert len(context) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_update_message_embedding(self, rag_service: RAGService, mock_embeddings):
        """测试更新单个消息的嵌入向量"""
        persona_id = "update_test_persona"
        
        # 创建一个没有嵌入的消息
        message = {
            "persona_id": persona_id,
            "sender": "Test",
            "content": "Original message",
            "timestamp": datetime.now(),
            "metadata": {}
        }
        
        result = await rag_service.db.messages.insert_one(message)
        message_id = result.inserted_id
        
        # 更新嵌入向量
        new_embedding = [0.2] * 1536
        with patch.object(rag_service, '_generate_embedding', return_value=new_embedding):
            await rag_service.update_message_embedding(str(message_id))
        
        # 验证更新
        updated_msg = await rag_service.db.messages.find_one({"_id": message_id})
        assert updated_msg["embedding"] == new_embedding
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_search_with_metadata_filter(self, rag_service: RAGService, mock_embeddings):
        """测试带元数据过滤的搜索"""
        persona_id = "filter_test_persona"
        
        # 索引带不同元数据的消息
        test_messages = [
            {
                "sender": "Alice",
                "content": "Python programming",
                "timestamp": datetime.now(),
                "metadata": {"platform": "whatsapp"}
            },
            {
                "sender": "Bob",
                "content": "Python coding",
                "timestamp": datetime.now(),
                "metadata": {"platform": "telegram"}
            },
            {
                "sender": "Charlie",
                "content": "Python development",
                "timestamp": datetime.now(),
                "metadata": {"platform": "whatsapp"}
            }
        ]
        
        with patch.object(rag_service, '_generate_embedding', return_value=mock_embeddings):
            await rag_service.index_messages(persona_id, test_messages)
            
            # 搜索只来自WhatsApp的消息
            results = await rag_service.search(
                persona_id,
                "Python",
                k=10,
                metadata_filter={"platform": "whatsapp"}
            )
            
            # 验证结果
            assert all(r.get("metadata", {}).get("platform") == "whatsapp" for r in results)