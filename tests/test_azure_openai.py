"""
测试Azure OpenAI连接
"""

import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv("backend/.env")

async def test_azure_openai():
    """测试Azure OpenAI API连接"""
    print("🔧 测试Azure OpenAI连接...\n")
    
    # 检查环境变量
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_key = os.getenv("AZURE_OPENAI_KEY")
    chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    
    print(f"📍 Endpoint: {endpoint}")
    print(f"🚀 Chat Deployment: {chat_deployment}")
    print(f"📅 API Version: {api_version}")
    print()
    
    if not all([endpoint, api_key, chat_deployment]):
        print("❌ 缺少必要的环境变量")
        return False
    
    try:
        from openai import AsyncAzureOpenAI
        
        # 创建客户端
        client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            api_key=api_key,
            api_version=api_version
        )
        
        print("✅ 客户端创建成功")
        
        # 测试聊天功能
        print("\n🤖 测试聊天生成...")
        response = await client.chat.completions.create(
            model=chat_deployment,
            messages=[
                {"role": "system", "content": "你是一个友好的助手"},
                {"role": "user", "content": "你好！请用一句话介绍自己。"}
            ],
            max_tokens=100
        )
        
        print(f"✅ 回复: {response.choices[0].message.content}")
        
        # 测试向量生成（如果有embedding模型）
        embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        if embedding_deployment and embedding_deployment != "text-embedding-ada-002":
            print("\n🔢 测试向量生成...")
            try:
                embedding_response = await client.embeddings.create(
                    model=embedding_deployment,
                    input="测试文本"
                )
                print(f"✅ 向量维度: {len(embedding_response.data[0].embedding)}")
            except Exception as e:
                print(f"⚠️  向量生成失败（可能该部署不支持）: {e}")
        
        print("\n✨ Azure OpenAI 连接测试成功！")
        return True
        
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n可能的原因：")
        print("1. API密钥无效")
        print("2. 端点URL错误")
        print("3. 部署名称错误")
        print("4. 网络连接问题")
        return False


async def test_simple_rag():
    """测试简单的RAG功能"""
    print("\n\n🧪 测试RAG功能...\n")
    
    try:
        from backend.services.rag_service import RAGService
        
        rag = RAGService()
        
        # 测试文本向量生成
        print("1️⃣ 测试文本向量生成...")
        embedding = await rag.generate_embedding("今天天气真好")
        print(f"✅ 生成向量长度: {len(embedding)}")
        
        # 测试对话生成
        print("\n2️⃣ 测试对话生成...")
        response = await rag.generate_response(
            persona_id="test123",
            user_input="你好，最近怎么样？",
            context_messages=[],
            chat_history=[]
        )
        print(f"✅ 生成回复: {response}")
        
        print("\n✨ RAG功能测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ RAG测试失败: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Second Self - Azure OpenAI 连接测试")
    print("=" * 60)
    
    # 运行测试
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # 测试Azure OpenAI
    openai_ok = loop.run_until_complete(test_azure_openai())
    
    # 如果OpenAI连接成功，测试RAG
    if openai_ok:
        loop.run_until_complete(test_simple_rag())
    
    print("\n" + "=" * 60)