# Second Self 快速开始指南

## 前置要求

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (可选)
- PostgreSQL, Redis, Qdrant (如果不使用Docker)

## 快速启动

### 方法1: 使用Docker (推荐)

```bash
# 1. 克隆项目
git clone [repository-url]
cd She

# 2. 复制环境变量
cp .env.example .env

# 3. 编辑.env文件，填入你的OpenAI API Key
# OPENAI_API_KEY=your-key-here

# 4. 启动所有服务
docker-compose up -d

# 5. 访问应用
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 方法2: 手动启动

```bash
# 1. 运行setup脚本
./setup.sh

# 2. 激活Python虚拟环境
source venv/bin/activate

# 3. 启动数据库服务
# 确保PostgreSQL, Redis, Qdrant正在运行

# 4. 运行数据库迁移
cd backend
alembic upgrade head

# 5. 启动后端
uvicorn main:app --reload

# 6. 新终端启动Celery
celery -A tasks.celery_app worker --loglevel=info

# 7. 新终端启动前端
cd frontend
npm run dev
```

## 测试流程

1. 访问 http://localhost:3000
2. 注册新账号
3. 上传聊天记录（支持ZIP文件）
4. 等待处理完成
5. 开始对话

## 常见问题

### Q: 如何准备测试数据？
A: 可以使用微信PC版导出聊天记录，或使用我们提供的测试数据。

### Q: 处理需要多长时间？
A: 取决于数据量，通常10MB数据需要1-2分钟。

### Q: 支持哪些聊天记录格式？
A: 目前支持微信(.db)、WhatsApp(.txt)、通用格式(.json/.csv)

## 开发指南

- 后端API文档: http://localhost:8000/docs
- 前端组件: 使用Radix UI + Tailwind CSS
- 状态管理: Zustand
- 请求库: Axios + React Query

## 故障排除

如果遇到问题：
1. 检查.env配置
2. 查看Docker日志: `docker-compose logs -f`
3. 确保所有端口未被占用
4. 查看TEST_LOG.md中的已知问题

---
更多详情请查看完整文档。