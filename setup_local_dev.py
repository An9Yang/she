"""
本地开发环境设置脚本
"""

import os
import sys
from pathlib import Path

def setup_local_mongodb():
    """设置本地MongoDB（开发用）"""
    print("🗄️ 配置本地开发环境...\n")
    
    # 检查是否已有.env文件
    env_file = "backend/.env"
    if not os.path.exists(env_file):
        print("❌ 未找到 backend/.env 文件")
        return
    
    print("📝 当前MongoDB配置选项：\n")
    print("1. 使用本地MongoDB (localhost)")
    print("2. 等待MongoDB Atlas配置完成")
    print("3. 使用内存数据库（仅测试用）")
    
    choice = input("\n请选择 (1/2/3): ").strip()
    
    if choice == "1":
        print("\n✅ 使用本地MongoDB配置")
        print("确保MongoDB正在运行：")
        print("  - macOS: brew services start mongodb-community")
        print("  - Linux: sudo systemctl start mongod")
        print("  - Windows: net start MongoDB")
        print("\n当前配置已设置为: mongodb://localhost:27017/second_self_test")
        
    elif choice == "2":
        print("\n📋 MongoDB Atlas配置步骤：")
        print("1. 访问 https://cloud.mongodb.com")
        print("2. 创建免费集群")
        print("3. 设置数据库用户")
        print("4. 配置网络访问（添加你的IP）")
        print("5. 获取连接字符串")
        print("6. 更新 backend/.env 中的 MONGODB_URL")
        print("\n连接字符串格式：")
        print("mongodb+srv://<username>:<password>@<cluster>.mongodb.net/second_self?retryWrites=true&w=majority")
        
    elif choice == "3":
        print("\n⚠️  使用内存数据库（数据不会持久化）")
        # 创建一个使用内存存储的配置
        with open("backend/.env.inmemory", "w") as f:
            f.write("""# 内存数据库配置（仅开发测试用）
USE_INMEMORY_DB=true
MONGODB_URL=mongodb://localhost:27017/second_self_test
DATABASE_NAME=second_self_test
""")
        print("✅ 已创建内存数据库配置")
        print("注意：重启应用后数据将丢失")


def check_dependencies():
    """检查依赖安装情况"""
    print("\n🔍 检查依赖安装...\n")
    
    required_packages = {
        "fastapi": "FastAPI Web框架",
        "motor": "MongoDB异步驱动",
        "beanie": "MongoDB ODM",
        "openai": "OpenAI SDK",
        "jose": "JWT认证",
        "passlib": "密码加密"
    }
    
    missing = []
    for package, desc in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {desc} ({package})")
        except ImportError:
            print(f"❌ {desc} ({package})")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  缺少 {len(missing)} 个依赖包")
        print("请运行: ./install_dependencies.sh")
        return False
    
    print("\n✅ 所有依赖已安装")
    return True


def create_test_user_guide():
    """创建测试用户指南"""
    guide = """
# 🚀 Second Self 快速测试指南

## 1. 启动应用

### 后端（终端1）:
```bash
source venv/bin/activate  # Windows: venv\\Scripts\\activate
cd backend
python -m uvicorn main:app --reload
```

### 前端（终端2）:
```bash
cd frontend
npm run dev
```

## 2. 测试流程

### 步骤1: 注册账号
- 访问 http://localhost:3000
- 点击"立即开始"或"注册"
- 填写信息（可以使用假邮箱如 test@example.com）

### 步骤2: 上传测试数据
- 使用提供的测试文件：`test_data/sample_chat.json`
- 或创建自己的JSON文件：
```json
{
  "messages": [
    {"timestamp": "2024-01-01 10:00:00", "sender": "朋友", "content": "早上好！"},
    {"timestamp": "2024-01-01 10:01:00", "sender": "我", "content": "早上好呀～"},
    {"timestamp": "2024-01-01 10:02:00", "sender": "朋友", "content": "今天有什么计划吗？"},
    {"timestamp": "2024-01-01 10:03:00", "sender": "我", "content": "准备去图书馆学习"}
  ]
}
```

### 步骤3: 开始对话
- 等待处理完成（状态变为"可用"）
- 点击"开始对话"
- 输入消息，AI会模拟对方的风格回复

## 3. 常见问题

### MongoDB连接失败
- 确保MongoDB正在运行
- 或使用MongoDB Atlas云服务
- 检查防火墙设置

### Azure OpenAI错误
- 检查API密钥是否正确
- 确认部署名称（当前配置为"o3"）
- 检查网络连接

### 前端无法连接后端
- 确保后端运行在 http://localhost:8000
- 检查CORS配置
- 查看浏览器控制台错误

## 4. 测试账号（如果需要）
- 邮箱: demo@example.com
- 密码: demo123456

祝测试愉快！🎉
"""
    
    with open("QUICK_START.md", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("\n📖 已创建快速开始指南: QUICK_START.md")


def create_sample_data():
    """创建示例测试数据"""
    print("\n📄 创建测试数据...\n")
    
    os.makedirs("test_data", exist_ok=True)
    
    # 创建示例聊天记录
    sample_chat = {
        "messages": [
            {"timestamp": "2024-01-01 10:00:00", "sender": "小明", "content": "早上好！今天天气真不错"},
            {"timestamp": "2024-01-01 10:01:00", "sender": "我", "content": "是啊，阳光明媚的"},
            {"timestamp": "2024-01-01 10:02:00", "sender": "小明", "content": "要不要一起去公园走走？"},
            {"timestamp": "2024-01-01 10:03:00", "sender": "我", "content": "好主意！几点出发？"},
            {"timestamp": "2024-01-01 10:04:00", "sender": "小明", "content": "下午3点怎么样？"},
            {"timestamp": "2024-01-01 10:05:00", "sender": "我", "content": "可以，到时候见！"},
            {"timestamp": "2024-01-01 15:00:00", "sender": "小明", "content": "我到了，你在哪里？"},
            {"timestamp": "2024-01-01 15:02:00", "sender": "我", "content": "马上到，在路上了"},
            {"timestamp": "2024-01-01 15:10:00", "sender": "小明", "content": "看到你了！"},
            {"timestamp": "2024-01-01 17:30:00", "sender": "小明", "content": "今天玩得真开心，下次再约"},
            {"timestamp": "2024-01-01 17:31:00", "sender": "我", "content": "嗯嗯，下次见！"}
        ]
    }
    
    import json
    with open("test_data/sample_chat.json", "w", encoding="utf-8") as f:
        json.dump(sample_chat, f, ensure_ascii=False, indent=2)
    
    print("✅ 创建示例聊天记录: test_data/sample_chat.json")
    
    # 创建WhatsApp格式示例
    whatsapp_sample = """[2024/1/1, 14:30:00] 小王: 周末有空吗？
[2024/1/1, 14:32:00] 小李: 有啊，怎么了？
[2024/1/1, 14:33:00] 小王: 想约你看电影
[2024/1/1, 14:35:00] 小李: 好啊，看什么电影？
[2024/1/1, 14:36:00] 小王: 最新的科幻片怎么样？
[2024/1/1, 14:37:00] 小李: 可以，几点的场次？
[2024/1/1, 14:38:00] 小王: 晚上7点吧
[2024/1/1, 14:39:00] 小李: OK，到时候见！"""
    
    with open("test_data/whatsapp_chat.txt", "w", encoding="utf-8") as f:
        f.write(whatsapp_sample)
    
    print("✅ 创建WhatsApp格式示例: test_data/whatsapp_chat.txt")


if __name__ == "__main__":
    print("=" * 60)
    print("🛠️  Second Self 本地开发环境设置")
    print("=" * 60)
    
    # 检查依赖
    deps_ok = check_dependencies()
    
    # MongoDB配置
    setup_local_mongodb()
    
    # 创建测试数据
    create_sample_data()
    
    # 创建快速开始指南
    create_test_user_guide()
    
    print("\n" + "=" * 60)
    print("\n✅ 设置完成！")
    
    if deps_ok:
        print("\n下一步：")
        print("1. 测试Azure OpenAI连接: python test_azure_openai.py")
        print("2. 启动项目: 查看 QUICK_START.md")
    else:
        print("\n请先安装依赖: ./install_dependencies.sh")