#!/bin/bash

# 后端启动脚本 - 修复版

echo "🚀 启动 Second Self 后端服务..."

# 进入后端目录
cd "$(dirname "$0")"

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 设置项目根目录到PYTHONPATH
export PYTHONPATH="$(dirname "$PWD"):$PYTHONPATH"
echo "✅ PYTHONPATH设置为: $PYTHONPATH"

# 加载环境变量
if [ -f .env ]; then
    echo "📝 加载环境变量..."
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  警告: .env文件不存在"
fi

# 使用简化版本启动（避免MongoDB索引冲突）
echo "🔧 使用 main_simple.py 启动..."
echo "📍 访问地址: http://localhost:8000"
echo "📚 API文档: http://localhost:8000/docs"
echo ""

# 启动服务
uvicorn backend.main_simple:app --reload --host 0.0.0.0 --port 8000