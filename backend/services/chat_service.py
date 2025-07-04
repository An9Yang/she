"""
对话服务
"""

from typing import List, Optional, Dict
from datetime import datetime
from beanie import PydanticObjectId
from backend.models.chat_model import Chat, ChatMessage
from backend.models.persona import Persona
from backend.services.rag_service import RAGService
from backend.services.message_service import MessageService
from backend.core.logger import logger


class ChatService:
    """对话管理服务"""
    
    def __init__(self):
        """初始化对话服务"""
        self.rag_service = RAGService()
        self.message_service = MessageService()
    
    async def create_chat(
        self,
        user_id: str,
        persona_id: str,
        title: Optional[str] = None
    ) -> Chat:
        """创建新对话"""
        try:
            # 验证人格存在
            persona = await Persona.get(PydanticObjectId(persona_id))
            if not persona:
                raise ValueError("人格不存在")
            
            # 创建对话
            chat = Chat(
                user_id=PydanticObjectId(user_id),
                persona_id=PydanticObjectId(persona_id),
                title=title or f"与{persona.name}的对话",
                messages=[],
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            await chat.save()
            return chat
            
        except Exception as e:
            logger.error(f"创建对话失败: {str(e)}")
            raise
    
    async def get_chat(self, chat_id: str) -> Optional[Chat]:
        """获取对话"""
        try:
            return await Chat.get(PydanticObjectId(chat_id))
        except Exception as e:
            logger.error(f"获取对话失败: {str(e)}")
            raise
    
    async def get_user_chats(
        self,
        user_id: str,
        limit: int = 20,
        skip: int = 0
    ) -> List[Chat]:
        """获取用户的对话列表"""
        try:
            chats = await Chat.find(
                {"user_id": PydanticObjectId(user_id)}
            ).sort("-updated_at").skip(skip).limit(limit).to_list()
            
            return chats
            
        except Exception as e:
            logger.error(f"获取用户对话列表失败: {str(e)}")
            raise
    
    async def send_message(
        self,
        chat_id: str,
        content: str,
        generate_response: bool = True
    ) -> Dict[str, ChatMessage]:
        """发送消息并获取回复"""
        try:
            # 获取对话
            chat = await Chat.get(PydanticObjectId(chat_id))
            if not chat:
                raise ValueError("对话不存在")
            
            # 创建用户消息
            user_message = ChatMessage(
                role="user",
                content=content,
                timestamp=datetime.now()
            )
            
            # 添加到对话历史
            chat.messages.append(user_message)
            chat.updated_at = datetime.now()
            
            result = {"user_message": user_message}
            
            if generate_response:
                # 搜索相关上下文
                context_messages = await self.rag_service.hybrid_search(
                    persona_id=str(chat.persona_id),
                    query=content,
                    limit=10
                )
                
                # 构建聊天历史
                chat_history = [
                    {"role": msg.role, "content": msg.content}
                    for msg in chat.messages[-10:]  # 最近10条
                ]
                
                # 生成回复
                response_content = await self.rag_service.generate_response(
                    persona_id=str(chat.persona_id),
                    user_input=content,
                    context_messages=context_messages,
                    chat_history=chat_history
                )
                
                # 创建助手消息
                assistant_message = ChatMessage(
                    role="assistant",
                    content=response_content,
                    timestamp=datetime.now()
                )
                
                # 添加到对话历史
                chat.messages.append(assistant_message)
                result["assistant_message"] = assistant_message
            
            # 保存对话
            await chat.save()
            
            return result
            
        except Exception as e:
            logger.error(f"发送消息失败: {str(e)}")
            raise
    
    async def regenerate_response(
        self,
        chat_id: str,
        message_index: int
    ) -> ChatMessage:
        """重新生成回复"""
        try:
            # 获取对话
            chat = await Chat.get(PydanticObjectId(chat_id))
            if not chat:
                raise ValueError("对话不存在")
            
            # 验证消息索引
            if message_index >= len(chat.messages) or message_index < 0:
                raise ValueError("消息索引无效")
            
            # 找到对应的用户消息
            if message_index == 0:
                user_input = chat.messages[0].content
                chat_history = []
            else:
                # 获取该消息之前的最后一条用户消息
                user_input = None
                for i in range(message_index - 1, -1, -1):
                    if chat.messages[i].role == "user":
                        user_input = chat.messages[i].content
                        break
                
                if not user_input:
                    raise ValueError("找不到对应的用户输入")
                
                # 构建到该点为止的聊天历史
                chat_history = [
                    {"role": msg.role, "content": msg.content}
                    for msg in chat.messages[:message_index]
                ]
            
            # 搜索相关上下文
            context_messages = await self.rag_service.hybrid_search(
                persona_id=str(chat.persona_id),
                query=user_input,
                limit=10
            )
            
            # 生成新回复
            response_content = await self.rag_service.generate_response(
                persona_id=str(chat.persona_id),
                user_input=user_input,
                context_messages=context_messages,
                chat_history=chat_history
            )
            
            # 更新消息
            chat.messages[message_index].content = response_content
            chat.messages[message_index].timestamp = datetime.now()
            chat.updated_at = datetime.now()
            
            # 保存对话
            await chat.save()
            
            return chat.messages[message_index]
            
        except Exception as e:
            logger.error(f"重新生成回复失败: {str(e)}")
            raise
    
    async def delete_chat(self, chat_id: str) -> bool:
        """删除对话"""
        try:
            chat = await Chat.get(PydanticObjectId(chat_id))
            if chat:
                await chat.delete()
                return True
            return False
            
        except Exception as e:
            logger.error(f"删除对话失败: {str(e)}")
            raise
    
    async def clear_chat_history(self, chat_id: str) -> Chat:
        """清空对话历史"""
        try:
            chat = await Chat.get(PydanticObjectId(chat_id))
            if not chat:
                raise ValueError("对话不存在")
            
            chat.messages = []
            chat.updated_at = datetime.now()
            await chat.save()
            
            return chat
            
        except Exception as e:
            logger.error(f"清空对话历史失败: {str(e)}")
            raise
    
    async def export_chat(self, chat_id: str) -> Dict:
        """导出对话"""
        try:
            chat = await Chat.get(PydanticObjectId(chat_id))
            if not chat:
                raise ValueError("对话不存在")
            
            # 获取人格信息
            persona = await Persona.get(chat.persona_id)
            
            export_data = {
                "chat_id": str(chat.id),
                "title": chat.title,
                "persona_name": persona.name if persona else "Unknown",
                "created_at": chat.created_at.isoformat(),
                "updated_at": chat.updated_at.isoformat(),
                "messages": [
                    {
                        "role": msg.role,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat()
                    }
                    for msg in chat.messages
                ]
            }
            
            return export_data
            
        except Exception as e:
            logger.error(f"导出对话失败: {str(e)}")
            raise