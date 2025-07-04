"""
项目状态检查脚本
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("🔍 Second Self 项目状态检查")
print("=" * 60)

# 1. 环境变量检查
print("\n📋 环境变量配置：")
env_vars = {
    "MONGODB_URL": "MongoDB连接",
    "AZURE_OPENAI_KEY": "Azure OpenAI密钥",
    "AZURE_OPENAI_CHAT_DEPLOYMENT": "聊天模型部署",
}

from dotenv import load_dotenv
load_dotenv("backend/.env")

all_configured = True
for var, desc in env_vars.items():
    value = os.getenv(var)
    if value:
        if "password" in var.lower() or "key" in var.lower():
            display_value = "***已配置***"
        else:
            display_value = value[:20] + "..." if len(value) > 20 else value
        print(f"✅ {desc}: {display_value}")
    else:
        print(f"❌ {desc}: 未配置")
        all_configured = False

# 2. 依赖安装检查
print("\n📦 依赖安装状态：")

# Python依赖
python_deps = ["fastapi", "motor", "beanie", "openai", "jose"]
python_missing = []
for dep in python_deps:
    try:
        __import__(dep)
    except ImportError:
        python_missing.append(dep)

if python_missing:
    print(f"❌ Python依赖缺失: {', '.join(python_missing)}")
    print("   运行: ./install_dependencies.sh")
else:
    print("✅ Python依赖已安装")

# Node.js依赖
if os.path.exists("frontend/node_modules"):
    print("✅ 前端依赖已安装")
else:
    print("❌ 前端依赖未安装")
    print("   运行: cd frontend && npm install")

# 3. 测试数据
print("\n📄 测试数据：")
if os.path.exists("test_data/sample_chat.json"):
    print("✅ 测试聊天记录已创建: test_data/sample_chat.json")
else:
    print("❌ 测试数据未创建")
    print("   运行: python quick_setup.py")

# 4. 项目状态总结
print("\n" + "=" * 60)
print("📊 项目状态总结：")
print("=" * 60)

status_items = {
    "Azure OpenAI": "✅ 已配置 (o3模型)" if os.getenv("AZURE_OPENAI_KEY") else "❌ 未配置",
    "MongoDB Atlas": "✅ 已配置" if "mongodb+srv" in (os.getenv("MONGODB_URL") or "") else "⚠️  使用本地MongoDB",
    "Python依赖": "✅ 已安装" if not python_missing else "❌ 未安装",
    "前端依赖": "✅ 已安装" if os.path.exists("frontend/node_modules") else "❌ 未安装",
    "测试数据": "✅ 已准备" if os.path.exists("test_data/sample_chat.json") else "❌ 未准备",
}

ready_count = 0
for item, status in status_items.items():
    print(f"{item}: {status}")
    if "✅" in status:
        ready_count += 1

# 5. 启动建议
print("\n" + "=" * 60)

if ready_count == len(status_items):
    print("\n✅ 项目已准备就绪！可以启动了。")
    print("\n🚀 启动命令：")
    print("\n终端1 - 后端:")
    print("  source venv/bin/activate")
    print("  cd backend")
    print("  python -m uvicorn main:app --reload")
    print("\n终端2 - 前端:")
    print("  cd frontend")
    print("  npm run dev")
    print("\n然后访问: http://localhost:3000")
else:
    print(f"\n⚠️  项目准备度: {ready_count}/{len(status_items)}")
    print("\n需要完成的步骤：")
    
    if python_missing:
        print("1. 安装Python依赖: ./install_dependencies.sh")
    
    if not os.path.exists("frontend/node_modules"):
        print("2. 安装前端依赖: cd frontend && npm install")
    
    if not os.path.exists("test_data/sample_chat.json"):
        print("3. 创建测试数据: python quick_setup.py")
    
    if not os.getenv("AZURE_OPENAI_KEY"):
        print("4. 配置Azure OpenAI密钥")

print("\n" + "=" * 60)