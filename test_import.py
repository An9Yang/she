"""
测试数据导入功能的独立脚本
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
import sys
sys.path.append(str(Path(__file__).parent))

from backend.services.data_processor import DataProcessorService
from backend.core.database import init_db, close_db


async def test_data_import():
    """测试数据导入"""
    print("🧪 开始测试数据导入功能...\n")
    
    # 初始化数据库
    print("📊 初始化数据库连接...")
    await init_db()
    
    # 创建处理器
    processor = DataProcessorService()
    
    # 测试编码检测
    print("\n1️⃣ 测试编码检测")
    test_file = Path(__file__).parent / "tests" / "test_data" / "test_chat.json"
    if test_file.exists():
        encoding = processor._detect_encoding(str(test_file))
        print(f"✅ 检测到编码: {encoding}")
    
    # 测试时间戳解析
    print("\n2️⃣ 测试时间戳解析")
    test_timestamps = [
        '2024/1/1, 10:30:45',
        '2024-01-01 10:30:45',
        '2024年1月1日 10:30:45'
    ]
    for ts in test_timestamps:
        parsed = processor._parse_timestamp(ts)
        print(f"✅ '{ts}' -> {parsed}")
    
    # 测试消息清洗
    print("\n3️⃣ 测试消息清洗")
    raw_messages = [
        {'content': '  Hello  ', 'sender': 'Alice'},
        {'content': '', 'sender': 'Bob'},
        {'content': 'Valid message', 'sender': 'Alice'},
    ]
    cleaned = processor._clean_messages(raw_messages)
    print(f"✅ 清洗前: {len(raw_messages)} 条, 清洗后: {len(cleaned)} 条")
    
    # 测试JSON解析
    print("\n4️⃣ 测试JSON文件解析")
    if test_file.exists():
        messages = await processor._parse_json_chat(str(test_file))
        print(f"✅ 解析出 {len(messages)} 条消息")
        if messages:
            print(f"   第一条: {messages[0]['sender']}: {messages[0]['content']}")
    
    # 测试人格分析
    print("\n5️⃣ 测试人格信息分析")
    test_messages = [
        {'content': 'Hi', 'sender': 'User'},
        {'content': 'Hello', 'sender': 'Alice'},
        {'content': 'How are you?', 'sender': 'User'},
        {'content': 'I am fine', 'sender': 'Alice'},
    ]
    info = processor._analyze_persona_info(test_messages)
    print(f"✅ 识别出人格: {info['name']}")
    
    # 关闭数据库
    await close_db()
    
    print("\n✨ 所有测试完成!")


async def test_full_import():
    """测试完整的导入流程"""
    print("\n🚀 测试完整导入流程...\n")
    
    # 初始化数据库
    await init_db()
    
    # 创建测试文件
    test_data = {
        'messages': [
            {'timestamp': '2024-01-01 10:00:00', 'sender': '小明', 'content': '早上好！'},
            {'timestamp': '2024-01-01 10:01:00', 'sender': '小红', 'content': '早上好呀～今天天气真不错'},
            {'timestamp': '2024-01-01 10:02:00', 'sender': '小明', 'content': '是啊，要不要一起去公园走走？'},
            {'timestamp': '2024-01-01 10:03:00', 'sender': '小红', 'content': '好啊好啊！几点见面呢？'},
        ]
    }
    
    import json
    import tempfile
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f, ensure_ascii=False)
        temp_file = f.name
    
    # 处理文件
    processor = DataProcessorService()
    result = await processor.process_chat_data(
        file_path=temp_file,
        user_id="507f1f77bcf86cd799439011",  # 测试用户ID
        task_id="test_task_001"
    )
    
    print(f"处理结果: {result}")
    
    # 清理
    os.unlink(temp_file)
    await close_db()


if __name__ == "__main__":
    # 先创建测试数据
    from tests.test_data_processor import create_test_data
    create_test_data()
    
    # 运行测试
    asyncio.run(test_data_import())
    
    # 如果有MongoDB连接，可以测试完整流程
    # asyncio.run(test_full_import())