"""
Second Self - FastAPI Backend
主应用入口 - 简化版
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from dotenv import load_dotenv

from backend.api import auth, personas, chat_api, upload, adapter
from backend.core.config import settings
from backend.core.database import init_db, close_db

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Starting up Second Self backend...")
    # 初始化数据库
    await init_db()
    yield
    # 关闭数据库连接
    await close_db()
    logger.info("Shutting down...")


# 创建FastAPI实例
app = FastAPI(
    title="Second Self API",
    description="AI对话伴侣后端服务",
    version="0.1.0",
    lifespan=lifespan
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
app.include_router(adapter.router)  # API兼容性适配器
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(upload.router, prefix="/api/upload", tags=["上传"])
app.include_router(personas.router, prefix="/api/personas", tags=["人格"])
app.include_router(chat_api.router, prefix="/api/chat", tags=["对话"])


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
        "database": "connected",
        "version": settings.VERSION
    }