"""
消息模型 - MongoDB版本，支持向量搜索
"""

from datetime import datetime
from typing import Optional, List
from pydantic import Field
from beanie import Document, Indexed, PydanticObjectId


class Message(Document):
    """消息文档模型 - 原始聊天记录"""
    
    # 关联
    persona_id: Indexed(PydanticObjectId)
    
    # 消息内容
    content: str
    sender: str  # 发送者名称
    timestamp: Indexed(datetime)
    
    # 向量嵌入 - 用于语义搜索
    embedding: Optional[List[float]] = None
    
    # 元数据
    message_type: str = "text"  # text, image, voice, video, file
    media_url: Optional[str] = None  # 媒体文件URL
    
    # 分析数据
    emotion: Optional[str] = None  # 情绪标签
    keywords: Optional[List[str]] = Field(default_factory=list)
    
    # 导入信息
    original_id: Optional[str] = None  # 原平台的消息ID
    import_batch: Optional[str] = None  # 导入批次标识
    
    class Settings:
        name = "messages"
        indexes = [
            "persona_id",
            "timestamp",
            "sender",
            # MongoDB Atlas Vector Search索引需要在Atlas UI中创建
            # 索引配置示例：
            # {
            #   "type": "vectorSearch",
            #   "fields": [{
            #     "type": "vector",
            #     "path": "embedding",
            #     "numDimensions": 1536,
            #     "similarity": "cosine"
            #   }]
            # }
        ]