#!/bin/bash

echo "🚀 启动 Second Self 项目"
echo "========================"

# 检查是否有虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 未找到Python虚拟环境"
    echo "请先运行: ./install_dependencies.sh"
    exit 1
fi

# 检查是否安装了前端依赖
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ 未找到前端依赖"
    echo "请先运行: ./install_dependencies.sh"
    exit 1
fi

# 创建两个终端会话的提示
echo ""
echo "项目需要在两个终端中运行："
echo ""
echo "📟 终端 1 - 后端服务:"
echo "================================"
echo "source venv/bin/activate"
echo "cd backend"
echo "python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📱 终端 2 - 前端服务:"
echo "================================"
echo "cd frontend"
echo "npm run dev"
echo ""
echo "🌐 访问地址:"
echo "- 前端界面: http://localhost:3000"
echo "- 后端API文档: http://localhost:8000/docs"
echo ""
echo "💡 提示:"
echo "- 确保MongoDB正在运行"
echo "- 检查环境变量配置是否正确"
echo "- 首次使用请先注册账号"