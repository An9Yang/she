"""
快速设置脚本（非交互式）
"""

import os
import json
from pathlib import Path

print("=" * 60)
print("🚀 Second Self 快速设置")
print("=" * 60)

# 1. 创建测试数据
print("\n📄 创建测试数据...")
os.makedirs("test_data", exist_ok=True)

sample_chat = {
    "messages": [
        {"timestamp": "2024-01-01 10:00:00", "sender": "小明", "content": "早上好！今天天气真不错"},
        {"timestamp": "2024-01-01 10:01:00", "sender": "我", "content": "是啊，阳光明媚的"},
        {"timestamp": "2024-01-01 10:02:00", "sender": "小明", "content": "要不要一起去公园走走？"},
        {"timestamp": "2024-01-01 10:03:00", "sender": "我", "content": "好主意！几点出发？"},
        {"timestamp": "2024-01-01 10:04:00", "sender": "小明", "content": "下午3点怎么样？"},
        {"timestamp": "2024-01-01 10:05:00", "sender": "我", "content": "可以，到时候见！"},
    ]
}

with open("test_data/sample_chat.json", "w", encoding="utf-8") as f:
    json.dump(sample_chat, f, ensure_ascii=False, indent=2)

print("✅ 创建测试聊天记录: test_data/sample_chat.json")

# 2. 显示当前配置
print("\n📋 当前配置：")
print("- Azure OpenAI: 已配置 (o3模型)")
print("- MongoDB: 等待Atlas配置 (当前使用本地)")
print("- 前端: http://localhost:3000")
print("- 后端: http://localhost:8000")

# 3. 显示启动步骤
print("\n🚀 启动步骤：")
print("\n1️⃣ 安装依赖（如果还没安装）：")
print("   ./install_dependencies.sh")

print("\n2️⃣ 启动后端（终端1）：")
print("   source venv/bin/activate")
print("   cd backend")
print("   python -m uvicorn main:app --reload")

print("\n3️⃣ 启动前端（终端2）：")
print("   cd frontend")
print("   npm run dev")

print("\n4️⃣ 访问应用：")
print("   打开浏览器访问 http://localhost:3000")

# 4. MongoDB Atlas提醒
print("\n⚠️  MongoDB Atlas配置提醒：")
print("配置完成后，更新 backend/.env 中的 MONGODB_URL")
print("格式: mongodb+srv://username:password@cluster.mongodb.net/second_self")

print("\n✨ 设置完成！可以开始使用了。")
print("=" * 60)