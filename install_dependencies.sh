#!/bin/bash

echo "📦 安装 Second Self 项目依赖"
echo "============================="

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装后端依赖
echo ""
echo "📥 安装后端依赖..."
cd backend

# 创建简化的requirements.txt（去除可能有问题的包）
cat > requirements_simple.txt << EOF
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
pydantic-settings==2.1.0

# MongoDB
motor==3.3.2
beanie==1.24.0

# OpenAI
openai==1.8.0

# File Processing
aiofiles==23.2.1
chardet==5.2.0

# Development
httpx==0.26.0
EOF

pip install -r requirements_simple.txt

cd ..

# 安装前端依赖
echo ""
echo "📥 安装前端依赖..."
cd frontend

# 检查是否安装了npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm未安装。请先安装Node.js"
    exit 1
fi

npm install

cd ..

echo ""
echo "✅ 依赖安装完成！"
echo ""
echo "启动项目："
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 启动后端: cd backend && python -m uvicorn main:app --reload"
echo "3. 启动前端: cd frontend && npm run dev"