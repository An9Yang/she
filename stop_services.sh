#!/bin/bash

# 停止服务脚本

echo "🛑 停止 Second Self 服务..."

# 读取PID
if [ -f .backend.pid ]; then
    BACKEND_PID=$(cat .backend.pid)
    kill -9 $BACKEND_PID 2>/dev/null && echo "✅ 后端服务已停止"
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    kill -9 $FRONTEND_PID 2>/dev/null && echo "✅ 前端服务已停止"
    rm .frontend.pid
fi

# 清理端口
lsof -ti:3000,8000 | xargs kill -9 2>/dev/null || true

echo "✅ 所有服务已停止"