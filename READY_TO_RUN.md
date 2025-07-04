# 🎉 Second Self 项目已准备就绪！

## ✅ 已完成的准备工作

1. **环境隔离**：
   - ✅ 创建了Python虚拟环境 (`venv`)
   - ✅ 所有Python包都安装在虚拟环境中
   - ✅ 没有污染全局Python环境

2. **依赖安装**：
   - ✅ 后端Python依赖已安装（FastAPI, MongoDB驱动等）
   - ✅ 前端npm依赖已安装（Next.js, React等）

3. **配置完成**：
   - ✅ Azure OpenAI已配置（o3模型）
   - ✅ MongoDB Atlas已配置
   - ✅ 环境变量已设置

4. **测试数据**：
   - ✅ 示例聊天记录已创建：`test_data/sample_chat.json`

## 🚀 启动项目

### 方法1：使用启动脚本（推荐）

打开两个终端窗口：

**终端1 - 启动后端**：
```bash
./run_backend.sh
```

**终端2 - 启动前端**：
```bash
./run_frontend.sh
```

### 方法2：手动启动

**终端1 - 后端**：
```bash
source venv/bin/activate
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
cd backend
python -m uvicorn main:app --reload
```

**终端2 - 前端**：
```bash
cd frontend
npm run dev
```

## 🌐 访问应用

- **前端界面**: http://localhost:3000
- **API文档**: http://localhost:8000/docs

## 📝 使用流程

1. 访问 http://localhost:3000
2. 点击"立即开始"或"注册"
3. 创建账号（可以用假邮箱如 test@example.com）
4. 登录后点击"导入聊天记录"
5. 上传 `test_data/sample_chat.json`
6. 等待处理完成
7. 点击"开始对话"，享受AI对话体验！

## ⚠️ 注意事项

- 确保MongoDB Atlas的IP白名单包含你的IP
- o3模型可能响应较慢，请耐心等待
- 首次启动可能需要一些时间加载

## 🛠️ 故障排除

**后端启动失败**：
- 检查是否激活了虚拟环境
- 确认PYTHONPATH设置正确

**前端启动失败**：
- 确认npm依赖已安装
- 检查端口3000是否被占用

**连接错误**：
- 检查MongoDB Atlas连接
- 验证Azure OpenAI密钥

---

项目完全准备就绪，开始你的Second Self之旅吧！ 🎊