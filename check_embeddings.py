#!/usr/bin/env python3
"""
检查和配置向量（embeddings）服务
"""
import os
import sys
from pathlib import Path
import asyncio
from typing import List

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.core.config import settings
from backend.services.rag_service import RAGService
from backend.core.database import motor_client, init_db


async def check_current_config():
    """检查当前配置"""
    print("🔍 当前向量服务配置:")
    print("=" * 50)
    
    # 检查环境变量
    use_mock = getattr(settings, "USE_MOCK_EMBEDDINGS", "false").lower() == "true"
    print(f"USE_MOCK_EMBEDDINGS: {use_mock}")
    
    if not use_mock:
        print("\n✅ 使用真实的Azure OpenAI Embeddings")
        print(f"   端点: {settings.AZURE_OPENAI_ENDPOINT[:30]}...")
        print(f"   API密钥: {'已设置' if settings.AZURE_OPENAI_KEY else '❌ 未设置'}")
        print(f"   Embedding模型部署: {settings.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
        print(f"   API版本: {settings.AZURE_OPENAI_API_VERSION}")
    else:
        print("\n⚠️  使用Mock Embeddings（仿真模式）")
        print("   这会影响搜索质量，建议切换到真实服务")
    
    return use_mock


async def test_embedding_generation():
    """测试向量生成"""
    print("\n🧪 测试向量生成...")
    print("=" * 50)
    
    try:
        # 初始化数据库
        await init_db()
        
        # 创建RAG服务
        rag_service = RAGService()
        
        # 测试文本
        test_texts = [
            "Hello, how are you today?",
            "今天天气真不错",
            "我喜欢编程"
        ]
        
        print(f"测试文本数量: {len(test_texts)}")
        
        # 生成向量
        embeddings = await rag_service.generate_embeddings(test_texts)
        
        if embeddings and len(embeddings) == len(test_texts):
            print(f"✅ 成功生成 {len(embeddings)} 个向量")
            print(f"   向量维度: {len(embeddings[0])}")
            print(f"   向量类型: {type(embeddings[0][0])}")
            
            # 检查是否是mock向量
            if all(isinstance(e, (int, float)) and e == embeddings[0][0] for emb in embeddings for e in emb[:10]):
                print("   ⚠️  检测到Mock向量（所有值相同）")
            else:
                print("   ✅ 真实向量（值有变化）")
            
            return True
        else:
            print(f"❌ 向量生成失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    finally:
        # 关闭数据库连接
        if motor_client:
            motor_client.close()


async def test_vector_search():
    """测试向量搜索"""
    print("\n🔍 测试向量搜索...")
    print("=" * 50)
    
    try:
        # 初始化数据库
        await init_db()
        
        # 创建RAG服务
        rag_service = RAGService()
        
        # 测试数据
        from backend.models.message import Message
        from datetime import datetime
        
        test_persona_id = "test_persona_123"
        messages = [
            Message(
                persona_id=test_persona_id,
                sender="Alice",
                content="I love programming in Python",
                timestamp=datetime.now()
            ),
            Message(
                persona_id=test_persona_id,
                sender="Bob",
                content="Python is great for data science",
                timestamp=datetime.now()
            ),
            Message(
                persona_id=test_persona_id,
                sender="Alice",
                content="Let's go for a walk in the park",
                timestamp=datetime.now()
            )
        ]
        
        # 生成并存储向量
        print("存储测试消息...")
        texts = [m.content for m in messages]
        embeddings = await rag_service.generate_embeddings(texts)
        
        # 模拟存储（实际应该存到数据库）
        for msg, emb in zip(messages, embeddings):
            msg.embedding = emb
        
        # 测试搜索
        query = "Python programming"
        print(f"搜索查询: '{query}'")
        
        # 生成查询向量
        query_embedding = await rag_service.generate_embedding(query)
        
        # 计算相似度（简单的余弦相似度）
        def cosine_similarity(a: List[float], b: List[float]) -> float:
            dot_product = sum(x * y for x, y in zip(a, b))
            norm_a = sum(x * x for x in a) ** 0.5
            norm_b = sum(y * y for y in b) ** 0.5
            return dot_product / (norm_a * norm_b) if norm_a * norm_b > 0 else 0
        
        results = []
        for msg in messages:
            score = cosine_similarity(query_embedding, msg.embedding)
            results.append((msg, score))
        
        # 排序结果
        results.sort(key=lambda x: x[1], reverse=True)
        
        print("\n搜索结果:")
        for msg, score in results:
            print(f"   相似度 {score:.4f}: {msg.content}")
        
        # 检查结果质量
        if results[0][1] > results[-1][1]:
            print("\n✅ 向量搜索工作正常（相似度有差异）")
        else:
            print("\n⚠️  向量搜索可能使用Mock（相似度相同）")
        
        return True
        
    except Exception as e:
        print(f"❌ 搜索测试失败: {e}")
        return False
    finally:
        if motor_client:
            motor_client.close()


def show_configuration_guide():
    """显示配置指南"""
    print("\n📚 如何配置真实的向量服务:")
    print("=" * 50)
    print("""
1. 在.env文件中设置（如果还没有.env，复制.env.example）:
   
   # 关闭Mock模式
   USE_MOCK_EMBEDDINGS=false
   
   # Azure OpenAI配置
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_KEY=your-api-key
   AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002

2. 确保Azure OpenAI资源已部署embedding模型

3. 重启后端服务:
   ./stop_services.sh
   ./start_services.sh

4. 再次运行此脚本验证配置
""")


async def main():
    """主函数"""
    print("🚀 Second Self 向量服务检查工具")
    print("=" * 50)
    
    # 1. 检查当前配置
    is_mock = await check_current_config()
    
    # 2. 测试向量生成
    embedding_ok = await test_embedding_generation()
    
    # 3. 测试向量搜索
    if embedding_ok:
        search_ok = await test_vector_search()
    else:
        search_ok = False
    
    # 4. 总结和建议
    print("\n📊 检查结果:")
    print("=" * 50)
    
    if is_mock:
        print("❌ 当前使用Mock向量服务")
        print("   - 搜索功能受限")
        print("   - 建议配置真实的Azure OpenAI服务")
        show_configuration_guide()
    else:
        if embedding_ok and search_ok:
            print("✅ 向量服务工作正常！")
            print("   - Azure OpenAI配置正确")
            print("   - 向量生成和搜索功能正常")
        else:
            print("⚠️  Azure OpenAI配置可能有问题")
            print("   - 请检查API密钥和端点")
            print("   - 确保部署了embedding模型")
            show_configuration_guide()


if __name__ == "__main__":
    asyncio.run(main())