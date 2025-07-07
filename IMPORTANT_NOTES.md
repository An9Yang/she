# Second Self 重要备忘录

> ⚠️ **重要**：这个文件记录了项目的关键配置信息，请勿删除！

## 🔑 环境配置位置

### .env文件位置
**重要**：.env文件在 `backend/.env`，不是根目录！

```bash
# 正确的路径
backend/.env

# 不要在这里找
/.env  # ❌ 错误位置
```

### 为什么容易搞错？
1. 通常.env在项目根目录，但这个项目放在了backend目录
2. 根目录只有.env.example示例文件
3. backend/.env已被.gitignore正确忽略

## 🚀 服务启动说明

### 启动命令
```bash
# 推荐：使用官方脚本
./start_services.sh

# 手动启动后端
cd backend
source ../venv/bin/activate
export PYTHONPATH="$PWD/..:$PYTHONPATH"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 常见报错及解决
1. **ERROR: [Errno 48] Address already in use**
   ```bash
   # 查找占用端口的进程
   lsof -i :8000
   # 或杀死所有uvicorn进程
   pkill -f uvicorn
   ```

2. **ModuleNotFoundError: No module named 'backend'**
   - 确保从正确的目录运行
   - 设置正确的PYTHONPATH

## 🔧 当前配置状态

### MongoDB Atlas ✅
- 连接正常
- 数据库名：second_self
- 集群：cluster0.f2bzcr.mongodb.net

### Azure OpenAI ⚠️
- Chat模型（o3）：✅ 正常工作
- Embedding模型（text-embedding-ada-002）：❌ 部署不存在
- 当前使用Mock实现作为降级方案

### 需要你做的事
1. **创建Azure Embedding部署**
   - 登录Azure Portal
   - 在OpenAI资源中创建text-embedding-ada-002部署
   - 或修改backend/.env中的AZURE_OPENAI_EMBEDDING_DEPLOYMENT为你实际的部署名

2. **清理测试文件**
   ```bash
   # 查看所有测试文件
   ls *.py | grep -E "(test_|check_)"
   
   # 可以安全删除或移动到tests/
   ```

## 📝 API测试

### 健康检查
```bash
# 注意是 /health 不是 /api/health
curl http://localhost:8000/health
```

### API文档
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ⚡ 快速调试

### 检查环境配置
```bash
cd /Users/annanyang/Downloads/Prototype\ and\ test/She
python check_env_config.py
```

### 测试向量功能
```bash
python test_embeddings.py
```

### 测试所有API
```bash
python test_api_endpoints.py
```

---
最后更新：2025-07-07 18:20