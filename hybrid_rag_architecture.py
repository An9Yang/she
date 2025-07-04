"""
Hybrid RAG 架构实现
专门针对人格模拟场景优化
"""

from typing import List, Dict, Tuple
import numpy as np
from dataclasses import dataclass
from enum import Enum

class RetrievalStrategy(Enum):
    SEMANTIC = "semantic"          # 语义相似
    KEYWORD = "keyword"            # 关键词匹配
    TEMPORAL = "temporal"          # 时间相关
    EMOTIONAL = "emotional"        # 情绪相似
    CONVERSATIONAL = "conversational"  # 对话模式

@dataclass
class Message:
    content: str
    timestamp: str
    sender: str
    context: List[str]  # 前几条消息
    emotion: str        # 情绪标签
    topic: str          # 话题标签

class HybridRAGPersonality:
    """
    混合RAG系统，专门用于人格模拟
    """
    
    def __init__(self):
        self.vector_store = None  # 向量数据库
        self.keyword_index = {}   # 关键词索引
        self.pattern_bank = {}    # 对话模式库
        self.style_profile = {}   # 风格特征
        
    def build_index(self, chat_history: List[Message]):
        """构建多维度索引"""
        
        # 1. 向量索引 - 语义相似度
        self._build_semantic_index(chat_history)
        
        # 2. 关键词索引 - 快速匹配口头禅
        self._build_keyword_index(chat_history)
        
        # 3. 对话模式索引 - 问答模式
        self._build_pattern_index(chat_history)
        
        # 4. 情绪索引 - 情绪响应模式
        self._build_emotion_index(chat_history)
        
        # 5. 时序索引 - 对话节奏
        self._build_temporal_index(chat_history)
    
    def retrieve(self, query: str, context: List[str] = None) -> List[Message]:
        """
        混合检索策略
        """
        candidates = []
        
        # 1. 语义检索 - 找相似话题 (权重 40%)
        semantic_results = self._semantic_search(query, top_k=20)
        candidates.extend([(msg, 0.4, 'semantic') for msg in semantic_results])
        
        # 2. 关键词检索 - 匹配特定用语 (权重 20%)
        keyword_results = self._keyword_search(query, top_k=10)
        candidates.extend([(msg, 0.2, 'keyword') for msg in keyword_results])
        
        # 3. 对话模式检索 - 匹配问答模式 (权重 20%)
        if self._is_question(query):
            pattern_results = self._pattern_search('question_response', top_k=10)
            candidates.extend([(msg, 0.2, 'pattern') for msg in pattern_results])
        
        # 4. 情绪匹配 - 情绪一致性 (权重 10%)
        emotion = self._detect_emotion(query)
        emotion_results = self._emotion_search(emotion, top_k=5)
        candidates.extend([(msg, 0.1, 'emotion') for msg in emotion_results])
        
        # 5. 上下文连贯 - 考虑对话流程 (权重 10%)
        if context:
            context_results = self._context_search(context, top_k=5)
            candidates.extend([(msg, 0.1, 'context') for msg in context_results])
        
        # 重排序和去重
        return self._rerank_and_dedupe(candidates)
    
    def generate_response(self, query: str, retrieved_messages: List[Message]) -> str:
        """
        基于检索结果生成回复
        """
        # 1. 提取风格特征
        style_features = self._extract_style_features(retrieved_messages)
        
        # 2. 构建少样本示例
        few_shot_examples = self._select_diverse_examples(retrieved_messages, n=5)
        
        # 3. 生成提示词
        prompt = self._build_generation_prompt(
            query=query,
            style=style_features,
            examples=few_shot_examples,
            personality=self.style_profile
        )
        
        # 4. 调用LLM生成
        response = self._call_llm(prompt)
        
        # 5. 后处理 - 确保风格一致
        return self._post_process(response, style_features)
    
    def _build_semantic_index(self, messages: List[Message]):
        """构建语义向量索引"""
        # 使用 sentence-transformers 或 OpenAI embeddings
        pass
    
    def _build_keyword_index(self, messages: List[Message]):
        """构建关键词倒排索引"""
        for msg in messages:
            # 提取关键词和口头禅
            keywords = self._extract_keywords(msg.content)
            for keyword in keywords:
                if keyword not in self.keyword_index:
                    self.keyword_index[keyword] = []
                self.keyword_index[keyword].append(msg)
    
    def _build_pattern_index(self, messages: List[Message]):
        """构建对话模式索引"""
        patterns = {
            'greeting': [],           # 打招呼
            'question_response': [],  # 问答
            'emotion_expression': [], # 情绪表达
            'topic_transition': [],   # 话题转换
            'goodbye': []            # 告别
        }
        
        for i, msg in enumerate(messages):
            pattern_type = self._classify_pattern(msg, messages[i-1] if i > 0 else None)
            patterns[pattern_type].append(msg)
        
        self.pattern_bank = patterns
    
    def _extract_style_features(self, messages: List[Message]) -> Dict:
        """提取风格特征"""
        return {
            'avg_length': np.mean([len(m.content) for m in messages]),
            'emoji_usage': self._calculate_emoji_ratio(messages),
            'punctuation_style': self._analyze_punctuation(messages),
            'sentence_endings': self._common_endings(messages),
            'response_delay': self._avg_response_time(messages)
        }
    
    def _build_generation_prompt(self, query, style, examples, personality):
        """构建生成提示词"""
        prompt = f"""你需要模仿一个特定的人进行对话。

## 人格特征
- 平均消息长度: {style['avg_length']:.0f}字
- 表情使用频率: {style['emoji_usage']:.2%}
- 标点风格: {style['punctuation_style']}
- 常见句尾: {', '.join(style['sentence_endings'])}

## 对话示例
"""
        for ex in examples:
            prompt += f"用户: {ex.context[-1] if ex.context else '(开始对话)'}\n"
            prompt += f"回复: {ex.content}\n\n"
        
        prompt += f"""## 当前对话
用户: {query}
请用上述风格回复，保持人格一致性。不要解释，直接回复。"""
        
        return prompt
    
    def _rerank_and_dedupe(self, candidates: List[Tuple[Message, float, str]]) -> List[Message]:
        """重排序和去重"""
        # 按综合得分排序
        seen = set()
        results = []
        
        # 计算综合得分
        message_scores = {}
        for msg, weight, source in candidates:
            if msg.content not in message_scores:
                message_scores[msg.content] = {
                    'message': msg,
                    'score': 0,
                    'sources': []
                }
            message_scores[msg.content]['score'] += weight
            message_scores[msg.content]['sources'].append(source)
        
        # 排序并返回
        sorted_messages = sorted(
            message_scores.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )
        
        return [item['message'] for item in sorted_messages[:10]]
    
    # 辅助方法
    def _is_question(self, text: str) -> bool:
        question_markers = ['？', '?', '吗', '呢', '么', '哪', '什么', '怎么', '为什么']
        return any(marker in text for marker in question_markers)
    
    def _detect_emotion(self, text: str) -> str:
        # 简化的情绪检测
        if any(word in text for word in ['开心', '高兴', '哈哈', '😊', '😄']):
            return 'positive'
        elif any(word in text for word in ['难过', '伤心', '唉', '😔', '😢']):
            return 'negative'
        return 'neutral'
    
    def _extract_keywords(self, text: str) -> List[str]:
        # 提取关键词和口头禅
        import jieba
        words = jieba.lcut(text)
        # 过滤停用词，保留特征词
        return [w for w in words if len(w) > 1]

# 使用示例
if __name__ == "__main__":
    # 初始化系统
    rag_system = HybridRAGPersonality()
    
    # 构建索引
    chat_history = [
        Message(
            content="哈哈哈哈太搞笑了",
            timestamp="2024-01-01 10:00",
            sender="friend",
            context=["分享了一个视频"],
            emotion="positive",
            topic="entertainment"
        ),
        # ... 更多历史消息
    ]
    
    rag_system.build_index(chat_history)
    
    # 生成回复
    user_query = "今天好累啊"
    retrieved = rag_system.retrieve(user_query, context=["刚下班"])
    response = rag_system.generate_response(user_query, retrieved)
    
    print(f"模拟回复: {response}")