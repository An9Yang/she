"""
消息服务
"""

from typing import List, Optional
from datetime import datetime
from beanie import PydanticObjectId
from backend.models.message import Message
from backend.models.persona import Persona
from backend.services.rag_service import RAGService
from backend.core.logger import logger


class MessageService:
    """消息管理服务"""
    
    def __init__(self):
        """初始化消息服务"""
        self.rag_service = RAGService()
    
    async def create_message(
        self,
        persona_id: str,
        content: str,
        sender: str,
        timestamp: Optional[datetime] = None,
        metadata: Optional[dict] = None
    ) -> Message:
        """创建消息"""
        try:
            # 生成向量
            embedding = await self.rag_service.generate_embedding(content)
            
            # 创建消息
            message = Message(
                persona_id=PydanticObjectId(persona_id),
                content=content,
                sender=sender,
                timestamp=timestamp or datetime.now(),
                embedding=embedding,
                metadata=metadata or {}
            )
            
            await message.save()
            
            # 更新人格消息计数
            await Persona.find_one(
                {"_id": PydanticObjectId(persona_id)}
            ).update({"$inc": {"message_count": 1}})
            
            return message
            
        except Exception as e:
            logger.error(f"创建消息失败: {str(e)}")
            raise
    
    async def batch_create_messages(
        self,
        persona_id: str,
        messages_data: List[dict]
    ) -> List[Message]:
        """批量创建消息"""
        try:
            # 提取文本内容
            texts = [msg.get("content", "") for msg in messages_data]
            
            # 批量生成向量
            embeddings = await self.rag_service.batch_generate_embeddings(texts)
            
            # 创建消息对象
            messages = []
            for i, msg_data in enumerate(messages_data):
                message = Message(
                    persona_id=PydanticObjectId(persona_id),
                    content=msg_data.get("content", ""),
                    sender=msg_data.get("sender", "Unknown"),
                    timestamp=msg_data.get("timestamp", datetime.now()),
                    embedding=embeddings[i] if i < len(embeddings) else None,
                    metadata=msg_data.get("metadata", {})
                )
                messages.append(message)
            
            # 批量保存
            if messages:
                await Message.insert_many(messages)
                
                # 更新人格消息计数
                await Persona.find_one(
                    {"_id": PydanticObjectId(persona_id)}
                ).update({"$inc": {"message_count": len(messages)}})
            
            return messages
            
        except Exception as e:
            logger.error(f"批量创建消息失败: {str(e)}")
            raise
    
    async def get_messages(
        self,
        persona_id: str,
        limit: int = 50,
        skip: int = 0,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[Message]:
        """获取消息列表"""
        try:
            # 构建查询条件
            query = {"persona_id": PydanticObjectId(persona_id)}
            
            # 时间范围过滤
            if start_time or end_time:
                time_filter = {}
                if start_time:
                    time_filter["$gte"] = start_time
                if end_time:
                    time_filter["$lte"] = end_time
                if time_filter:
                    query["timestamp"] = time_filter
            
            # 查询消息
            messages = await Message.find(query).sort("-timestamp").skip(skip).limit(limit).to_list()
            
            return messages
            
        except Exception as e:
            logger.error(f"获取消息失败: {str(e)}")
            raise
    
    async def search_messages(
        self,
        persona_id: str,
        query: str,
        limit: int = 10,
        search_type: str = "hybrid"
    ) -> List[Message]:
        """搜索消息"""
        try:
            if search_type == "hybrid":
                # 使用混合搜索
                messages = await self.rag_service.hybrid_search(
                    persona_id=persona_id,
                    query=query,
                    limit=limit
                )
            else:
                # 简单文本搜索
                messages = await Message.find({
                    "persona_id": PydanticObjectId(persona_id),
                    "content": {"$regex": query, "$options": "i"}
                }).sort("-timestamp").limit(limit).to_list()
            
            return messages
            
        except Exception as e:
            logger.error(f"搜索消息失败: {str(e)}")
            raise
    
    async def delete_message(self, message_id: str) -> bool:
        """删除消息"""
        try:
            message = await Message.get(PydanticObjectId(message_id))
            if message:
                # 更新人格消息计数
                await Persona.find_one(
                    {"_id": message.persona_id}
                ).update({"$inc": {"message_count": -1}})
                
                # 删除消息
                await message.delete()
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"删除消息失败: {str(e)}")
            raise
    
    async def update_embeddings(self, persona_id: str, batch_size: int = 100) -> int:
        """更新消息向量"""
        try:
            updated_count = 0
            
            # 查找没有向量的消息
            while True:
                messages = await Message.find({
                    "persona_id": PydanticObjectId(persona_id),
                    "embedding": None
                }).limit(batch_size).to_list()
                
                if not messages:
                    break
                
                # 提取文本
                texts = [msg.content for msg in messages]
                
                # 生成向量
                embeddings = await self.rag_service.batch_generate_embeddings(texts)
                
                # 更新消息
                for i, msg in enumerate(messages):
                    if i < len(embeddings):
                        msg.embedding = embeddings[i]
                        await msg.save()
                        updated_count += 1
            
            return updated_count
            
        except Exception as e:
            logger.error(f"更新向量失败: {str(e)}")
            raise