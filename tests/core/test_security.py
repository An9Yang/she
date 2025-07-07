"""安全模块测试"""
import pytest
from datetime import datetime, timedelta
import jwt

from backend.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token
)
from backend.core.config import settings


class TestSecurity:
    """安全功能测试类"""
    
    @pytest.mark.unit
    def test_password_hashing(self):
        """测试密码哈希"""
        plain_password = "SecurePassword123!"
        
        # 生成哈希
        hashed = get_password_hash(plain_password)
        
        assert hashed is not None
        assert hashed != plain_password
        assert len(hashed) > 50  # bcrypt哈希通常很长
        assert hashed.startswith("$2b$")  # bcrypt格式
    
    @pytest.mark.unit
    def test_password_verification_success(self):
        """测试密码验证成功"""
        plain_password = "TestPassword456!"
        hashed = get_password_hash(plain_password)
        
        # 验证正确的密码
        assert verify_password(plain_password, hashed) is True
    
    @pytest.mark.unit
    def test_password_verification_failure(self):
        """测试密码验证失败"""
        plain_password = "CorrectPassword"
        wrong_password = "WrongPassword"
        hashed = get_password_hash(plain_password)
        
        # 验证错误的密码
        assert verify_password(wrong_password, hashed) is False
    
    @pytest.mark.unit
    def test_password_hash_uniqueness(self):
        """测试密码哈希唯一性"""
        plain_password = "SamePassword123"
        
        # 生成两个哈希
        hash1 = get_password_hash(plain_password)
        hash2 = get_password_hash(plain_password)
        
        # 相同密码的哈希应该不同（因为盐值不同）
        assert hash1 != hash2
        
        # 但都能验证原始密码
        assert verify_password(plain_password, hash1) is True
        assert verify_password(plain_password, hash2) is True
    
    @pytest.mark.unit
    def test_create_access_token(self):
        """测试创建访问令牌"""
        data = {"sub": "testuser", "user_id": "123"}
        
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # 解码令牌验证内容
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert decoded["sub"] == "testuser"
        assert decoded["user_id"] == "123"
        assert "exp" in decoded
    
    @pytest.mark.unit
    def test_create_access_token_with_expiry(self):
        """测试创建带过期时间的访问令牌"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        
        token = create_access_token(data, expires_delta)
        
        decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # 验证过期时间
        exp_time = datetime.fromtimestamp(decoded["exp"])
        now = datetime.utcnow()
        
        # 过期时间应该在14-16分钟之间
        assert (exp_time - now).total_seconds() > 14 * 60
        assert (exp_time - now).total_seconds() < 16 * 60
    
    @pytest.mark.unit
    def test_decode_valid_token(self):
        """测试解码有效令牌"""
        data = {"sub": "testuser", "role": "admin"}
        token = create_access_token(data)
        
        decoded = decode_access_token(token)
        
        assert decoded is not None
        assert decoded["sub"] == "testuser"
        assert decoded["role"] == "admin"
    
    @pytest.mark.unit
    def test_decode_expired_token(self):
        """测试解码过期令牌"""
        data = {"sub": "testuser"}
        # 创建一个已过期的令牌
        token = create_access_token(data, timedelta(seconds=-1))
        
        decoded = decode_access_token(token)
        
        assert decoded is None
    
    @pytest.mark.unit
    def test_decode_invalid_token(self):
        """测试解码无效令牌"""
        invalid_token = "invalid.token.here"
        
        decoded = decode_access_token(invalid_token)
        
        assert decoded is None
    
    @pytest.mark.unit
    def test_decode_token_wrong_secret(self):
        """测试使用错误密钥解码令牌"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # 使用错误的密钥
        wrong_secret = "wrong-secret-key"
        with pytest.raises(jwt.InvalidSignatureError):
            jwt.decode(token, wrong_secret, algorithms=[settings.ALGORITHM])
    
    @pytest.mark.unit
    def test_token_algorithm(self):
        """测试令牌算法"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # 尝试用错误的算法解码
        with pytest.raises(jwt.InvalidAlgorithmError):
            jwt.decode(token, settings.SECRET_KEY, algorithms=["RS256"])
    
    @pytest.mark.unit
    def test_password_complexity_hash(self):
        """测试复杂密码的哈希处理"""
        complex_passwords = [
            "P@ssw0rd!2025",
            "超级密码123!@#",
            "🔐SecurePass123",
            "Very Long Password With Many Words And Numbers 123!",
            "!@#$%^&*()_+-=[]{}|;':\",./<>?"
        ]
        
        for password in complex_passwords:
            hashed = get_password_hash(password)
            assert verify_password(password, hashed) is True
    
    @pytest.mark.unit
    def test_empty_password_handling(self):
        """测试空密码处理"""
        # 空密码也应该能被哈希
        empty_hash = get_password_hash("")
        assert empty_hash is not None
        assert verify_password("", empty_hash) is True
        assert verify_password("not empty", empty_hash) is False