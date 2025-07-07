"""认证服务测试"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from backend.services.auth_service import AuthService
from backend.core.security import verify_password, create_access_token
from backend.core.database import Database
from backend.models.user import User


class TestAuthService:
    """认证服务测试类"""
    
    @pytest.fixture
    async def auth_service(self, clean_db: Database) -> AuthService:
        """创建认证服务实例"""
        return AuthService(clean_db)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_register_user_success(self, auth_service: AuthService):
        """测试成功注册用户"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePass123!"
        }
        
        user = await auth_service.register_user(**user_data)
        
        assert user is not None
        assert user.username == user_data["username"]
        assert user.email == user_data["email"]
        assert user.id is not None
        assert hasattr(user, 'hashed_password')
        assert verify_password(user_data["password"], user.hashed_password)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_register_duplicate_username(self, auth_service: AuthService):
        """测试重复用户名注册"""
        user_data = {
            "username": "testuser",
            "email": "test1@example.com",
            "password": "SecurePass123!"
        }
        
        # 第一次注册成功
        await auth_service.register_user(**user_data)
        
        # 第二次注册失败
        user_data["email"] = "test2@example.com"
        with pytest.raises(ValueError, match="already exists"):
            await auth_service.register_user(**user_data)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_register_duplicate_email(self, auth_service: AuthService):
        """测试重复邮箱注册"""
        user_data = {
            "username": "user1",
            "email": "same@example.com",
            "password": "SecurePass123!"
        }
        
        # 第一次注册成功
        await auth_service.register_user(**user_data)
        
        # 第二次注册失败
        user_data["username"] = "user2"
        with pytest.raises(ValueError, match="already exists"):
            await auth_service.register_user(**user_data)
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_authenticate_user_success(self, auth_service: AuthService):
        """测试成功认证用户"""
        # 先注册用户
        user_data = {
            "username": "authuser",
            "email": "auth@example.com",
            "password": "SecurePass123!"
        }
        await auth_service.register_user(**user_data)
        
        # 认证用户
        authenticated_user = await auth_service.authenticate_user(
            user_data["username"], 
            user_data["password"]
        )
        
        assert authenticated_user is not None
        assert authenticated_user.username == user_data["username"]
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_authenticate_user_wrong_password(self, auth_service: AuthService):
        """测试错误密码认证"""
        # 先注册用户
        user_data = {
            "username": "authuser",
            "email": "auth@example.com",
            "password": "SecurePass123!"
        }
        await auth_service.register_user(**user_data)
        
        # 使用错误密码认证
        authenticated_user = await auth_service.authenticate_user(
            user_data["username"], 
            "WrongPassword123!"
        )
        
        assert authenticated_user is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_authenticate_nonexistent_user(self, auth_service: AuthService):
        """测试不存在的用户认证"""
        authenticated_user = await auth_service.authenticate_user(
            "nonexistent", 
            "anypassword"
        )
        
        assert authenticated_user is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_user_by_username(self, auth_service: AuthService):
        """测试通过用户名获取用户"""
        # 先注册用户
        user_data = {
            "username": "finduser",
            "email": "find@example.com",
            "password": "SecurePass123!"
        }
        registered_user = await auth_service.register_user(**user_data)
        
        # 通过用户名查找
        found_user = await auth_service.get_user_by_username(user_data["username"])
        
        assert found_user is not None
        assert found_user.id == registered_user.id
        assert found_user.username == user_data["username"]
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_get_user_by_username_not_found(self, auth_service: AuthService):
        """测试查找不存在的用户"""
        found_user = await auth_service.get_user_by_username("nonexistent")
        assert found_user is None
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_update_user_last_login(self, auth_service: AuthService):
        """测试更新用户最后登录时间"""
        # 先注册用户
        user_data = {
            "username": "loginuser",
            "email": "login@example.com",
            "password": "SecurePass123!"
        }
        user = await auth_service.register_user(**user_data)
        
        # 记录初始时间
        initial_last_login = user.last_login
        
        # 等待一小段时间
        import asyncio
        await asyncio.sleep(0.1)
        
        # 更新最后登录时间
        await auth_service.update_user_last_login(user.id)
        
        # 重新获取用户
        updated_user = await auth_service.get_user_by_username(user.username)
        
        assert updated_user.last_login > initial_last_login
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_validate_password_strength(self, auth_service: AuthService):
        """测试密码强度验证"""
        # 测试弱密码
        weak_passwords = [
            "123456",  # 太简单
            "password",  # 太常见
            "Pass1!",  # 太短
            "passwordpassword",  # 没有数字和特殊字符
            "12345678",  # 只有数字
        ]
        
        for weak_pass in weak_passwords:
            is_valid = auth_service._validate_password_strength(weak_pass)
            assert not is_valid, f"密码 '{weak_pass}' 应该被认为是弱密码"
        
        # 测试强密码
        strong_passwords = [
            "SecurePass123!",
            "MyStr0ng@Password",
            "C0mpl3x!Pass#2025",
        ]
        
        for strong_pass in strong_passwords:
            is_valid = auth_service._validate_password_strength(strong_pass)
            assert is_valid, f"密码 '{strong_pass}' 应该被认为是强密码"
    
    @pytest.mark.asyncio
    @pytest.mark.unit
    @pytest.mark.service
    async def test_create_access_token(self, auth_service: AuthService):
        """测试创建访问令牌"""
        # 使用 auth_service 的方法创建令牌
        username = "testuser"
        token = create_access_token(data={"sub": username})
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # 验证令牌内容
        import jwt
        from backend.core.config import settings
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        assert decoded["sub"] == username
        assert "exp" in decoded