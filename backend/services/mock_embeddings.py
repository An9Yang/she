"""
模拟embeddings服务 - 用于测试
"""

import random
from typing import List

class MockEmbeddingService:
    """模拟向量服务"""
    
    @staticmethod
    def generate_embedding(text: str) -> List[float]:
        """生成模拟向量"""
        # 生成1536维的随机向量（与ada-002相同维度）
        random.seed(hash(text))  # 相同文本生成相同向量
        return [random.random() for _ in range(1536)]
    
    @staticmethod
    def generate_embeddings(texts: List[str]) -> List[List[float]]:
        """批量生成模拟向量"""
        return [MockEmbeddingService.generate_embedding(text) for text in texts]