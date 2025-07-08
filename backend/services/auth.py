"""
认证服务 - MongoDB版本
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from beanie import PydanticObjectId

from backend.core.config import settings
from backend.models.user import User
from backend.schemas.user import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


class AuthService:
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """密码哈希"""
        return pwd_context.hash(password)
    
    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        """创建用户"""
        # 如果没有提供username，使用email的用户名部分
        if not user_data.username:
            user_data.username = user_data.email.split('@')[0]
        
        # 检查邮箱是否已存在
        existing_user = await User.find_one(User.email == user_data.email)
        if existing_user:
            return None
        
        # 检查用户名是否已存在
        existing_username = await User.find_one(User.username == user_data.username)
        if existing_username:
            return None
        
        # 创建新用户
        user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=self.get_password_hash(user_data.password)
        )
        await user.save()
        return user
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """认证用户"""
        # 支持邮箱或用户名登录
        user = await User.find_one(
            {"$or": [
                {"username": username},
                {"email": username}
            ]}
        )
        
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """从token获取当前用户"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id: str = payload.get("sub")
            if user_id is None:
                return None
        except JWTError:
            return None
        
        user = await User.get(PydanticObjectId(user_id))
        return user


async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    """依赖注入：获取当前用户"""
    auth_service = AuthService()
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user