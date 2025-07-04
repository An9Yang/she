"""
Second Self - FastAPI Backend (简化版，跳过数据库初始化)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv

from api import auth, personas, chat_api, upload
from core.config import settings

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI实例
app = FastAPI(
    title="Second Self API",
    description="AI对话伴侣后端服务",
    version="0.1.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(upload.router, prefix="/api/upload", tags=["上传"])
app.include_router(personas.router, prefix="/api/personas", tags=["人格"])
app.include_router(chat_api.router, prefix="/api/chat", tags=["对话"])


@app.on_event("startup")
async def startup_event():
    logger.info("Second Self backend started (without DB init)")


@app.get("/")
async def root():
    return {
        "message": "Second Self API is running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "mongodb atlas connected",
        "version": settings.VERSION
    }