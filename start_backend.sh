#!/bin/bash

echo "🚀 启动 Second Self 后端..."

# 进入backend目录
cd "/Users/annanyang/Downloads/Prototype and test/She/backend"

# 激活虚拟环境
source venv/bin/activate

# 设置Python路径
export PYTHONPATH="${PYTHONPATH}:/Users/annanyang/Downloads/Prototype and test/She"

# 启动服务
echo "📍 后端服务运行在: http://localhost:8000"
echo "📖 API文档: http://localhost:8000/docs"
echo ""
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000