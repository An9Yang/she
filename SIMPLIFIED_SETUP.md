# 简化版开发环境设置

## 不使用Docker的快速开始

### 1. MongoDB Atlas设置
```bash
# 1. 创建免费的M0集群
# 2. 获取连接字符串
# 3. 创建数据库用户
# 4. 添加IP白名单 (0.0.0.0/0 用于开发)
```

### 2. 后端启动
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
cd backend
pip install -r requirements.txt

# 配置环境变量
cp ../.env.example ../.env
# 编辑.env，填入：
# MONGODB_URL=mongodb+srv://...
# OPENAI_API_KEY=sk-...

# 启动服务
uvicorn main:app --reload --port 8000
```

### 3. 前端启动
```bash
# 新终端
cd frontend
npm install
npm run dev
```

### 4. Redis (可选)
如果你有Redis云服务：
```bash
# .env中添加
REDIS_URL=redis://...
```

如果没有，可以暂时用内存缓存。

## 优势
- ✅ 启动更快
- ✅ 资源占用少  
- ✅ 利用云服务额度
- ✅ 开发体验更简单

## 部署建议
- **MongoDB**: Atlas M0 (免费)
- **Redis**: AWS ElastiCache / Azure Cache
- **后端**: Google Cloud Run (有免费额度)
- **前端**: Vercel (免费)

这样可以完全利用你的云服务额度，而且部署也很简单！