"""人格 API 端点测试"""
import pytest
from fastapi import status
from httpx import AsyncClient
from pathlib import Path

from backend.models.user import User
from backend.models.persona import Persona


class TestPersonasAPI:
    """人格 API 测试类"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_personas_empty(self, async_client: AsyncClient, test_user: User, auth_headers: dict):
        """测试获取空的人格列表"""
        response = await async_client.get("/api/personas", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data == []
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_personas_with_data(self, async_client: AsyncClient, test_persona: Persona, auth_headers: dict):
        """测试获取人格列表"""
        response = await async_client.get("/api/personas", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == test_persona.name
        assert data[0]["id"] == str(test_persona.id)
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_personas_unauthorized(self, async_client: AsyncClient):
        """测试未授权获取人格列表"""
        response = await async_client.get("/api/personas")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_persona_by_id(self, async_client: AsyncClient, test_persona: Persona, auth_headers: dict):
        """测试通过ID获取人格"""
        response = await async_client.get(f"/api/personas/{test_persona.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == str(test_persona.id)
        assert data["name"] == test_persona.name
        assert data["description"] == test_persona.description
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_persona_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """测试获取不存在的人格"""
        fake_id = "507f1f77bcf86cd799439011"
        response = await async_client.get(f"/api/personas/{fake_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_persona_invalid_id(self, async_client: AsyncClient, auth_headers: dict):
        """测试无效ID格式"""
        response = await async_client.get("/api/personas/invalid-id", headers=auth_headers)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_update_persona(self, async_client: AsyncClient, test_persona: Persona, auth_headers: dict):
        """测试更新人格"""
        update_data = {
            "name": "Updated Persona",
            "description": "Updated description"
        }
        
        response = await async_client.put(
            f"/api/personas/{test_persona.id}", 
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["description"] == update_data["description"]
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_update_persona_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """测试更新不存在的人格"""
        fake_id = "507f1f77bcf86cd799439011"
        update_data = {"name": "Updated"}
        
        response = await async_client.put(
            f"/api/personas/{fake_id}", 
            json=update_data,
            headers=auth_headers
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_update_persona_unauthorized_user(self, async_client: AsyncClient, test_persona: Persona):
        """测试未授权用户更新人格"""
        # 创建另一个用户的认证头
        other_user_data = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "OtherPass123!"
        }
        
        # 注册另一个用户
        await async_client.post("/api/auth/register", json=other_user_data)
        
        # 登录获取令牌
        login_response = await async_client.post(
            "/api/auth/login",
            data={"username": other_user_data["username"], "password": other_user_data["password"]}
        )
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # 尝试更新第一个用户的人格
        update_data = {"name": "Hacked"}
        response = await async_client.put(
            f"/api/personas/{test_persona.id}", 
            json=update_data,
            headers=other_headers
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_delete_persona(self, async_client: AsyncClient, test_persona: Persona, auth_headers: dict):
        """测试删除人格"""
        response = await async_client.delete(f"/api/personas/{test_persona.id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        
        # 验证人格已被删除
        get_response = await async_client.get(f"/api/personas/{test_persona.id}", headers=auth_headers)
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_delete_persona_not_found(self, async_client: AsyncClient, auth_headers: dict):
        """测试删除不存在的人格"""
        fake_id = "507f1f77bcf86cd799439011"
        response = await async_client.delete(f"/api/personas/{fake_id}", headers=auth_headers)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    @pytest.mark.api
    async def test_get_persona_statistics(self, async_client: AsyncClient, test_persona: Persona, auth_headers: dict):
        """测试获取人格统计信息"""
        response = await async_client.get(f"/api/personas/{test_persona.id}/stats", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message_count" in data
        assert "chat_count" in data
        assert "last_chat_date" in data
        assert "created_at" in data