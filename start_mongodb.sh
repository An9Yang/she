#!/bin/bash

echo "🚀 启动 MongoDB..."

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ 需要先安装Docker"
    echo "请访问 https://www.docker.com/products/docker-desktop 下载安装"
    exit 1
fi

# 检查是否已有mongodb容器
if docker ps -a | grep -q mongodb-secondself; then
    echo "📦 MongoDB容器已存在，启动中..."
    docker start mongodb-secondself
else
    echo "📦 创建并启动MongoDB容器..."
    docker run -d \
        --name mongodb-secondself \
        -p 27017:27017 \
        -v mongodb-data:/data/db \
        mongo:latest
fi

echo "✅ MongoDB已启动在 localhost:27017"
echo ""
echo "💡 提示："
echo "   - 停止MongoDB: docker stop mongodb-secondself"
echo "   - 删除MongoDB: docker rm mongodb-secondself"
echo "   - 查看日志: docker logs mongodb-secondself"