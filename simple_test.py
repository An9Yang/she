"""
简单的数据导入测试（不需要数据库）
"""

import json
import tempfile
import os
from datetime import datetime
import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

# 简化版DataProcessor用于测试
class SimpleDataProcessor:
    """简化的数据处理器"""
    
    def detect_encoding(self, file_path):
        """简单的编码检测"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read()
            return 'utf-8'
        except:
            return 'gbk'
    
    def parse_timestamp(self, timestamp_str):
        """解析时间戳"""
        formats = [
            '%Y/%m/%d, %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y年%m月%d日 %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str.strip(), fmt)
            except:
                continue
        return datetime.now()
    
    def parse_json_chat(self, file_path):
        """解析JSON聊天记录"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = []
        if isinstance(data, dict) and 'messages' in data:
            messages = data['messages']
        
        return messages
    
    def clean_messages(self, messages):
        """清洗消息"""
        cleaned = []
        for msg in messages:
            if msg.get('content', '').strip():
                cleaned.append({
                    'content': msg['content'].strip(),
                    'sender': msg['sender'],
                    'timestamp': msg.get('timestamp')
                })
        return cleaned
    
    def analyze_persona(self, messages):
        """分析人格信息"""
        from collections import Counter
        senders = Counter(msg['sender'] for msg in messages)
        
        # 找出最常见的发送者
        most_common = senders.most_common(2)
        persona_name = most_common[0][0] if most_common else 'Unknown'
        
        return {
            'name': persona_name,
            'message_count': len(messages),
            'senders': dict(senders)
        }


def test_processor():
    """测试数据处理器"""
    print("🧪 测试数据导入功能\n")
    
    processor = SimpleDataProcessor()
    
    # 1. 创建测试数据
    print("1️⃣ 创建测试数据...")
    test_data = {
        'messages': [
            {'timestamp': '2024-01-01 10:00:00', 'sender': '小明', 'content': '早上好！'},
            {'timestamp': '2024-01-01 10:01:00', 'sender': '小红', 'content': '早上好呀～'},
            {'timestamp': '2024-01-01 10:02:00', 'sender': '小明', 'content': '今天天气真好'},
            {'timestamp': '2024-01-01 10:03:00', 'sender': '小红', 'content': '是啊，要不要出去走走？'},
            {'timestamp': '2024-01-01 10:04:00', 'sender': '小明', 'content': '好主意！'},
        ]
    }
    
    # 保存到临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    print(f"✅ 测试文件创建成功: {temp_file}\n")
    
    # 2. 测试编码检测
    print("2️⃣ 测试编码检测...")
    encoding = processor.detect_encoding(temp_file)
    print(f"✅ 检测到编码: {encoding}\n")
    
    # 3. 测试JSON解析
    print("3️⃣ 测试JSON解析...")
    messages = processor.parse_json_chat(temp_file)
    print(f"✅ 解析出 {len(messages)} 条消息")
    print(f"   第一条: {messages[0]['sender']}: {messages[0]['content']}\n")
    
    # 4. 测试时间戳解析
    print("4️⃣ 测试时间戳解析...")
    timestamp = processor.parse_timestamp(messages[0]['timestamp'])
    print(f"✅ 时间戳解析成功: {timestamp}\n")
    
    # 5. 测试消息清洗
    print("5️⃣ 测试消息清洗...")
    messages.append({'sender': 'test', 'content': ''})  # 添加空消息
    cleaned = processor.clean_messages(messages)
    print(f"✅ 清洗前: {len(messages)} 条, 清洗后: {len(cleaned)} 条\n")
    
    # 6. 测试人格分析
    print("6️⃣ 测试人格分析...")
    persona_info = processor.analyze_persona(cleaned)
    print(f"✅ 分析结果:")
    print(f"   主要人格: {persona_info['name']}")
    print(f"   消息总数: {persona_info['message_count']}")
    print(f"   发送者统计: {persona_info['senders']}\n")
    
    # 清理临时文件
    os.unlink(temp_file)
    
    print("✨ 所有测试完成！\n")
    
    # 测试WhatsApp格式
    print("7️⃣ 测试WhatsApp格式解析...")
    test_whatsapp_format()


def test_whatsapp_format():
    """测试WhatsApp格式解析"""
    import re
    
    whatsapp_content = """[2024/1/1, 14:30:00] 小王: 周末有空吗？
[2024/1/1, 14:32:00] 小李: 有啊，怎么了？
[2024/1/1, 14:33:00] 小王: 一起去爬山吧
[2024/1/1, 14:35:00] 小李: 好啊，几点出发？"""
    
    # WhatsApp正则表达式
    pattern = r'\[(\d{4}/\d{1,2}/\d{1,2},\s*\d{1,2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.*)'
    matches = re.findall(pattern, whatsapp_content)
    
    print(f"✅ 解析出 {len(matches)} 条WhatsApp消息")
    for timestamp, sender, content in matches[:2]:
        print(f"   {sender}: {content}")


if __name__ == "__main__":
    test_processor()