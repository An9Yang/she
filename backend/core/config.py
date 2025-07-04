"""
配置管理 - Azure优化版
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # 基础配置
    PROJECT_NAME: str = "Second Self"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # 安全配置
    SECRET_KEY: str = Field(default="your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # MongoDB配置
    MONGODB_URL: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB连接字符串，支持MongoDB Atlas"
    )
    DATABASE_NAME: str = "secondself"
    
    # CORS配置
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://*.vercel.app",
    ]
    
    # Azure OpenAI配置
    AZURE_OPENAI_ENDPOINT: str = Field(default="", description="Azure OpenAI端点")
    AZURE_OPENAI_KEY: str = Field(default="", description="Azure OpenAI密钥")
    AZURE_OPENAI_VERSION: str = "2024-02-01"
    AZURE_OPENAI_API_VERSION: str = Field(default="2024-02-01", description="API版本")
    
    # 模型部署名称
    AZURE_OPENAI_CHAT_DEPLOYMENT: str = Field(default="gpt-35-turbo", description="聊天模型部署名")
    AZURE_OPENAI_EMBEDDING_DEPLOYMENT: str = Field(default="text-embedding-ada-002", description="嵌入模型部署名")
    
    # OpenAI配置（备用）
    USE_AZURE_OPENAI: bool = True
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API密钥（备用）")
    
    # 文件上传配置
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    UPLOAD_DIR: str = "./uploads"
    TEMP_DIR: str = "./temp"
    
    # Azure Blob Storage配置
    AZURE_STORAGE_CONNECTION_STRING: str = Field(default="", description="Azure存储连接字符串")
    AZURE_STORAGE_CONTAINER_NAME: str = "uploads"
    
    # 性能优化配置
    EMBEDDING_BATCH_SIZE: int = 100
    CACHE_EMBEDDINGS: bool = True
    MAX_RETRIES: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()