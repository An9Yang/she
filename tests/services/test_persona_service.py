"""人格服务测试"""
import pytest
from datetime import datetime
from bson import ObjectId

from backend.services.persona_service import PersonaService
from backend.core.database import Database
from backend.models.persona import Persona


class TestPersonaService:
    """人格服务测试类"""
    
    @pytest.fixture
    async def persona_service(self, clean_db: Database) -> PersonaService:
        """创建人格服务实例"""
        return PersonaService(clean_db)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_create_persona(self, persona_service: PersonaService):
        """测试创建人格"""
        persona_data = {
            "name": "Test Persona",
            "description": "A test persona for unit testing",
            "user_id": str(ObjectId()),
            "source_type": "whatsapp",
            "message_count": 100,
            "metadata": {
                "platform": "WhatsApp",
                "created_from": "test"
            }
        }
        
        persona = await persona_service.create_persona(**persona_data)
        
        assert persona is not None
        assert persona.name == persona_data["name"]
        assert persona.description == persona_data["description"]
        assert persona.user_id == persona_data["user_id"]
        assert persona.source_type == persona_data["source_type"]
        assert persona.message_count == persona_data["message_count"]
        assert persona.metadata == persona_data["metadata"]
        assert persona.id is not None
        assert isinstance(persona.created_at, datetime)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_persona_by_id(self, persona_service: PersonaService):
        """测试通过ID获取人格"""
        # 先创建人格
        persona_data = {
            "name": "Find Me",
            "user_id": str(ObjectId()),
            "source_type": "telegram"
        }
        created_persona = await persona_service.create_persona(**persona_data)
        
        # 通过ID查找
        found_persona = await persona_service.get_persona_by_id(str(created_persona.id))
        
        assert found_persona is not None
        assert found_persona.id == created_persona.id
        assert found_persona.name == created_persona.name
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_persona_by_id_not_found(self, persona_service: PersonaService):
        """测试获取不存在的人格"""
        fake_id = str(ObjectId())
        found_persona = await persona_service.get_persona_by_id(fake_id)
        assert found_persona is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_persona_by_id_invalid_format(self, persona_service: PersonaService):
        """测试无效ID格式"""
        found_persona = await persona_service.get_persona_by_id("invalid-id")
        assert found_persona is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_user_personas(self, persona_service: PersonaService):
        """测试获取用户的所有人格"""
        user_id = str(ObjectId())
        
        # 创建多个人格
        personas_data = [
            {"name": "Persona 1", "user_id": user_id, "source_type": "whatsapp"},
            {"name": "Persona 2", "user_id": user_id, "source_type": "telegram"},
            {"name": "Persona 3", "user_id": user_id, "source_type": "wechat"}
        ]
        
        for data in personas_data:
            await persona_service.create_persona(**data)
        
        # 创建其他用户的人格
        other_user_id = str(ObjectId())
        await persona_service.create_persona(
            name="Other User Persona",
            user_id=other_user_id,
            source_type="whatsapp"
        )
        
        # 获取第一个用户的人格
        user_personas = await persona_service.get_user_personas(user_id)
        
        assert len(user_personas) == 3
        assert all(p.user_id == user_id for p in user_personas)
        assert {p.name for p in user_personas} == {"Persona 1", "Persona 2", "Persona 3"}
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_user_personas_empty(self, persona_service: PersonaService):
        """测试获取没有人格的用户"""
        user_id = str(ObjectId())
        personas = await persona_service.get_user_personas(user_id)
        assert personas == []
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_update_persona(self, persona_service: PersonaService):
        """测试更新人格"""
        # 创建人格
        original_data = {
            "name": "Original Name",
            "description": "Original description",
            "user_id": str(ObjectId()),
            "source_type": "whatsapp"
        }
        persona = await persona_service.create_persona(**original_data)
        
        # 更新人格
        update_data = {
            "name": "Updated Name",
            "description": "Updated description",
            "metadata": {"updated": True}
        }
        
        updated_persona = await persona_service.update_persona(
            str(persona.id),
            **update_data
        )
        
        assert updated_persona is not None
        assert updated_persona.name == update_data["name"]
        assert updated_persona.description == update_data["description"]
        assert updated_persona.metadata == update_data["metadata"]
        assert updated_persona.source_type == original_data["source_type"]  # 未更新的字段保持不变
        assert updated_persona.updated_at > persona.created_at
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_update_persona_not_found(self, persona_service: PersonaService):
        """测试更新不存在的人格"""
        fake_id = str(ObjectId())
        updated_persona = await persona_service.update_persona(
            fake_id,
            name="New Name"
        )
        assert updated_persona is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_delete_persona(self, persona_service: PersonaService):
        """测试删除人格"""
        # 创建人格
        persona = await persona_service.create_persona(
            name="To Be Deleted",
            user_id=str(ObjectId()),
            source_type="whatsapp"
        )
        
        # 删除人格
        result = await persona_service.delete_persona(str(persona.id))
        assert result is True
        
        # 验证已删除
        deleted_persona = await persona_service.get_persona_by_id(str(persona.id))
        assert deleted_persona is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_delete_persona_not_found(self, persona_service: PersonaService):
        """测试删除不存在的人格"""
        fake_id = str(ObjectId())
        result = await persona_service.delete_persona(fake_id)
        assert result is False
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_persona_by_name_and_user(self, persona_service: PersonaService):
        """测试通过名称和用户ID获取人格"""
        user_id = str(ObjectId())
        persona_name = "Unique Name"
        
        # 创建人格
        await persona_service.create_persona(
            name=persona_name,
            user_id=user_id,
            source_type="whatsapp"
        )
        
        # 查找人格
        found_persona = await persona_service.get_persona_by_name_and_user(
            persona_name,
            user_id
        )
        
        assert found_persona is not None
        assert found_persona.name == persona_name
        assert found_persona.user_id == user_id
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_update_persona_message_count(self, persona_service: PersonaService):
        """测试更新人格消息计数"""
        # 创建人格
        persona = await persona_service.create_persona(
            name="Message Counter",
            user_id=str(ObjectId()),
            source_type="whatsapp",
            message_count=10
        )
        
        # 增加消息计数
        await persona_service.update_persona_message_count(str(persona.id), 5)
        
        # 验证更新
        updated_persona = await persona_service.get_persona_by_id(str(persona.id))
        assert updated_persona.message_count == 15
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_persona_statistics(self, persona_service: PersonaService):
        """测试获取人格统计信息"""
        # 创建人格
        persona = await persona_service.create_persona(
            name="Stats Test",
            user_id=str(ObjectId()),
            source_type="whatsapp",
            message_count=50
        )
        
        # 获取统计信息
        stats = await persona_service.get_persona_statistics(str(persona.id))
        
        assert stats is not None
        assert stats["message_count"] == 50
        assert stats["chat_count"] == 0  # 还没有创建聊天
        assert "created_at" in stats
        assert "last_chat_date" in stats