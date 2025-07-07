"""用户流程集成测试"""
import pytest
from fastapi import status
from httpx import AsyncClient
from pathlib import Path
import json
from unittest.mock import patch

from backend.models.user import User
from backend.models.persona import Persona
from backend.models.chat import Chat


class TestUserFlow:
    """完整用户流程测试"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.slow
    async def test_complete_user_journey(self, async_client: AsyncClient, tmp_path: Path, mock_openai_client):
        """测试完整的用户旅程"""
        # 1. 注册新用户
        user_data = {
            "username": "journey_user",
            "email": "journey@example.com",
            "password": "JourneyPass123!"
        }
        
        register_response = await async_client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == status.HTTP_201_CREATED
        user_id = register_response.json()["id"]
        
        # 2. 登录获取令牌
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": user_data["username"], "password": user_data["password"]}
        )
        assert login_response.status_code == status.HTTP_200_OK
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 3. 上传聊天文件创建人格
        chat_content = """[2025-07-01 10:00:00] Alice: Hello! How are you today?
[2025-07-01 10:01:00] Bob: I'm doing great, thanks for asking!
[2025-07-01 10:02:00] Alice: That's wonderful to hear. What are you working on?
[2025-07-01 10:03:00] Bob: I'm learning Python programming.
[2025-07-01 10:04:00] Alice: Python is amazing! I love it too.
[2025-07-01 10:05:00] Bob: Yes, it's very versatile and easy to learn."""
        
        test_file = tmp_path / "journey_chat.txt"
        test_file.write_text(chat_content)
        
        with open(test_file, "rb") as f:
            files = {"file": ("journey_chat.txt", f, "text/plain")}
            data = {"source_type": "whatsapp", "persona_name": "Journey Assistant"}
            
            upload_response = await async_client.post(
                "/api/upload",
                files=files,
                data=data,
                headers=headers
            )
        
        assert upload_response.status_code == status.HTTP_201_CREATED
        upload_result = upload_response.json()
        persona_id = upload_result["persona_id"]
        assert upload_result["message_count"] == 6
        
        # 4. 获取人格列表
        personas_response = await async_client.get("/api/personas", headers=headers)
        assert personas_response.status_code == status.HTTP_200_OK
        personas = personas_response.json()
        assert len(personas) == 1
        assert personas[0]["name"] == "Journey Assistant"
        
        # 5. 创建聊天会话
        chat_data = {
            "persona_id": persona_id,
            "title": "My First Chat"
        }
        create_chat_response = await async_client.post(
            "/api/chats",
            json=chat_data,
            headers=headers
        )
        assert create_chat_response.status_code == status.HTTP_201_CREATED
        chat = create_chat_response.json()
        chat_id = chat["id"]
        
        # 6. 发送消息并获取AI响应
        with patch('backend.services.ai_service.AIService._get_client', return_value=mock_openai_client):
            message_data = {"content": "Tell me about Python programming"}
            send_message_response = await async_client.post(
                f"/api/chats/{chat_id}/messages",
                json=message_data,
                headers=headers
            )
            assert send_message_response.status_code == status.HTTP_201_CREATED
            user_message = send_message_response.json()
            assert user_message["role"] == "user"
            assert user_message["content"] == message_data["content"]
        
        # 7. 获取聊天历史
        messages_response = await async_client.get(
            f"/api/chats/{chat_id}/messages",
            headers=headers
        )
        assert messages_response.status_code == status.HTTP_200_OK
        messages = messages_response.json()
        assert len(messages) >= 1  # 至少有用户消息
        
        # 8. 获取聊天列表
        chats_response = await async_client.get("/api/chats", headers=headers)
        assert chats_response.status_code == status.HTTP_200_OK
        chats = chats_response.json()
        assert len(chats) == 1
        assert chats[0]["title"] == "My First Chat"
        
        # 9. 更新聊天标题
        update_chat_data = {"title": "Python Discussion"}
        update_chat_response = await async_client.put(
            f"/api/chats/{chat_id}",
            json=update_chat_data,
            headers=headers
        )
        assert update_chat_response.status_code == status.HTTP_200_OK
        updated_chat = update_chat_response.json()
        assert updated_chat["title"] == "Python Discussion"
        
        # 10. 获取用户信息
        me_response = await async_client.get("/api/auth/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK
        me = me_response.json()
        assert me["username"] == user_data["username"]
        assert me["email"] == user_data["email"]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_multi_persona_workflow(self, async_client: AsyncClient, tmp_path: Path, mock_openai_client):
        """测试多人格工作流"""
        # 1. 注册并登录
        user_data = {
            "username": "multi_persona_user",
            "email": "multi@example.com",
            "password": "MultiPass123!"
        }
        
        await async_client.post("/api/auth/register", json=user_data)
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": user_data["username"], "password": user_data["password"]}
        )
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. 创建多个人格
        personas = []
        for i in range(3):
            chat_content = f"[2025-07-01 10:00:00] Person{i}: Hello from persona {i}!"
            test_file = tmp_path / f"chat_{i}.txt"
            test_file.write_text(chat_content)
            
            with open(test_file, "rb") as f:
                files = {"file": (f"chat_{i}.txt", f, "text/plain")}
                data = {"source_type": "whatsapp", "persona_name": f"Persona {i}"}
                
                upload_response = await async_client.post(
                    "/api/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
            
            assert upload_response.status_code == status.HTTP_201_CREATED
            personas.append(upload_response.json()["persona_id"])
        
        # 3. 为每个人格创建聊天
        chat_ids = []
        for i, persona_id in enumerate(personas):
            chat_response = await async_client.post(
                "/api/chats",
                json={"persona_id": persona_id, "title": f"Chat with Persona {i}"},
                headers=headers
            )
            assert chat_response.status_code == status.HTTP_201_CREATED
            chat_ids.append(chat_response.json()["id"])
        
        # 4. 验证可以获取所有聊天
        all_chats_response = await async_client.get("/api/chats", headers=headers)
        assert all_chats_response.status_code == status.HTTP_200_OK
        all_chats = all_chats_response.json()
        assert len(all_chats) == 3
        
        # 5. 按人格过滤聊天
        filtered_chats_response = await async_client.get(
            f"/api/chats?persona_id={personas[0]}",
            headers=headers
        )
        assert filtered_chats_response.status_code == status.HTTP_200_OK
        filtered_chats = filtered_chats_response.json()
        assert len(filtered_chats) == 1
        assert filtered_chats[0]["persona_id"] == personas[0]
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    async def test_error_handling_flow(self, async_client: AsyncClient):
        """测试错误处理流程"""
        # 1. 尝试未授权访问
        unauthorized_response = await async_client.get("/api/personas")
        assert unauthorized_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # 2. 尝试使用无效凭证登录
        invalid_login_response = await async_client.post(
            "/api/auth/login",
            data={"username": "nonexistent", "password": "wrongpass"}
        )
        assert invalid_login_response.status_code == status.HTTP_401_UNAUTHORIZED
        
        # 3. 尝试注册已存在的用户
        existing_user = {
            "username": "existing_user",
            "email": "existing@example.com",
            "password": "ExistingPass123!"
        }
        
        # 第一次注册成功
        first_register = await async_client.post("/api/auth/register", json=existing_user)
        assert first_register.status_code == status.HTTP_201_CREATED
        
        # 第二次注册失败
        second_register = await async_client.post("/api/auth/register", json=existing_user)
        assert second_register.status_code == status.HTTP_400_BAD_REQUEST
        
        # 4. 尝试使用无效的令牌
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        invalid_token_response = await async_client.get("/api/auth/me", headers=invalid_headers)
        assert invalid_token_response.status_code == status.HTTP_401_UNAUTHORIZED