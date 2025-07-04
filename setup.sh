#!/bin/bash

echo "🚀 Setting up Second Self development environment..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# 创建Python虚拟环境
echo "Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# 安装后端依赖
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# 安装前端依赖
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# 复制环境变量文件
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your actual configuration values"
fi

# 创建必要的目录
mkdir -p uploads temp

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Start the development environment:"
echo "   - Docker: docker-compose up"
echo "   - Or manually:"
echo "     - Backend: cd backend && uvicorn main:app --reload"
echo "     - Frontend: cd frontend && npm run dev"