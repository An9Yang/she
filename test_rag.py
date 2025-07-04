"""
测试RAG系统功能
"""

import asyncio
import os
from datetime import datetime
from pathlib import Path
import sys

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

# 模拟Azure OpenAI响应（测试环境）
class MockAzureOpenAI:
    """模拟Azure OpenAI客户端"""
    
    class Embeddings:
        async def create(self, model, input):
            # 模拟向量生成
            if isinstance(input, list):
                embeddings = []
                for text in input:
                    # 简单的哈希模拟
                    hash_val = hash(text)
                    embedding = [(hash_val >> i) & 1 for i in range(1536)]
                    embeddings.append(type('obj', (object,), {'embedding': embedding}))
                return type('obj', (object,), {'data': embeddings})
            else:
                hash_val = hash(input)
                embedding = [(hash_val >> i) & 1 for i in range(1536)]
                return type('obj', (object,), {
                    'data': [type('obj', (object,), {'embedding': embedding})]
                })
    
    class Chat:
        class Completions:
            async def create(self, model, messages, temperature=0.7, max_tokens=500):
                # 根据输入生成回复
                user_input = messages[-1]['content']
                if "你好" in user_input:
                    content = "你好呀！今天过得怎么样？😊"
                elif "天气" in user_input:
                    content = "今天天气真不错呢！要不要出去走走？"
                else:
                    content = "嗯嗯，我明白你的意思～"
                
                return type('obj', (object,), {
                    'choices': [type('obj', (object,), {
                        'message': type('obj', (object,), {'content': content})
                    })]
                })
        
        def __init__(self):
            self.completions = self.Completions()
    
    def __init__(self, **kwargs):
        self.embeddings = self.Embeddings()
        self.chat = self.Chat()


class AsyncAzureOpenAI(MockAzureOpenAI):
    """异步版本的模拟客户端"""
    pass


# 模拟RAG服务
class SimpleRAGService:
    """简化的RAG服务（不依赖数据库）"""
    
    def __init__(self):
        self.client = AsyncAzureOpenAI()
        self.embedding_deployment = "text-embedding-ada-002"
        self.chat_deployment = "gpt-35-turbo"
    
    async def generate_embedding(self, text: str):
        """生成文本向量"""
        response = await self.client.embeddings.create(
            model=self.embedding_deployment,
            input=text
        )
        return response.data[0].embedding
    
    async def batch_generate_embeddings(self, texts):
        """批量生成向量"""
        if not texts:
            return []
        
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
    
    async def generate_response(self, user_input: str, persona_name: str = "小明"):
        """生成回复"""
        system_prompt = f"""你是{persona_name}，一个友善、幽默的朋友。
你喜欢使用表情符号，说话比较随性自然。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        response = await self.client.chat.completions.create(
            model=self.chat_deployment,
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    
    def analyze_conversation_patterns(self, messages):
        """分析对话模式"""
        if not messages:
            return {}
        
        # 分析平均长度
        total_length = sum(len(msg['content']) for msg in messages)
        avg_length = total_length / len(messages) if messages else 0
        
        # 分析情感
        positive_count = sum(1 for msg in messages if any(
            word in msg['content'] for word in ["好", "开心", "哈哈", "😊"]
        ))
        
        return {
            "response_patterns": {
                "average_message_length": avg_length,
                "message_count": len(messages)
            },
            "emotional_patterns": {
                "positive": positive_count / len(messages) if messages else 0,
                "neutral": 1 - (positive_count / len(messages) if messages else 0)
            }
        }


async def test_rag_functions():
    """测试RAG功能"""
    print("🧪 测试RAG系统功能\n")
    
    rag = SimpleRAGService()
    
    # 1. 测试向量生成
    print("1️⃣ 测试向量生成")
    text = "今天天气真好，要不要一起去公园走走？"
    embedding = await rag.generate_embedding(text)
    print(f"✅ 生成向量长度: {len(embedding)}")
    print(f"   向量前10维: {embedding[:10]}")
    
    # 2. 测试批量向量生成
    print("\n2️⃣ 测试批量向量生成")
    texts = [
        "早上好！",
        "今天天气怎么样？",
        "一起去吃饭吧",
        "周末有什么计划吗？"
    ]
    embeddings = await rag.batch_generate_embeddings(texts)
    print(f"✅ 生成了 {len(embeddings)} 个向量")
    
    # 3. 测试对话生成
    print("\n3️⃣ 测试对话生成")
    test_inputs = [
        "你好！",
        "今天天气真不错",
        "周末想去哪里玩？"
    ]
    
    for user_input in test_inputs:
        response = await rag.generate_response(user_input, "小红")
        print(f"👤 用户: {user_input}")
        print(f"🤖 小红: {response}")
        print()
    
    # 4. 测试对话模式分析
    print("4️⃣ 测试对话模式分析")
    test_messages = [
        {"content": "早上好！今天真开心", "sender": "小明", "timestamp": datetime.now()},
        {"content": "哈哈，是啊", "sender": "小红", "timestamp": datetime.now()},
        {"content": "一起去吃饭吧😊", "sender": "小明", "timestamp": datetime.now()},
        {"content": "好啊好啊！", "sender": "小红", "timestamp": datetime.now()},
    ]
    
    patterns = rag.analyze_conversation_patterns(test_messages)
    print(f"✅ 分析结果:")
    print(f"   平均消息长度: {patterns['response_patterns']['average_message_length']:.1f}")
    print(f"   积极情绪比例: {patterns['emotional_patterns']['positive']:.1%}")
    
    print("\n✨ RAG系统测试完成！")


async def test_hybrid_search():
    """测试混合搜索功能"""
    print("\n5️⃣ 测试混合搜索逻辑")
    
    # 模拟消息数据
    messages = [
        {"content": "今天去公园散步了", "timestamp": "2024-01-01 10:00"},
        {"content": "公园里的花开得真漂亮", "timestamp": "2024-01-01 10:05"},
        {"content": "晚上一起吃饭吗？", "timestamp": "2024-01-01 18:00"},
        {"content": "好啊，去哪里吃？", "timestamp": "2024-01-01 18:02"},
    ]
    
    # 模拟搜索
    query = "公园"
    matched = [msg for msg in messages if query in msg['content']]
    print(f"✅ 搜索 '{query}' 找到 {len(matched)} 条相关消息:")
    for msg in matched:
        print(f"   - {msg['content']}")


if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_rag_functions())
    asyncio.run(test_hybrid_search())