# Second Self - AI对话伴侣

> 把散落的聊天片段转化为可交互的活性记忆，随时与重要的人继续对话。

## 🎯 项目概述

Second Self 是一个基于AI的对话伴侣应用。用户可以上传与某人的完整聊天记录，系统通过Hybrid RAG技术分析对方的性格特征与表达习惯，构建高度相似的"数字分身"，让用户能够继续获得风格一致的对话体验。

## 🚀 核心特性

- **一键导入**: 支持微信、WhatsApp等多平台聊天记录，ZIP直接上传
- **智能分析**: 自动提取语言风格、情绪模式、话题偏好
- **高度还原**: 基于Hybrid RAG技术，对话相似度达80%+
- **隐私安全**: 本地处理，数据加密，用户完全控制

## 📁 项目结构

```
She/
├── CLAUDE.md          # Claude Code工作指令
├── DEVELOPMENT.md     # 开发计划和进度跟踪 ⭐
├── README.md          # 项目说明（本文件）
├── TECH_DECISIONS.md  # 技术决策记录
├── TEST_LOG.md        # 测试记录
├── IDEAS.md           # 创意和实验想法
│
├── docs/              # 详细文档
├── frontend/          # Next.js前端
├── backend/           # FastAPI后端
├── data_processor/    # 数据处理模块
├── rag_engine/        # RAG引擎
└── tests/             # 测试文件
```

## 🛠 技术栈

- **前端**: Next.js 14 + TypeScript + Tailwind CSS
- **后端**: FastAPI (Python) + Celery
- **数据库**: PostgreSQL + Redis + Qdrant
- **AI**: OpenAI API + LangChain + Hybrid RAG
- **部署**: Docker + Vercel/Railway

## 🏃 快速开始

### 一键启动（推荐）
```bash
# 启动前后端服务
./start_services.sh

# 停止所有服务
./stop_services.sh
```

### 手动启动
```bash
# 后端
cd backend
source venv/bin/activate
./start_backend_fixed.sh

# 前端（新terminal）
cd frontend
npm run dev
```

### 首次设置
```bash
# 克隆项目
git clone [repo-url]
cd She

# 后端设置
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 前端设置
cd ../frontend
npm install
```

### 开发模式
- 前端使用Mock API，无需后端即可开发
- 访问 http://localhost:3000 自动跳转到personas页面
- API文档: http://localhost:8000/docs

## 📊 项目状态

- 开始日期: 2025-07-03
- 当前阶段: MVP核心功能已完成，优化中
- MVP目标: 2025-08-30
- 进度: 83% (15/18 核心任务完成)

## 🤝 参与贡献

本项目采用文档驱动开发，所有决策和进度都记录在案。参与前请先阅读：

1. `CLAUDE.md` - 了解工作流程
2. `DEVELOPMENT.md` - 查看当前进度
3. `TECH_DECISIONS.md` - 理解技术选择

## 📝 许可证

[待定]

---
*项目由 Claude Code 协助开发*