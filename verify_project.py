#!/usr/bin/env python3
"""
项目完整性验证脚本（无外部依赖）
"""

import os
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    exists = os.path.exists(filepath)
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_directory_structure():
    """检查目录结构"""
    print("\n📁 检查项目目录结构")
    print("="*50)
    
    required_dirs = {
        "backend": "后端代码目录",
        "backend/api": "API路由目录",
        "backend/core": "核心配置目录",
        "backend/models": "数据模型目录",
        "backend/services": "服务层目录",
        "backend/schemas": "数据架构目录",
        "frontend": "前端代码目录",
        "frontend/src": "前端源码目录",
        "frontend/src/app": "Next.js应用目录",
        "frontend/src/components": "组件目录",
        "frontend/src/services": "前端服务目录",
    }
    
    all_exist = True
    for dir_path, desc in required_dirs.items():
        if not check_file_exists(dir_path, desc):
            all_exist = False
    
    return all_exist

def check_backend_files():
    """检查后端文件"""
    print("\n🔧 检查后端文件")
    print("="*50)
    
    backend_files = {
        "backend/main.py": "FastAPI主应用",
        "backend/requirements.txt": "Python依赖列表",
        "backend/.env": "环境配置文件",
        "backend/core/config.py": "配置管理",
        "backend/core/database.py": "数据库连接",
        "backend/core/deps.py": "依赖注入",
        "backend/models/user.py": "用户模型",
        "backend/models/persona.py": "人格模型",
        "backend/models/message.py": "消息模型",
        "backend/models/chat.py": "对话模型",
        "backend/services/auth.py": "认证服务",
        "backend/services/data_processor.py": "数据处理服务",
        "backend/services/rag_service.py": "RAG服务",
        "backend/services/chat_service.py": "对话服务",
        "backend/api/auth.py": "认证API",
        "backend/api/personas.py": "人格API",
        "backend/api/chat_api.py": "对话API",
        "backend/api/upload.py": "上传API",
    }
    
    all_exist = True
    for file_path, desc in backend_files.items():
        if not check_file_exists(file_path, desc):
            all_exist = False
    
    return all_exist

def check_frontend_files():
    """检查前端文件"""
    print("\n🎨 检查前端文件")
    print("="*50)
    
    frontend_files = {
        "frontend/package.json": "前端依赖配置",
        "frontend/tsconfig.json": "TypeScript配置",
        "frontend/tailwind.config.js": "Tailwind配置",
        "frontend/.env.local": "前端环境变量",
        "frontend/src/app/page.tsx": "首页",
        "frontend/src/app/layout.tsx": "布局组件",
        "frontend/src/middleware.ts": "中间件",
        "frontend/src/services/api.ts": "API服务",
        "frontend/src/components/ChatInterface.tsx": "聊天界面组件",
        "frontend/src/components/PersonaCard.tsx": "人格卡片组件",
        "frontend/src/components/FileUpload.tsx": "文件上传组件",
        "frontend/src/app/auth/login/page.tsx": "登录页面",
        "frontend/src/app/auth/register/page.tsx": "注册页面",
        "frontend/src/app/personas/page.tsx": "人格列表页",
        "frontend/src/app/chat/[id]/page.tsx": "对话页面",
        "frontend/src/app/chat/new/page.tsx": "新建对话页",
    }
    
    all_exist = True
    for file_path, desc in frontend_files.items():
        if not check_file_exists(file_path, desc):
            all_exist = False
    
    return all_exist

def check_test_files():
    """检查测试文件"""
    print("\n🧪 检查测试文件")
    print("="*50)
    
    test_files = {
        "simple_test.py": "简单测试脚本",
        "test_rag.py": "RAG测试脚本",
        "test_frontend.py": "前端测试脚本",
        "run_full_test.py": "完整测试脚本",
    }
    
    all_exist = True
    for file_path, desc in test_files.items():
        if not check_file_exists(file_path, desc):
            all_exist = False
    
    return all_exist

def check_documentation():
    """检查文档"""
    print("\n📚 检查项目文档")
    print("="*50)
    
    doc_files = {
        "README.md": "项目说明",
        "CLAUDE.md": "Claude助手说明",
        "DEVELOPMENT.md": "开发进度跟踪",
        "TECH_DECISIONS.md": "技术决策记录",
        "TEST_LOG.md": "测试日志",
        "IDEAS.md": "创意和想法",
    }
    
    all_exist = True
    for file_path, desc in doc_files.items():
        if not check_file_exists(file_path, desc):
            all_exist = False
    
    return all_exist

def analyze_package_json():
    """分析前端依赖"""
    print("\n📦 分析前端依赖")
    print("="*50)
    
    try:
        with open("frontend/package.json", "r") as f:
            package = json.load(f)
        
        print("项目名称:", package.get("name", "未知"))
        print("版本:", package.get("version", "未知"))
        
        deps = package.get("dependencies", {})
        print(f"\n依赖包数量: {len(deps)}")
        
        key_deps = ["next", "react", "typescript", "axios", "lucide-react", "tailwindcss"]
        print("\n关键依赖:")
        for dep in key_deps:
            version = deps.get(dep, "未安装")
            status = "✅" if dep in deps else "❌"
            print(f"  {status} {dep}: {version}")
        
        return True
    except Exception as e:
        print(f"❌ 无法分析package.json: {e}")
        return False

def check_env_files():
    """检查环境变量配置"""
    print("\n🔐 检查环境变量")
    print("="*50)
    
    # 检查后端环境变量
    backend_env = "backend/.env"
    if os.path.exists(backend_env):
        print("✅ 后端环境文件存在")
        with open(backend_env, "r") as f:
            content = f.read()
            required_vars = ["MONGODB_URL", "SECRET_KEY", "AZURE_OPENAI_KEY"]
            for var in required_vars:
                if var in content:
                    print(f"  ✅ {var} 已配置")
                else:
                    print(f"  ⚠️  {var} 未配置")
    else:
        print("❌ 后端环境文件不存在")
    
    # 检查前端环境变量
    frontend_env = "frontend/.env.local"
    if os.path.exists(frontend_env):
        print("\n✅ 前端环境文件存在")
        with open(frontend_env, "r") as f:
            content = f.read()
            if "NEXT_PUBLIC_API_URL" in content:
                print("  ✅ API URL 已配置")
    else:
        print("\n❌ 前端环境文件不存在")
    
    return True

def generate_report():
    """生成项目报告"""
    print("\n" + "="*60)
    print("📊 Second Self 项目完整性检查报告")
    print("="*60)
    
    checks = {
        "目录结构": check_directory_structure(),
        "后端文件": check_backend_files(),
        "前端文件": check_frontend_files(),
        "测试文件": check_test_files(),
        "项目文档": check_documentation(),
        "前端依赖": analyze_package_json(),
        "环境配置": check_env_files(),
    }
    
    print("\n📈 检查结果汇总:")
    print("-"*40)
    
    all_passed = True
    for item, passed in checks.items():
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{item}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("\n🎉 项目结构完整！可以开始安装依赖并运行。")
        print("\n下一步操作：")
        print("1. 安装依赖: ./install_dependencies.sh")
        print("2. 启动后端: cd backend && python -m uvicorn main:app --reload")
        print("3. 启动前端: cd frontend && npm run dev")
    else:
        print("\n⚠️  项目结构不完整，请检查缺失的文件。")
    
    # 统计信息
    print("\n📊 项目统计:")
    print(f"- 后端Python文件: {len([f for f in Path('backend').rglob('*.py') if f.is_file()])}")
    print(f"- 前端TypeScript文件: {len([f for f in Path('frontend').rglob('*.tsx') if f.is_file()])}")
    print(f"- 文档文件: {len([f for f in Path('.').glob('*.md') if f.is_file()])}")
    
    return all_passed

if __name__ == "__main__":
    result = generate_report()
    exit(0 if result else 1)