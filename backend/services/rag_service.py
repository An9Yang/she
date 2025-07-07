"""
RAG服务实现
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import asyncio
from beanie import PydanticObjectId
from openai import AsyncAzureOpenAI
import numpy as np
from backend.core.config import settings
from backend.models.message import Message
from backend.models.persona import Persona
from backend.models.chat import ChatHistory
from backend.core.logger import logger
from backend.services.mock_embeddings import MockEmbeddingService


class RAGService:
    """混合RAG服务"""
    
    def __init__(self):
        """初始化RAG服务"""
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_key=settings.AZURE_OPENAI_KEY,
            api_version=getattr(settings, "AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
        )
        self.embedding_deployment = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        self.chat_deployment = settings.AZURE_OPENAI_CHAT_DEPLOYMENT
        
    async def generate_embedding(self, text: str) -> List[float]:
        """生成文本向量"""
        try:
            # 检查是否使用模拟embeddings
            use_mock = getattr(settings, "USE_MOCK_EMBEDDINGS", "false").lower() == "true"
            
            if use_mock:
                logger.info("使用模拟embedding服务")
                return MockEmbeddingService.generate_embedding(text)
            else:
                logger.info("使用Azure OpenAI embedding服务")
                response = await self.client.embeddings.create(
                    model=self.embedding_deployment,
                    input=text
                )
                return response.data[0].embedding
        except Exception as e:
            logger.error(f"生成向量失败: {str(e)}")
            # 如果Azure失败，降级到模拟服务
            logger.warning("Azure OpenAI失败，降级到模拟embedding服务")
            return MockEmbeddingService.generate_embedding(text)
    
    async def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量生成向量"""
        if not texts:
            return []
            
        try:
            # 检查是否使用模拟embeddings
            use_mock = getattr(settings, "USE_MOCK_EMBEDDINGS", "false").lower() == "true"
            
            if use_mock:
                logger.info("使用模拟embeddings服务")
                return MockEmbeddingService.generate_embeddings(texts)
            else:
                logger.info(f"使用Azure OpenAI批量生成{len(texts)}个embeddings")
                # Azure OpenAI限制每次请求最多16个文本
                batch_size = 16
                all_embeddings = []
                
                for i in range(0, len(texts), batch_size):
                    batch = texts[i:i + batch_size]
                    response = await self.client.embeddings.create(
                        model=self.embedding_deployment,
                        input=batch
                    )
                    embeddings = [item.embedding for item in response.data]
                    all_embeddings.extend(embeddings)
                    
                return all_embeddings
        except Exception as e:
            logger.error(f"批量生成向量失败: {str(e)}")
            # 如果Azure失败，降级到模拟服务
            logger.warning("Azure OpenAI失败，降级到模拟embeddings服务")
            return MockEmbeddingService.generate_embeddings(texts)
    
    async def hybrid_search(
        self, 
        persona_id: str,
        query: str,
        limit: int = 10,
        time_range: Optional[Dict[str, datetime]] = None
    ) -> List[Message]:
        """混合检索 - 简化版本"""
        try:
            # 构建查询条件
            query_filter = {
                "persona_id": PydanticObjectId(persona_id),
                "$or": [
                    {"content": {"$regex": query, "$options": "i"}},  # 内容匹配
                    {"sender": {"$regex": query, "$options": "i"}}    # 发送者匹配
                ]
            }
            
            # 时间范围过滤
            if time_range:
                time_filter = {}
                if "start" in time_range:
                    time_filter["$gte"] = time_range["start"]
                if "end" in time_range:
                    time_filter["$lte"] = time_range["end"]
                if time_filter:
                    query_filter["timestamp"] = time_filter
            
            # 执行查询
            messages = await Message.find(query_filter).limit(limit).to_list()
            
            return messages
            
        except Exception as e:
            logger.error(f"混合搜索失败: {str(e)}")
            # 降级到简单搜索
            return await Message.find(
                {"persona_id": PydanticObjectId(persona_id)}
            ).sort("-timestamp").limit(limit).to_list()
    
    async def generate_response(
        self,
        persona_id: str,
        user_input: str,
        context_messages: List[Message],
        chat_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """生成回复"""
        try:
            # 获取人格信息
            persona = await Persona.get(PydanticObjectId(persona_id))
            if not persona:
                raise ValueError("人格不存在")
            
            # 构建系统提示
            system_prompt = self._build_system_prompt(persona)
            
            # 构建上下文
            context = self._build_context(context_messages)
            
            # 构建消息历史
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"相关上下文:\n{context}"}
            ]
            
            # 添加聊天历史
            if chat_history:
                for msg in chat_history[-10:]:  # 最近10条
                    messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
            
            # 添加用户输入
            messages.append({"role": "user", "content": user_input})
            
            # 调用Azure OpenAI
            # o3模型使用max_completion_tokens而不是max_tokens
            # o3模型不支持temperature参数，只能用默认值1
            response = await self.client.chat.completions.create(
                model=self.chat_deployment,
                messages=messages,
                max_completion_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"生成回复失败: {str(e)}")
            raise
    
    def _build_system_prompt(self, persona: Persona) -> str:
        """构建系统提示"""
        prompt = f"""你是{persona.name}，需要模拟ta的说话风格和性格特点。

基本信息:
- 昵称: {persona.name}
- 消息数量: {persona.message_count}
- 活跃时间: {persona.created_at.strftime('%Y年%m月')}开始

性格特征:
"""
        
        # 添加性格特征
        if hasattr(persona, 'style_features') and persona.style_features:
            for trait, score in persona.style_features.items():
                if score > 0.7:
                    prompt += f"- {trait}: 非常明显\n"
                elif score > 0.4:
                    prompt += f"- {trait}: 比较明显\n"
        
        # 添加说话风格
        if hasattr(persona, 'sentence_patterns') and persona.sentence_patterns:
            prompt += f"\n说话风格:\n"
            if persona.emoji_profile and len(persona.emoji_profile) > 5:
                prompt += "- 经常使用表情符号\n"
            if persona.sentence_patterns:
                prompt += f"- 句式特点: {list(persona.sentence_patterns.keys())[:3]}\n"
            if persona.frequent_words:
                prompt += f"- 常用词语: {', '.join(persona.frequent_words[:5])}\n"
        
        prompt += """
请根据以上特征，用相似的语气和风格回复。保持自然，不要刻意模仿。
"""
        
        return prompt
    
    def _build_context(self, messages: List[Message]) -> str:
        """构建上下文"""
        if not messages:
            return "暂无相关上下文"
        
        context_parts = []
        for msg in messages[:5]:  # 最多5条相关消息
            timestamp = msg.timestamp.strftime("%Y-%m-%d %H:%M")
            context_parts.append(f"[{timestamp}] {msg.sender}: {msg.content}")
        
        return "\n".join(context_parts)
    
    async def analyze_conversation_patterns(
        self,
        persona_id: str,
        sample_size: int = 100
    ) -> Dict[str, Any]:
        """分析对话模式"""
        try:
            # 获取样本消息
            messages = await Message.find(
                {"persona_id": PydanticObjectId(persona_id)}
            ).sort("-timestamp").limit(sample_size).to_list()
            
            if not messages:
                return {}
            
            # 分析模式
            patterns = {
                "response_patterns": self._analyze_response_patterns(messages),
                "topic_transitions": self._analyze_topic_transitions(messages),
                "emotional_patterns": self._analyze_emotional_patterns(messages),
                "time_patterns": self._analyze_time_patterns(messages)
            }
            
            return patterns
            
        except Exception as e:
            logger.error(f"分析对话模式失败: {str(e)}")
            return {}
    
    def _analyze_response_patterns(self, messages: List[Message]) -> Dict[str, Any]:
        """分析回复模式"""
        # 简化实现
        total_length = sum(len(m.content) for m in messages)
        avg_length = total_length / len(messages) if messages else 0
        
        # 分析回复速度（假设连续消息）
        response_times = []
        for i in range(1, len(messages)):
            if messages[i].sender != messages[i-1].sender:
                time_diff = (messages[i-1].timestamp - messages[i].timestamp).total_seconds()
                if 0 < time_diff < 3600:  # 1小时内的回复
                    response_times.append(time_diff)
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "average_message_length": avg_length,
            "average_response_time_seconds": avg_response_time,
            "message_count": len(messages)
        }
    
    def _analyze_topic_transitions(self, messages: List[Message]) -> List[str]:
        """分析话题转换"""
        # 简化实现：识别问句
        topics = []
        for msg in messages:
            if "？" in msg.content or "?" in msg.content:
                topics.append(msg.content[:20] + "...")
        return topics[:5]  # 返回前5个话题
    
    def _analyze_emotional_patterns(self, messages: List[Message]) -> Dict[str, float]:
        """分析情感模式"""
        # 简化实现：基于关键词
        emotions = {
            "positive": 0,
            "negative": 0,
            "neutral": 0
        }
        
        positive_words = ["好", "哈哈", "开心", "喜欢", "棒", "😊", "😄", "❤️"]
        negative_words = ["不", "难过", "生气", "讨厌", "烦", "😔", "😢", "😡"]
        
        for msg in messages:
            content = msg.content.lower()
            has_positive = any(word in content for word in positive_words)
            has_negative = any(word in content for word in negative_words)
            
            if has_positive and not has_negative:
                emotions["positive"] += 1
            elif has_negative and not has_positive:
                emotions["negative"] += 1
            else:
                emotions["neutral"] += 1
        
        # 转换为比例
        total = sum(emotions.values())
        if total > 0:
            for key in emotions:
                emotions[key] = emotions[key] / total
        
        return emotions
    
    def _analyze_time_patterns(self, messages: List[Message]) -> Dict[str, Any]:
        """分析时间模式"""
        # 活跃时间段分析
        hour_distribution = {}
        for msg in messages:
            hour = msg.timestamp.hour
            hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
        
        # 找出最活跃的时间段
        if hour_distribution:
            peak_hour = max(hour_distribution, key=hour_distribution.get)
            peak_period = f"{peak_hour}:00-{(peak_hour+1)%24}:00"
        else:
            peak_period = "未知"
        
        return {
            "peak_activity_period": peak_period,
            "hour_distribution": hour_distribution
        }