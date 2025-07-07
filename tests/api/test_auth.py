"""认证 API 端点测试"""
import pytest
from fastapi import status
from httpx import AsyncClient

from backend.models.user import User


class TestAuthAPI:
    """认证 API 测试类"""
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_register_success(self, async_client: AsyncClient):
        """测试成功注册用户"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
        
        response = await async_client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "id" in data
        assert "password" not in data
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_register_duplicate_username(self, async_client: AsyncClient, test_user: User):
        """测试重复用户名注册失败"""
        user_data = {
            "username": test_user.username,
            "email": "another@example.com",
            "password": "SecurePass123!"
        }
        
        response = await async_client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_register_invalid_email(self, async_client: AsyncClient):
        """测试无效邮箱注册失败"""
        user_data = {
            "username": "testuser",
            "email": "invalid-email",
            "password": "SecurePass123!"
        }
        
        response = await async_client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_register_weak_password(self, async_client: AsyncClient):
        """测试弱密码注册失败"""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "weak"
        }
        
        response = await async_client.post("/api/auth/register", json=user_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_login_success(self, async_client: AsyncClient, test_user_data: dict):
        """测试成功登录"""
        # 先注册用户
        await async_client.post("/api/auth/register", json=test_user_data)
        
        # 登录
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        
        response = await async_client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_login_invalid_credentials(self, async_client: AsyncClient, test_user: User):
        """测试无效凭证登录失败"""
        login_data = {
            "username": test_user.username,
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "incorrect" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_login_nonexistent_user(self, async_client: AsyncClient):
        """测试不存在的用户登录失败"""
        login_data = {
            "username": "nonexistent",
            "password": "password123"
        }
        
        response = await async_client.post("/api/auth/login", data=login_data)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_get_current_user(self, async_client: AsyncClient, test_user: User, auth_headers: dict):
        """测试获取当前用户信息"""
        response = await async_client.get("/api/auth/me", headers=auth_headers)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert "password" not in data
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_get_current_user_unauthorized(self, async_client: AsyncClient):
        """测试未授权获取用户信息"""
        response = await async_client.get("/api/auth/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.asyncio
    @pytest.mark.api
    @pytest.mark.auth
    async def test_get_current_user_invalid_token(self, async_client: AsyncClient):
        """测试无效令牌获取用户信息"""
        headers = {"Authorization": "Bearer invalid-token"}
        response = await async_client.get("/api/auth/me", headers=headers)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED