#!/usr/bin/env python3
"""
测试向量（embeddings）功能
"""
import asyncio
import sys
from pathlib import Path
import os

# 添加项目路径
sys.path.append(str(Path(__file__).parent / "backend"))

async def test_embeddings():
    """测试向量生成功能"""
    print("🧪 测试向量（Embeddings）功能")
    print("=" * 50)
    
    # 导入RAG服务
    from backend.services.rag_service import RAGService
    
    # 测试文本
    test_texts = [
        "你好，我是测试用户",
        "今天天气真好",
        "Hello world, this is a test"
    ]
    
    # 检查配置
    use_mock = os.getenv("USE_MOCK_EMBEDDINGS", "true").lower() == "true"
    print(f"USE_MOCK_EMBEDDINGS: {use_mock}")
    
    if not use_mock:
        print("✅ 使用真实的Azure OpenAI embeddings")
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "")
        print(f"   Endpoint: {endpoint[:50]}...")
        print(f"   Deployment: {deployment}")
    else:
        print("⚠️  使用Mock embeddings")
    
    print("\n测试向量生成:")
    
    # 初始化RAG服务
    rag_service = RAGService()
    
    # 测试每个文本
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. 文本: '{text}'")
        try:
            # 生成向量
            embedding = await rag_service.generate_embedding(text)
            
            # 显示结果
            print(f"   向量长度: {len(embedding)}")
            print(f"   前5个值: {embedding[:5]}")
            print(f"   类型: {type(embedding[0])}")
            
            # 验证向量质量
            if use_mock:
                # Mock向量应该基于文本长度
                expected_first = len(text) / 100.0
                if abs(embedding[0] - expected_first) < 0.01:
                    print("   ✅ Mock向量生成正确")
                else:
                    print("   ❌ Mock向量生成错误")
            else:
                # 真实向量应该是归一化的
                import numpy as np
                norm = np.linalg.norm(embedding)
                print(f"   向量范数: {norm:.4f}")
                if 0.9 < norm < 1.1:
                    print("   ✅ 向量已归一化")
                else:
                    print("   ⚠️  向量未归一化")
                    
        except Exception as e:
            print(f"   ❌ 错误: {type(e).__name__}: {str(e)}")
    
    # 测试相似度计算
    if len(test_texts) >= 2:
        print("\n\n测试相似度计算:")
        try:
            emb1 = await rag_service.generate_embedding(test_texts[0])
            emb2 = await rag_service.generate_embedding(test_texts[1])
            
            # 计算余弦相似度
            import numpy as np
            similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
            
            print(f"文本1: '{test_texts[0]}'")
            print(f"文本2: '{test_texts[1]}'")
            print(f"余弦相似度: {similarity:.4f}")
            
            if not use_mock:
                print("\n✅ Azure OpenAI Embeddings 功能正常！")
            else:
                print("\n⚠️  当前使用Mock实现，建议配置真实的embedding服务")
                
        except Exception as e:
            print(f"❌ 相似度计算失败: {e}")
    
    print("\n" + "=" * 50)
    print("测试完成！")

async def main():
    """主函数"""
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv("backend/.env")
    
    # 初始化数据库（需要用于RAG服务）
    from backend.core.database import init_db, close_db
    await init_db()
    
    try:
        await test_embeddings()
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())