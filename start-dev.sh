#!/bin/bash

echo "🚀 启动 Second Self 开发环境..."

# 检查是否安装了必要的工具
command -v python3 >/dev/null 2>&1 || { echo >&2 "需要安装 Python 3"; exit 1; }
command -v npm >/dev/null 2>&1 || { echo >&2 "需要安装 Node.js"; exit 1; }

# 创建必要的目录
mkdir -p uploads temp

# 启动后端
echo "启动后端服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

# 在新终端启动后端
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)' && source venv/bin/activate && uvicorn main:app --reload"'

cd ..

# 启动前端
echo "启动前端服务..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "安装前端依赖..."
    npm install
fi

# 在新终端启动前端
osascript -e 'tell app "Terminal" to do script "cd '$(pwd)' && npm run dev"'

echo "✅ 启动完成！"
echo "后端: http://localhost:8000"
echo "前端: http://localhost:3000"
echo "API文档: http://localhost:8000/docs"