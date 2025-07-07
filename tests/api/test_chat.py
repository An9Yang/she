"""聊天 API 端点测试"""
import pytest
from fastapi import status
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock

from backend.models.user import User
from backend.models.persona import Persona
from backend.models.chat import Chat


class TestChatAPI:
    """聊天 API 测试类"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_chats_empty(self, async_client: AsyncClient, test_user: User, auth_headers: dict):
        """测试获取空的聊天列表"""
        response = await async_client.get("/api/chats", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_chats_with_data(self, async_client: AsyncClient, test_chat: Chat, auth_headers: dict):
        """测试获取聊天列表"""
        response = await async_client.get("/api/chats", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["id"] == str(test_chat.id)
        assert data[0]["title"] == test_chat.title
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_chats_with_persona_filter(self, async_client: AsyncClient, test_chat: Chat, auth_headers: dict):
        """测试按人格过滤聊天列表"""
        response = await async_client.get(
            f"/api/chats?persona_id={test_chat.persona_id}", 
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["persona_id"] == test_chat.persona_id
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_create_chat(self, async_client: AsyncClient, test_persona: Persona, auth_headers: dict):
        """测试创建聊天"""
        chat_data = {
            "persona_id": str(test_persona.id),
            "title": "New Chat"
        }
        
        response = await async_client.post("/api/chats", json=chat_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == chat_data["title"]
        assert data["persona_id"] == chat_data["persona_id"]
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_create_chat_without_title(self, async_client: AsyncClient, test_persona: Persona, auth_headers: dict):
        """测试创建没有标题的聊天"""
        chat_data = {
            "persona_id": str(test_persona.id)
        }
        
        response = await async_client.post("/api/chats", json=chat_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert "与" in data["title"] and "的对话" in data["title"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_create_chat_invalid_persona(self, async_client: AsyncClient, auth_headers: dict):
        """测试使用无效人格ID创建聊天"""
        chat_data = {
            "persona_id": "507f1f77bcf86cd799439011",
            "title": "Invalid Chat"
        }
        
        response = await async_client.post("/api/chats", json=chat_data, headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_chat_by_id(self, async_client: AsyncClient, test_chat: Chat, auth_headers: dict):
        """测试通过ID获取聊天"""
        response = await async_client.get(f"/api/chats/{test_chat.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_chat.id)
        assert data["title"] == test_chat.title
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_chat_messages(self, async_client: AsyncClient, test_chat: Chat, auth_headers: dict):
        """测试获取聊天消息"""
        response = await async_client.get(f"/api/chats/{test_chat.id}/messages", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_send_message(self, async_client: AsyncClient, test_chat: Chat, auth_headers: dict, mock_openai_client):
        """测试发送消息"""
        with patch('backend.services.ai_service.AIService._get_client', return_value=mock_openai_client):
            message_data = {
                "content": "Hello, how are you?"
            }
            
            response = await async_client.post(
                f"/api/chats/{test_chat.id}/messages",
                json=message_data,
                headers=auth_headers
            )
            
            assert response.status_code == status.HTTP_201_CREATED
            data = response.json()
            assert data["role"] == "user"
            assert data["content"] == message_data["content"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_send_empty_message(self, async_client: AsyncClient, test_chat: Chat, auth_headers: dict):
        """测试发送空消息"""
        message_data = {
            "content": ""
        }
        
        response = await async_client.post(
            f"/api/chats/{test_chat.id}/messages",
            json=message_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_delete_chat(self, async_client: AsyncClient, test_chat: Chat, auth_headers: dict):
        """测试删除聊天"""
        response = await async_client.delete(f"/api/chats/{test_chat.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # 验证聊天已被删除
        get_response = await async_client.get(f"/api/chats/{test_chat.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_clear_chat_messages(self, async_client: AsyncClient, test_chat: Chat, auth_headers: dict):
        """测试清空聊天消息"""
        # 先发送一些消息
        with patch('backend.services.ai_service.AIService._get_client', return_value=mock_openai_client):
            for i in range(3):
                await async_client.post(
                    f"/api/chats/{test_chat.id}/messages",
                    json={"content": f"Message {i}"},
                    headers=auth_headers
                )
        
        # 清空消息
        response = await async_client.delete(f"/api/chats/{test_chat.id}/messages", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # 验证消息已被清空
        messages_response = await async_client.get(
            f"/api/chats/{test_chat.id}/messages", 
            headers=auth_headers
        )
        assert messages_response.json() == []
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_update_chat_title(self, async_client: AsyncClient, test_chat: Chat, auth_headers: dict):
        """测试更新聊天标题"""
        update_data = {
            "title": "Updated Chat Title"
        }
        
        response = await async_client.put(
            f"/api/chats/{test_chat.id}",
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_chat_unauthorized_user(self, async_client: AsyncClient, test_chat: Chat):
        """测试未授权用户访问聊天"""
        # 创建另一个用户
        other_user_data = {
            "username": "otheruser",
            "email": "other@example.com", 
            "password": "OtherPass123!"
        }
        
        await async_client.post("/api/auth/register", json=other_user_data)
        
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": other_user_data["username"], "password": other_user_data["password"]}
        )
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # 尝试访问第一个用户的聊天
        response = await async_client.get(f"/api/chats/{test_chat.id}", headers=other_headers)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN