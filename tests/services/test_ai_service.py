"""AI服务测试"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import datetime

from backend.services.ai_service import AIService
from backend.services.rag_service import RAGService
from backend.core.database import Database


class TestAIService:
    """AI服务测试类"""
    
    @pytest.fixture
    async def ai_service(self, clean_db: Database) -> AIService:
        """创建AI服务实例"""
        rag_service = RAGService(clean_db)
        return AIService(clean_db, rag_service)
    
    @pytest.fixture
    def mock_chat_messages(self):
        """模拟聊天消息历史"""
        return [
            {"role": "user", "content": "Hello, how are you?"},
            {"role": "assistant", "content": "I'm doing well, thank you! How can I help you today?"},
            {"role": "user", "content": "Tell me about Python programming"}
        ]
    
    @pytest.fixture
    def mock_rag_results(self):
        """模拟RAG搜索结果"""
        return [
            {
                "content": "Python is a versatile programming language",
                "score": 0.95,
                "metadata": {"sender": "Alice", "timestamp": "2025-07-01"}
            },
            {
                "content": "I love using Python for data science",
                "score": 0.88,
                "metadata": {"sender": "Bob", "timestamp": "2025-07-02"}
            }
        ]
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_init_ai_service(self, ai_service: AIService):
        """测试AI服务初始化"""
        assert ai_service is not None
        assert ai_service.db is not None
        assert ai_service.rag_service is not None
        assert hasattr(ai_service, 'generate_response')
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_generate_response_simple(self, ai_service: AIService, mock_openai_client):
        """测试生成简单响应"""
        with patch.object(ai_service, '_get_client', return_value=mock_openai_client):
            response = await ai_service.generate_response(
                persona_id="test_persona",
                message="Hello!",
                chat_history=[]
            )
            
            assert response is not None
            assert isinstance(response, str)
            assert len(response) > 0
            assert response == "This is a test response"
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_generate_response_with_history(self, ai_service: AIService, mock_openai_client, mock_chat_messages):
        """测试带历史记录生成响应"""
        with patch.object(ai_service, '_get_client', return_value=mock_openai_client):
            response = await ai_service.generate_response(
                persona_id="test_persona",
                message="What did I ask about?",
                chat_history=mock_chat_messages
            )
            
            assert response is not None
            # 验证历史记录被传递给API
            mock_openai_client.chat.completions.create.assert_called_once()
            call_args = mock_openai_client.chat.completions.create.call_args
            messages = call_args[1]["messages"]
            assert len(messages) > len(mock_chat_messages)  # 包括系统提示词
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_generate_response_with_rag(self, ai_service: AIService, mock_openai_client, mock_rag_results):
        """测试使用RAG上下文生成响应"""
        with patch.object(ai_service, '_get_client', return_value=mock_openai_client):
            with patch.object(ai_service.rag_service, 'search', return_value=mock_rag_results):
                response = await ai_service.generate_response(
                    persona_id="test_persona",
                    message="Tell me about Python",
                    chat_history=[],
                    use_rag=True
                )
                
                assert response is not None
                # 验证RAG搜索被调用
                ai_service.rag_service.search.assert_called_once_with(
                    "test_persona",
                    "Tell me about Python",
                    k=5
                )
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_build_prompt_with_context(self, ai_service: AIService):
        """测试构建带上下文的提示词"""
        persona_data = {
            "name": "Test Assistant",
            "description": "A helpful test assistant",
            "metadata": {"personality": "friendly"}
        }
        
        context = "Previous conversation about Python programming"
        
        prompt = ai_service._build_prompt(persona_data, context)
        
        assert persona_data["name"] in prompt
        assert persona_data["description"] in prompt
        assert context in prompt
        assert "你是" in prompt or "You are" in prompt
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_format_chat_history(self, ai_service: AIService, mock_chat_messages):
        """测试格式化聊天历史"""
        formatted = ai_service._format_chat_history(mock_chat_messages)
        
        assert isinstance(formatted, list)
        assert len(formatted) == len(mock_chat_messages)
        for msg in formatted:
            assert "role" in msg
            assert "content" in msg
            assert msg["role"] in ["user", "assistant", "system"]
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_generate_response_error_handling(self, ai_service: AIService):
        """测试错误处理"""
        # 模拟API错误
        mock_client = AsyncMock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch.object(ai_service, '_get_client', return_value=mock_client):
            response = await ai_service.generate_response(
                persona_id="test_persona",
                message="Hello!",
                chat_history=[]
            )
            
            # 应该返回错误消息而不是抛出异常
            assert response is not None
            assert "error" in response.lower() or "sorry" in response.lower()
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_generate_response_with_persona_info(self, ai_service: AIService, mock_openai_client, clean_db: Database):
        """测试使用人格信息生成响应"""
        # 创建测试人格
        from backend.services.persona_service import PersonaService
        persona_service = PersonaService(clean_db)
        persona = await persona_service.create_persona(
            name="Friendly Bot",
            description="A very friendly and helpful assistant",
            user_id="test_user",
            source_type="test"
        )
        
        with patch.object(ai_service, '_get_client', return_value=mock_openai_client):
            response = await ai_service.generate_response(
                persona_id=str(persona.id),
                message="Hello!",
                chat_history=[]
            )
            
            assert response is not None
            # 验证人格信息被使用
            call_args = mock_openai_client.chat.completions.create.call_args
            messages = call_args[1]["messages"]
            system_message = messages[0]["content"]
            assert "Friendly Bot" in system_message
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_truncate_chat_history(self, ai_service: AIService):
        """测试截断过长的聊天历史"""
        # 创建很长的聊天历史
        long_history = []
        for i in range(100):
            long_history.append({"role": "user", "content": f"Message {i}"})
            long_history.append({"role": "assistant", "content": f"Response {i}"})
        
        truncated = ai_service._truncate_chat_history(long_history, max_messages=10)
        
        assert len(truncated) <= 10
        # 应该保留最新的消息
        assert truncated[-1]["content"] == "Response 99"
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_generate_summary(self, ai_service: AIService, mock_openai_client):
        """测试生成对话摘要"""
        messages = [
            {"role": "user", "content": "Let's talk about machine learning"},
            {"role": "assistant", "content": "Sure! Machine learning is fascinating..."},
            {"role": "user", "content": "What about neural networks?"},
            {"role": "assistant", "content": "Neural networks are a key component..."}
        ]
        
        with patch.object(ai_service, '_get_client', return_value=mock_openai_client):
            summary = await ai_service.generate_summary(messages)
            
            assert summary is not None
            assert isinstance(summary, str)
            assert len(summary) > 0
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_analyze_sentiment(self, ai_service: AIService, mock_openai_client):
        """测试情感分析"""
        message = "I'm really happy with the service!"
        
        # 修改mock响应为情感分析结果
        mock_openai_client.chat.completions.create.return_value = AsyncMock(
            choices=[
                AsyncMock(
                    message=AsyncMock(
                        content="positive",
                        role="assistant"
                    )
                )
            ]
        )
        
        with patch.object(ai_service, '_get_client', return_value=mock_openai_client):
            sentiment = await ai_service.analyze_sentiment(message)
            
            assert sentiment in ["positive", "negative", "neutral"]