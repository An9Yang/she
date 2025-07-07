#!/usr/bin/env python3
"""运行测试套件的脚本"""
import sys
import subprocess
import os
from pathlib import Path

def run_command(cmd, description):
    """运行命令并显示结果"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"❌ {description} 失败!")
        return False
    
    print(f"✅ {description} 成功!")
    return True

def main():
    """主函数"""
    print("🚀 开始运行 Second Self 测试套件...")
    
    # 确保在项目根目录
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # 检查虚拟环境
    if not os.path.exists("venv"):
        print("❌ 未找到虚拟环境! 请先运行: python -m venv venv")
        sys.exit(1)
    
    # 激活虚拟环境提示
    print("请确保已激活虚拟环境:")
    print("  - Windows: .\\venv\\Scripts\\activate")
    print("  - Mac/Linux: source venv/bin/activate")
    
    tests_passed = True
    
    # 1. 运行代码格式检查
    if not run_command(
        "python -m black --check backend/ tests/",
        "代码格式检查 (Black)"
    ):
        print("提示: 运行 'python -m black backend/ tests/' 来自动格式化代码")
        tests_passed = False
    
    # 2. 运行类型检查
    if not run_command(
        "python -m mypy backend/ --ignore-missing-imports",
        "类型检查 (MyPy)"
    ):
        tests_passed = False
    
    # 3. 运行 linting
    if not run_command(
        "python -m flake8 backend/ tests/ --max-line-length=100 --exclude=venv,__pycache__",
        "代码质量检查 (Flake8)"
    ):
        tests_passed = False
    
    # 4. 运行单元测试
    if not run_command(
        "python -m pytest tests/api tests/services tests/core -v -m 'unit'",
        "单元测试"
    ):
        tests_passed = False
    
    # 5. 运行集成测试
    if not run_command(
        "python -m pytest tests/integration -v -m 'integration'",
        "集成测试"
    ):
        tests_passed = False
    
    # 6. 运行所有测试并生成覆盖率报告
    if not run_command(
        "python -m pytest tests/ -v --cov=backend --cov-report=html --cov-report=term",
        "完整测试套件 + 覆盖率报告"
    ):
        tests_passed = False
    
    # 总结
    print(f"\n{'='*60}")
    if tests_passed:
        print("🎉 所有测试通过!")
        print("📊 覆盖率报告已生成: htmlcov/index.html")
    else:
        print("❌ 部分测试失败，请检查上面的错误信息")
        sys.exit(1)
    
    # 显示快速测试命令
    print(f"\n{'='*60}")
    print("快速测试命令:")
    print("  - 只运行单元测试: pytest tests/ -m unit")
    print("  - 只运行API测试: pytest tests/api/")
    print("  - 只运行服务测试: pytest tests/services/")
    print("  - 运行特定测试: pytest tests/api/test_auth.py::TestAuthAPI::test_login_success")
    print("  - 查看覆盖率: open htmlcov/index.html")

if __name__ == "__main__":
    main()