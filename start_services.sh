#!/bin/bash

# 启动前后端服务脚本

echo "🚀 启动 Second Self 服务..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 启动后端
echo -e "${BLUE}📦 启动后端服务...${NC}"
cd backend
source venv/bin/activate
export PYTHONPATH="$(dirname "$PWD"):$PYTHONPATH"
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
echo -e "${GREEN}✅ 后端启动成功 (PID: $BACKEND_PID)${NC}"
echo "   访问地址: http://localhost:8000"
echo "   API文档: http://localhost:8000/docs"
echo ""

# 等待后端启动
sleep 3

# 启动前端
echo -e "${BLUE}🎨 启动前端服务...${NC}"
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo -e "${GREEN}✅ 前端启动成功 (PID: $FRONTEND_PID)${NC}"
echo "   访问地址: http://localhost:3000"
echo ""

# 保存PID到文件
echo $BACKEND_PID > ../.backend.pid
echo $FRONTEND_PID > ../.frontend.pid

echo -e "${GREEN}🎉 所有服务已启动!${NC}"
echo ""
echo "停止服务请运行: ./stop_services.sh"
echo ""

# 等待用户按Ctrl+C
echo "按 Ctrl+C 停止所有服务..."
wait