"""
基于RAG的人格模拟方案示例
无需GPU，使用API即可实现
"""

import json
from typing import List, Dict
from collections import Counter
import jieba

class PersonalityRAG:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.personality_profile = {}
        
    def analyze_personality(self, messages: List[Dict]) -> Dict:
        """分析聊天记录，提取人格特征"""
        
        # 1. 统计分析
        stats = {
            'total_messages': len(messages),
            'avg_message_length': sum(len(m['content']) for m in messages) / len(messages),
            'time_patterns': self._analyze_time_patterns(messages),
            'emoji_usage': self._analyze_emoji_usage(messages),
            'frequent_words': self._get_frequent_words(messages),
            'sentence_patterns': self._analyze_sentence_patterns(messages)
        }
        
        # 2. 语言风格特征
        style_features = {
            'formality': self._measure_formality(messages),
            'emotional_tone': self._analyze_emotion(messages),
            'topic_preferences': self._extract_topics(messages),
            'response_patterns': self._analyze_response_patterns(messages)
        }
        
        # 3. 构建人格画像
        self.personality_profile = {
            'statistics': stats,
            'style': style_features,
            'sample_messages': self._select_representative_messages(messages)
        }
        
        return self.personality_profile
    
    def _analyze_emoji_usage(self, messages: List[Dict]) -> Dict:
        """分析表情使用习惯"""
        emoji_counter = Counter()
        emoji_patterns = {
            '😊😄😃': 'positive',
            '😔😢😭': 'sad',
            '😡😠': 'angry',
            '❤️💕': 'love'
        }
        
        for msg in messages:
            # 统计emoji
            for char in msg['content']:
                if ord(char) > 127:  # 简单判断emoji
                    emoji_counter[char] += 1
        
        return {
            'top_emojis': emoji_counter.most_common(10),
            'emoji_frequency': len(emoji_counter) / len(messages)
        }
    
    def _get_frequent_words(self, messages: List[Dict]) -> List[str]:
        """提取高频词汇"""
        all_words = []
        stop_words = {'的', '了', '是', '我', '你', '在', '吗', '啊', '吧'}
        
        for msg in messages:
            words = jieba.lcut(msg['content'])
            all_words.extend([w for w in words if w not in stop_words and len(w) > 1])
        
        word_freq = Counter(all_words)
        return [word for word, freq in word_freq.most_common(50)]
    
    def _analyze_sentence_patterns(self, messages: List[Dict]) -> Dict:
        """分析句式特征"""
        patterns = {
            'question_ratio': 0,
            'exclamation_ratio': 0,
            'avg_sentence_length': 0,
            'common_starters': [],
            'common_endings': []
        }
        
        questions = sum(1 for m in messages if '？' in m['content'] or '?' in m['content'])
        exclamations = sum(1 for m in messages if '！' in m['content'] or '!' in m['content'])
        
        patterns['question_ratio'] = questions / len(messages)
        patterns['exclamation_ratio'] = exclamations / len(messages)
        
        # 提取常见开头和结尾
        starters = [m['content'][:3] for m in messages if len(m['content']) > 3]
        endings = [m['content'][-3:] for m in messages if len(m['content']) > 3]
        
        patterns['common_starters'] = Counter(starters).most_common(10)
        patterns['common_endings'] = Counter(endings).most_common(10)
        
        return patterns
    
    def generate_prompt(self, user_input: str, context: List[str] = None) -> str:
        """生成模拟人格的提示词"""
        profile = self.personality_profile
        
        prompt = f"""你需要模仿一个人的说话风格。

## 人格特征：
- 平均消息长度：{profile['statistics']['avg_message_length']:.0f}字
- 问句使用频率：{profile['style']['response_patterns']['question_ratio']:.2%}
- 感叹句频率：{profile['style']['response_patterns']['exclamation_ratio']:.2%}
- 常用词汇：{', '.join(profile['statistics']['frequent_words'][:20])}
- 常用表情：{', '.join([e[0] for e in profile['statistics']['emoji_usage']['top_emojis'][:5]])}

## 说话风格示例：
"""
        
        # 添加相关的历史对话示例
        for msg in profile['sample_messages'][:5]:
            prompt += f"- {msg['content']}\n"
        
        prompt += f"\n基于以上风格，回复用户消息：'{user_input}'"
        
        if context:
            prompt += f"\n最近对话上下文：{' '.join(context[-3:])}"
        
        return prompt
    
    def _select_representative_messages(self, messages: List[Dict]) -> List[Dict]:
        """选择有代表性的消息样本"""
        # 简化版：随机选择不同长度的消息
        short = [m for m in messages if 5 < len(m['content']) < 20]
        medium = [m for m in messages if 20 <= len(m['content']) < 50]
        long = [m for m in messages if len(m['content']) >= 50]
        
        samples = []
        if short: samples.extend(short[:5])
        if medium: samples.extend(medium[:5])
        if long: samples.extend(long[:5])
        
        return samples
    
    def _analyze_time_patterns(self, messages):
        """分析时间模式 - 简化实现"""
        return {'morning': 0.3, 'afternoon': 0.4, 'evening': 0.3}
    
    def _measure_formality(self, messages):
        """测量正式程度 - 简化实现"""
        return 0.5
    
    def _analyze_emotion(self, messages):
        """情绪分析 - 简化实现"""
        return {'positive': 0.6, 'neutral': 0.3, 'negative': 0.1}
    
    def _extract_topics(self, messages):
        """话题提取 - 简化实现"""
        return ['日常', '工作', '美食', '娱乐']
    
    def _analyze_response_patterns(self, messages):
        """回复模式分析"""
        return {
            'question_ratio': 0.3,
            'exclamation_ratio': 0.2,
            'avg_response_time': 120  # 秒
        }

# 使用示例
if __name__ == "__main__":
    # 初始化
    rag = PersonalityRAG(api_key="your-api-key")
    
    # 假设已经解析了聊天记录
    chat_messages = [
        {'content': '哈哈哈哈今天好开心啊！', 'time': '2024-01-01 10:00'},
        {'content': '你在干嘛呢？', 'time': '2024-01-01 10:01'},
        {'content': '刚刚看了个超搞笑的视频😂', 'time': '2024-01-01 10:02'},
        # ... 更多消息
    ]
    
    # 分析人格
    profile = rag.analyze_personality(chat_messages)
    
    # 生成回复
    user_msg = "今天天气真好"
    prompt = rag.generate_prompt(user_msg)
    
    print("生成的提示词：")
    print(prompt)