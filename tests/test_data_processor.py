"""
数据处理服务测试
"""

import os
import json
import tempfile
from datetime import datetime
import pytest
from pathlib import Path

from backend.services.data_processor import DataProcessorService
from backend.models.persona import Persona, PersonaStatus
from backend.models.message import Message


class TestDataProcessor:
    """数据处理器测试类"""
    
    @pytest.fixture
    def processor(self):
        """创建处理器实例"""
        return DataProcessorService()
    
    @pytest.fixture
    def sample_user_id(self):
        """示例用户ID"""
        return "507f1f77bcf86cd799439011"
    
    def test_detect_encoding(self, processor):
        """测试编码检测"""
        # 创建UTF-8测试文件
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', delete=False) as f:
            f.write("测试中文内容")
            temp_file = f.name
        
        encoding = processor._detect_encoding(temp_file)
        assert encoding.lower() in ['utf-8', 'utf8']
        
        os.unlink(temp_file)
    
    def test_parse_timestamp(self, processor):
        """测试时间戳解析"""
        test_cases = [
            ('2024/1/1, 10:30:45', datetime(2024, 1, 1, 10, 30, 45)),
            ('2024-01-01 10:30:45', datetime(2024, 1, 1, 10, 30, 45)),
        ]
        
        for timestamp_str, expected in test_cases:
            result = processor._parse_timestamp(timestamp_str)
            assert result == expected
    
    def test_clean_messages(self, processor):
        """测试消息清洗"""
        raw_messages = [
            {'content': '  Hello  ', 'sender': 'Alice', 'timestamp': datetime.now()},
            {'content': '', 'sender': 'Bob', 'timestamp': datetime.now()},
            {'content': 'System message', 'sender': 'system', 'timestamp': datetime.now()},
            {'content': 'Valid message', 'sender': 'Alice', 'timestamp': datetime.now()},
        ]
        
        cleaned = processor._clean_messages(raw_messages)
        
        assert len(cleaned) == 2
        assert cleaned[0]['content'] == 'Hello'
        assert cleaned[1]['content'] == 'Valid message'
    
    def test_analyze_persona_info(self, processor):
        """测试人格信息分析"""
        messages = [
            {'content': 'Hi', 'sender': 'User', 'timestamp': datetime(2024, 1, 1)},
            {'content': 'Hello', 'sender': 'Alice', 'timestamp': datetime(2024, 1, 2)},
            {'content': 'How are you?', 'sender': 'User', 'timestamp': datetime(2024, 1, 3)},
            {'content': 'I am fine', 'sender': 'Alice', 'timestamp': datetime(2024, 1, 4)},
        ]
        
        info = processor._analyze_persona_info(messages)
        
        assert info['name'] == 'Alice'
        assert info['date_range_start'] == datetime(2024, 1, 1)
        assert info['date_range_end'] == datetime(2024, 1, 4)
    
    @pytest.mark.asyncio
    async def test_parse_json_chat(self, processor):
        """测试JSON聊天记录解析"""
        test_data = {
            'messages': [
                {
                    'timestamp': '2024-01-01 10:00:00',
                    'sender': 'Alice',
                    'content': 'Hello'
                },
                {
                    'timestamp': '2024-01-01 10:01:00',
                    'sender': 'Bob',
                    'content': 'Hi there'
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_file = f.name
        
        messages = await processor._parse_json_chat(temp_file)
        
        assert len(messages) == 2
        assert messages[0]['sender'] == 'Alice'
        assert messages[0]['content'] == 'Hello'
        
        os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_parse_txt_chat_whatsapp(self, processor):
        """测试WhatsApp格式TXT解析"""
        whatsapp_content = """[2024/1/1, 10:30:45] Alice: Hello
[2024/1/1, 10:31:00] Bob: Hi Alice!
[2024/1/1, 10:31:30] Alice: How are you?"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(whatsapp_content)
            temp_file = f.name
        
        messages = await processor._parse_txt_chat(temp_file)
        
        assert len(messages) == 3
        assert messages[0]['sender'] == 'Alice'
        assert messages[0]['content'] == 'Hello'
        assert messages[1]['sender'] == 'Bob'
        
        os.unlink(temp_file)


# 创建测试数据文件
def create_test_data():
    """创建测试数据文件"""
    test_dir = Path(__file__).parent / 'test_data'
    test_dir.mkdir(exist_ok=True)
    
    # 创建JSON测试文件
    json_data = {
        'messages': [
            {
                'timestamp': '2024-01-01 10:00:00',
                'sender': '小明',
                'content': '你好啊'
            },
            {
                'timestamp': '2024-01-01 10:01:00',
                'sender': '小红',
                'content': '嗨，最近怎么样？'
            },
            {
                'timestamp': '2024-01-01 10:02:00',
                'sender': '小明',
                'content': '挺好的，刚下班'
            }
        ]
    }
    
    with open(test_dir / 'test_chat.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)
    
    # 创建WhatsApp格式测试文件
    whatsapp_data = """[2024/1/1, 14:30:00] 小王: 周末有空吗？
[2024/1/1, 14:32:00] 小李: 有啊，怎么了？
[2024/1/1, 14:33:00] 小王: 一起去爬山吧
[2024/1/1, 14:35:00] 小李: 好啊，几点出发？"""
    
    with open(test_dir / 'test_whatsapp.txt', 'w', encoding='utf-8') as f:
        f.write(whatsapp_data)
    
    print(f"测试数据已创建在: {test_dir}")


if __name__ == '__main__':
    # 运行测试
    create_test_data()
    pytest.main([__file__, '-v'])