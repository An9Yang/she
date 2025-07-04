"""
AI服务 - 支持Azure OpenAI和OpenAI
"""

from typing import List, Optional, AsyncGenerator
import logging
from openai import AzureOpenAI, OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from backend.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """统一的AI服务接口"""
    
    def __init__(self):
        if settings.USE_AZURE_OPENAI:
            self.client = AzureOpenAI(
                azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
                api_key=settings.AZURE_OPENAI_KEY,
                api_version=settings.AZURE_OPENAI_VERSION
            )
            self.chat_model = settings.AZURE_OPENAI_CHAT_DEPLOYMENT
            self.embedding_model = settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT
        else:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            self.chat_model = "gpt-3.5-turbo"
            self.embedding_model = "text-embedding-3-small"
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def create_embedding(self, text: str) -> List[float]:
        """创建文本嵌入向量"""
        try:
            response = await self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"创建嵌入失败: {e}")
            raise
    
    async def batch_create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """批量创建嵌入向量"""
        embeddings = []
        batch_size = settings.EMBEDDING_BATCH_SIZE
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                response = await self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                embeddings.extend([item.embedding for item in response.data])
            except Exception as e:
                logger.error(f"批量嵌入失败: {e}")
                # 降级为单个处理
                for text in batch:
                    try:
                        embedding = await self.create_embedding(text)
                        embeddings.append(embedding)
                    except:
                        embeddings.append([0.0] * 1536)  # 默认向量
        
        return embeddings
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def generate_chat_completion(
        self,
        messages: List[dict],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ):
        """生成聊天回复"""
        try:
            return await self.client.chat.completions.create(
                model=self.chat_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
        except Exception as e:
            logger.error(f"生成回复失败: {e}")
            raise
    
    async def generate_chat_stream(
        self,
        messages: List[dict],
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """流式生成聊天回复"""
        try:
            stream = await self.generate_chat_completion(
                messages=messages,
                temperature=temperature,
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            logger.error(f"流式生成失败: {e}")
            yield f"抱歉，生成回复时出现错误: {str(e)}"
    
    async def analyze_personality(self, messages: List[str]) -> dict:
        """分析对话人格特征"""
        prompt = f"""
        分析以下对话消息的语言风格和人格特征：
        
        {chr(10).join(messages[:50])}  # 最多50条
        
        请提取：
        1. 语言风格（正式/随意/幽默等）
        2. 常用词汇和口头禅
        3. 情绪倾向
        4. 话题偏好
        5. 回复长度特征
        
        以JSON格式返回。
        """
        
        response = await self.generate_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        try:
            import json
            return json.loads(response.choices[0].message.content)
        except:
            return {
                "style": "未知",
                "keywords": [],
                "emotion": "中性",
                "topics": [],
                "avg_length": "中等"
            }


# 全局AI服务实例
ai_service = AIService()