# Second Self 部署指南

## 推荐架构

```
前端: Vercel (免费)
后端: Azure App Service (利用你的额度)
数据库: MongoDB Atlas (免费M0集群)
文件存储: Azure Blob Storage
```

## 1. MongoDB Atlas设置

1. 访问 https://cloud.mongodb.com
2. 创建免费M0集群
3. 创建数据库用户
4. 获取连接字符串
5. 在Atlas中创建向量搜索索引：

```json
{
  "mappings": {
    "dynamic": true,
    "fields": {
      "embedding": {
        "dimensions": 1536,
        "similarity": "cosine",
        "type": "knnVector"
      }
    }
  }
}
```

## 2. 后端部署到Azure

### 使用Azure CLI

```bash
# 登录Azure
az login

# 创建资源组
az group create --name secondself-rg --location eastus

# 创建App Service计划
az appservice plan create --name secondself-plan --resource-group secondself-rg --sku B1 --is-linux

# 创建Web App
az webapp create --resource-group secondself-rg --plan secondself-plan --name secondself-api --runtime "PYTHON:3.11"

# 配置环境变量
az webapp config appsettings set --resource-group secondself-rg --name secondself-api --settings \
  MONGODB_URL="your-mongodb-atlas-url" \
  OPENAI_API_KEY="your-openai-key" \
  SECRET_KEY="your-secret-key"

# 部署代码
az webapp up --resource-group secondself-rg --name secondself-api --runtime "PYTHON:3.11"
```

### 或使用GitHub Actions

创建 `.github/workflows/azure-deploy.yml`

## 3. 前端部署到Vercel

1. Push代码到GitHub
2. 访问 https://vercel.com
3. 导入GitHub仓库
4. 设置环境变量：
   - `NEXT_PUBLIC_API_URL`: https://secondself-api.azurewebsites.net
5. 部署

## 4. 自定义域名（可选）

- Vercel: 在项目设置中添加域名
- Azure: 在App Service中配置自定义域名

## 5. 监控和日志

- Azure: Application Insights
- Vercel: 内置分析
- MongoDB Atlas: 内置监控

## 成本估算

- MongoDB Atlas M0: 免费
- Vercel: 免费
- Azure App Service B1: 约$13/月（使用你的额度）
- OpenAI API: 按使用量计费

总计：基本免费（利用云服务额度）