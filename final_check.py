"""
最终项目检查（无外部依赖）
"""

import os
import sys

print("=" * 60)
print("🎯 Second Self 项目最终检查")
print("=" * 60)

# 读取环境文件
env_file = "backend/.env"
env_vars = {}
if os.path.exists(env_file):
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()

# 1. 配置检查
print("\n✅ 配置状态：")
print(f"- Azure OpenAI: {'已配置' if 'AZURE_OPENAI_KEY' in env_vars else '未配置'}")
print(f"- MongoDB Atlas: {'已配置' if 'mongodb+srv' in env_vars.get('MONGODB_URL', '') else '使用本地'}")
print(f"- 聊天模型: {env_vars.get('AZURE_OPENAI_CHAT_DEPLOYMENT', '未配置')}")

# 2. 文件检查
print("\n✅ 核心文件：")
core_files = [
    ("backend/main.py", "FastAPI主程序"),
    ("frontend/src/app/page.tsx", "前端首页"),
    ("test_data/sample_chat.json", "测试数据"),
]

for file, desc in core_files:
    exists = "✅" if os.path.exists(file) else "❌"
    print(f"{exists} {desc}: {file}")

# 3. 项目统计
print("\n📊 项目统计：")
py_files = len([f for f in os.walk('backend') for file in f[2] if file.endswith('.py')])
tsx_files = len([f for f in os.walk('frontend/src') for file in f[2] if file.endswith('.tsx')])
print(f"- Python文件: {py_files}个")
print(f"- React组件: {tsx_files}个")

print("\n" + "=" * 60)
print("\n🚀 项目已配置完成！")
print("\n现在你需要：")
print("\n1️⃣ 安装依赖（如果还没装）：")
print("   chmod +x install_dependencies.sh")
print("   ./install_dependencies.sh")

print("\n2️⃣ 启动项目：")
print("\n   终端1 - 后端:")
print("   source venv/bin/activate")
print("   cd backend && python -m uvicorn main:app --reload")
print("\n   终端2 - 前端:")
print("   cd frontend && npm run dev")

print("\n3️⃣ 访问应用：")
print("   http://localhost:3000")

print("\n📝 测试账号：")
print("   可以用任意邮箱注册，如 test@example.com")
print("   上传测试文件: test_data/sample_chat.json")

print("\n✨ 祝使用愉快！")
print("=" * 60)