"""聊天服务测试"""
import pytest
from datetime import datetime
from bson import ObjectId

from backend.services.chat_service import ChatService
from backend.services.persona_service import PersonaService
from backend.core.database import Database
from backend.models.chat import Chat
from backend.models.persona import Persona


class TestChatService:
    """聊天服务测试类"""
    
    @pytest.fixture
    async def chat_service(self, clean_db: Database) -> ChatService:
        """创建聊天服务实例"""
        return ChatService(clean_db)
    
    @pytest.fixture
    async def persona_service(self, clean_db: Database) -> PersonaService:
        """创建人格服务实例"""
        return PersonaService(clean_db)
    
    @pytest.fixture
    async def test_persona(self, persona_service: PersonaService) -> Persona:
        """创建测试人格"""
        return await persona_service.create_persona(
            name="Chat Test Persona",
            user_id=str(ObjectId()),
            source_type="whatsapp"
        )
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_create_chat(self, chat_service: ChatService, test_persona: Persona):
        """测试创建聊天"""
        user_id = test_persona.user_id
        
        chat = await chat_service.create_chat(
            user_id=user_id,
            persona_id=str(test_persona.id),
            title="Test Chat"
        )
        
        assert chat is not None
        assert chat.user_id == user_id
        assert chat.persona_id == str(test_persona.id)
        assert chat.title == "Test Chat"
        assert chat.id is not None
        assert isinstance(chat.created_at, datetime)
        assert chat.message_count == 0
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_create_chat_without_title(self, chat_service: ChatService, test_persona: Persona):
        """测试创建没有标题的聊天"""
        chat = await chat_service.create_chat(
            user_id=test_persona.user_id,
            persona_id=str(test_persona.id)
        )
        
        assert chat is not None
        assert f"与{test_persona.name}的对话" in chat.title
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_chat_by_id(self, chat_service: ChatService, test_persona: Persona):
        """测试通过ID获取聊天"""
        # 创建聊天
        chat = await chat_service.create_chat(
            user_id=test_persona.user_id,
            persona_id=str(test_persona.id),
            title="Find Me"
        )
        
        # 通过ID查找
        found_chat = await chat_service.get_chat_by_id(str(chat.id))
        
        assert found_chat is not None
        assert found_chat.id == chat.id
        assert found_chat.title == chat.title
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_chat_by_id_not_found(self, chat_service: ChatService):
        """测试获取不存在的聊天"""
        fake_id = str(ObjectId())
        found_chat = await chat_service.get_chat_by_id(fake_id)
        assert found_chat is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_user_chats(self, chat_service: ChatService, test_persona: Persona):
        """测试获取用户的所有聊天"""
        user_id = test_persona.user_id
        
        # 创建多个聊天
        chat_titles = ["Chat 1", "Chat 2", "Chat 3"]
        for title in chat_titles:
            await chat_service.create_chat(
                user_id=user_id,
                persona_id=str(test_persona.id),
                title=title
            )
        
        # 创建其他用户的聊天
        other_user_id = str(ObjectId())
        await chat_service.create_chat(
            user_id=other_user_id,
            persona_id=str(test_persona.id),
            title="Other User Chat"
        )
        
        # 获取第一个用户的聊天
        user_chats = await chat_service.get_user_chats(user_id)
        
        assert len(user_chats) == 3
        assert all(c.user_id == user_id for c in user_chats)
        assert {c.title for c in user_chats} == set(chat_titles)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_user_chats_with_persona_filter(self, chat_service: ChatService, persona_service: PersonaService):
        """测试按人格过滤用户聊天"""
        user_id = str(ObjectId())
        
        # 创建两个人格
        persona1 = await persona_service.create_persona(
            name="Persona 1",
            user_id=user_id,
            source_type="whatsapp"
        )
        persona2 = await persona_service.create_persona(
            name="Persona 2",
            user_id=user_id,
            source_type="telegram"
        )
        
        # 为每个人格创建聊天
        await chat_service.create_chat(user_id=user_id, persona_id=str(persona1.id), title="Chat P1-1")
        await chat_service.create_chat(user_id=user_id, persona_id=str(persona1.id), title="Chat P1-2")
        await chat_service.create_chat(user_id=user_id, persona_id=str(persona2.id), title="Chat P2-1")
        
        # 获取 persona1 的聊天
        persona1_chats = await chat_service.get_user_chats(user_id, persona_id=str(persona1.id))
        
        assert len(persona1_chats) == 2
        assert all(c.persona_id == str(persona1.id) for c in persona1_chats)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_update_chat(self, chat_service: ChatService, test_persona: Persona):
        """测试更新聊天"""
        # 创建聊天
        chat = await chat_service.create_chat(
            user_id=test_persona.user_id,
            persona_id=str(test_persona.id),
            title="Original Title"
        )
        
        # 更新聊天
        updated_chat = await chat_service.update_chat(
            str(chat.id),
            title="Updated Title"
        )
        
        assert updated_chat is not None
        assert updated_chat.title == "Updated Title"
        assert updated_chat.updated_at > chat.created_at
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_delete_chat(self, chat_service: ChatService, test_persona: Persona):
        """测试删除聊天"""
        # 创建聊天
        chat = await chat_service.create_chat(
            user_id=test_persona.user_id,
            persona_id=str(test_persona.id),
            title="To Be Deleted"
        )
        
        # 删除聊天
        result = await chat_service.delete_chat(str(chat.id))
        assert result is True
        
        # 验证已删除
        deleted_chat = await chat_service.get_chat_by_id(str(chat.id))
        assert deleted_chat is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_update_chat_message_count(self, chat_service: ChatService, test_persona: Persona):
        """测试更新聊天消息计数"""
        # 创建聊天
        chat = await chat_service.create_chat(
            user_id=test_persona.user_id,
            persona_id=str(test_persona.id),
            title="Message Counter"
        )
        
        assert chat.message_count == 0
        
        # 增加消息计数
        await chat_service.update_chat_message_count(str(chat.id), 1)
        
        # 验证更新
        updated_chat = await chat_service.get_chat_by_id(str(chat.id))
        assert updated_chat.message_count == 1
        
        # 再次增加
        await chat_service.update_chat_message_count(str(chat.id), 2)
        updated_chat = await chat_service.get_chat_by_id(str(chat.id))
        assert updated_chat.message_count == 3
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_recent_chats(self, chat_service: ChatService, test_persona: Persona):
        """测试获取最近的聊天"""
        user_id = test_persona.user_id
        
        # 创建多个聊天
        import asyncio
        chats = []
        for i in range(5):
            chat = await chat_service.create_chat(
                user_id=user_id,
                persona_id=str(test_persona.id),
                title=f"Chat {i}"
            )
            chats.append(chat)
            await asyncio.sleep(0.01)  # 确保时间戳不同
        
        # 获取最近3个聊天
        recent_chats = await chat_service.get_recent_chats(user_id, limit=3)
        
        assert len(recent_chats) == 3
        # 验证按时间倒序排列
        assert recent_chats[0].title == "Chat 4"
        assert recent_chats[1].title == "Chat 3"
        assert recent_chats[2].title == "Chat 2"
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_chat_exists(self, chat_service: ChatService, test_persona: Persona):
        """测试检查聊天是否存在"""
        # 创建聊天
        chat = await chat_service.create_chat(
            user_id=test_persona.user_id,
            persona_id=str(test_persona.id),
            title="Exists"
        )
        
        # 检查存在的聊天
        exists = await chat_service.chat_exists(str(chat.id))
        assert exists is True
        
        # 检查不存在的聊天
        fake_id = str(ObjectId())
        exists = await chat_service.chat_exists(fake_id)
        assert exists is False
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_chat_statistics(self, chat_service: ChatService, test_persona: Persona):
        """测试获取聊天统计信息"""
        # 创建聊天
        chat = await chat_service.create_chat(
            user_id=test_persona.user_id,
            persona_id=str(test_persona.id),
            title="Stats Test"
        )
        
        # 更新消息计数
        await chat_service.update_chat_message_count(str(chat.id), 10)
        
        # 获取统计信息
        stats = await chat_service.get_chat_statistics(str(chat.id))
        
        assert stats is not None
        assert stats["message_count"] == 10
        assert stats["duration_minutes"] >= 0
        assert "created_at" in stats
        assert "last_message_at" in stats