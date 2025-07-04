#!/usr/bin/env python3
"""
后端启动检查脚本 - 诊断启动问题
"""

import sys
import os
from pathlib import Path

print("=== 后端启动诊断 ===\n")

# 1. Python环境检查
print("1. Python环境:")
print(f"   Python路径: {sys.executable}")
print(f"   Python版本: {sys.version}")
print(f"   当前目录: {os.getcwd()}")
print()

# 2. PYTHONPATH检查
print("2. PYTHONPATH检查:")
print(f"   PYTHONPATH: {os.environ.get('PYTHONPATH', '未设置')}")
print(f"   sys.path前5个: {sys.path[:5]}")
print()

# 3. 模块导入测试
print("3. 模块导入测试:")
modules_to_test = [
    "fastapi",
    "motor",
    "beanie", 
    "openai",
    "langchain",
    "backend",
    "backend.api",
    "backend.core.config"
]

for module in modules_to_test:
    try:
        if module.startswith("backend"):
            # 添加正确的路径
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
        
        __import__(module)
        print(f"   ✅ {module}")
    except ImportError as e:
        print(f"   ❌ {module}: {str(e)}")
print()

# 4. 环境变量检查
print("4. 关键环境变量:")
env_vars = ["MONGODB_URL", "OPENAI_API_KEY", "AZURE_OPENAI_ENDPOINT"]
for var in env_vars:
    value = os.environ.get(var, "未设置")
    if value != "未设置" and len(value) > 20:
        value = value[:20] + "..."
    print(f"   {var}: {value}")
print()

# 5. 文件结构检查
print("5. 项目结构检查:")
backend_dir = Path(__file__).parent
important_files = [
    "main.py",
    "main_simple.py",
    ".env",
    "requirements.txt",
    "api/__init__.py",
    "core/config.py"
]

for file in important_files:
    file_path = backend_dir / file
    exists = "✅" if file_path.exists() else "❌"
    print(f"   {exists} {file}")
print()

# 6. 虚拟环境检查
print("6. 虚拟环境状态:")
venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
print(f"   虚拟环境激活: {'✅ 是' if venv_active else '❌ 否'}")
if venv_active:
    print(f"   虚拟环境路径: {sys.prefix}")
print()

print("=== 诊断完成 ===")