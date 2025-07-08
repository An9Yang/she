# 技术决策记录 (ADR)

> 记录所有重要的技术决策，包括背景、选择原因、替代方案和潜在风险。

## ADR-001: 使用Hybrid RAG而非模型微调
**日期**: 2025-07-03  
**状态**: ✅ 已采纳

### 背景
需要让AI模仿特定人的对话风格，有两种主要方案：
1. 微调LLM模型
2. 使用RAG技术

### 决策
选择 **Hybrid RAG** (结合语义、关键词、时序等多种检索策略)

### 原因
1. **无需GPU**: RAG只需API调用，微调需要昂贵GPU
2. **快速迭代**: RAG可实时调整，微调需要重新训练
3. **效果足够**: RAG能达到80%相似度，满足MVP需求
4. **成本可控**: 按使用量付费 vs 固定高昂训练成本

### 替代方案
- **方案A**: LoRA微调 - 需要16GB+ GPU，训练时间长
- **方案B**: Prompt工程 - 效果有限，无法捕捉个性化特征
- **方案C**: Few-shot learning - 作为RAG的补充使用

### 风险
- RAG效果上限可能不如微调
- 对向量数据库依赖较大
- 需要优化检索策略

---

## ADR-002: 前端框架选择Next.js
**日期**: 2025-07-03  
**状态**: ✅ 已采纳

### 背景
需要一个现代化的前端框架，支持SSR、SEO、快速开发

### 决策
选择 **Next.js 14** 

### 原因
1. **全栈能力**: API Routes可以快速搭建BFF
2. **性能优秀**: App Router + RSC提供最佳性能
3. **生态成熟**: 大量组件库和最佳实践
4. **部署简单**: Vercel一键部署

### 替代方案
- **Vue/Nuxt**: 团队不熟悉
- **Pure React**: 需要自己配置太多
- **Angular**: 过于重量级

---

## ADR-003: 数据处理采用自动识别策略
**日期**: 2025-07-03  
**状态**: ✅ 已采纳

### 背景
用户可能上传各种格式的聊天记录，需要统一处理

### 决策
实现**智能文件识别系统**，自动判断数据源类型

### 原因
1. **用户友好**: 无需用户选择文件类型
2. **减少错误**: 避免用户选错格式
3. **易于扩展**: 新增格式只需添加识别规则

### 实现细节
```python
# 识别策略
1. 文件扩展名
2. 文件内容特征
3. 目录结构模式
```

---

## ADR-004: 使用Qdrant作为向量数据库
**日期**: 2025-07-03  
**状态**: 💡 待评估

---

## ADR-006: 数据库选择 - MongoDB vs PostgreSQL
**日期**: 2025-07-03  
**状态**: ✅ 已采纳

### 背景
用户有云服务额度，需要重新评估数据库选择

### MongoDB的优势
1. **非结构化数据友好** - 聊天记录格式多样
2. **灵活Schema** - 人格特征可以动态扩展
3. **Atlas Vector Search** - MongoDB内置向量搜索！
4. **云服务成熟** - Azure CosmosDB/Atlas都很稳定

### 新架构建议
```
MongoDB Atlas (或 Azure CosmosDB)
├── users collection
├── personas collection  
├── messages collection (带向量索引)
└── chat_history collection
```

### 决策
**推荐使用MongoDB** + Atlas Vector Search，这样可以：
- 省去Qdrant，简化架构
- 利用你的云服务额度
- 一个数据库搞定所有需求

---

## ADR-007: 使用Azure OpenAI替代OpenAI API
**日期**: 2025-07-03  
**状态**: ✅ 已采纳

### 背景
用户有Azure额度，且Azure OpenAI提供更好的企业级支持

### Azure OpenAI优势
1. **更稳定** - SLA保证，不会突然限流
2. **合规性** - 数据不会用于训练，符合隐私要求
3. **成本优势** - 利用现有Azure额度
4. **区域部署** - 可选择就近的数据中心
5. **统一管理** - 与其他Azure服务集成

### 技术实现
```python
# 使用Azure OpenAI SDK
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://YOUR_RESOURCE_NAME.openai.azure.com",
    api_key="YOUR_API_KEY",
    api_version="2024-02-01"
)
```

### 模型选择
- **GPT-4o**: 用于高质量对话生成
- **GPT-3.5-Turbo**: 用于快速响应场景
- **text-embedding-ada-002**: 用于向量嵌入

### 决策
采用Azure OpenAI，配合Azure整体架构
用户有云服务额度，需要重新评估数据库选择

### MongoDB的优势
1. **非结构化数据友好** - 聊天记录格式多样
2. **灵活Schema** - 人格特征可以动态扩展
3. **Atlas Vector Search** - MongoDB内置向量搜索！
4. **云服务成熟** - Azure CosmosDB/Atlas都很稳定

### 新架构建议
```
MongoDB Atlas (或 Azure CosmosDB)
├── users collection
├── personas collection  
├── messages collection (带向量索引)
└── chat_history collection
```

### 决策
**推荐使用MongoDB** + Atlas Vector Search，这样可以：
- 省去Qdrant，简化架构
- 利用你的云服务额度
- 一个数据库搞定所有需求

### 候选方案
1. **Qdrant**: 开源、性能好、功能全
2. **Pinecone**: 托管服务、易用但贵
3. **Weaviate**: 功能强大但复杂
4. **Chroma**: 轻量级但功能有限

### 倾向
Qdrant - 平衡了性能、成本和功能

### 待决策
- [ ] 自托管 vs 云服务
- [ ] 数据分片策略
- [ ] 备份方案

---

## ADR-005: 微信数据解密方案
**日期**: 2025-07-03  
**状态**: ⚠️ 需要进一步研究

### 背景
微信聊天记录使用SQLCipher加密

### 当前方案
使用开源项目 **WeChatMsg**

### 问题
1. 仅支持Windows
2. 需要微信运行中
3. 版本兼容性

### 备选方案
1. **服务器端解密**: 安全风险
2. **用户端工具**: 需要额外下载
3. **手动导出**: 用户体验差

### TODO
- [ ] 研究Mac/Linux解决方案
- [ ] 评估法律风险
- [ ] 设计降级方案

---

## ADR-006: 后端启动架构简化
**日期**: 2025-07-04  
**状态**: ✅ 已采纳

### 背景
MongoDB索引冲突导致后端启动失败，需要快速解决方案继续开发

### 决策
创建`main_simple.py`作为简化版入口，跳过数据库初始化步骤

### 原因
1. **快速恢复开发** - 不阻塞前端开发进度
2. **隔离问题** - 将索引问题与业务逻辑分离
3. **临时方案** - 后续可以修复数据库后切回main.py

### 实现
```python
@app.on_event("startup")
async def startup_event():
    logger.info("Second Self backend started (without DB init)")
    # 跳过 await init_db()
```

### 后果
- ✅ 开发可以继续
- ⚠️ 数据库索引未创建
- ⚠️ 需要手动管理数据一致性

### TODO
- [x] 修复MongoDB索引冲突 ✅ [2025-07-04]
- [x] 迁移回main.py ✅ [2025-07-04]
- [ ] 添加数据库健康检查

---

## ADR-007: Mock API开发模式
**日期**: 2025-07-04  
**状态**: ✅ 已采纳

### 背景
CORS配置和认证问题阻碍前端开发

### 决策
实现完整的Mock API层，允许前端独立开发

### 实现
1. **mockApi.ts** - 模拟所有API端点
2. **USE_MOCK_API** - 环境变量控制
3. **假数据** - 预设personas和对话

### 优势
- 前后端解耦开发
- 快速原型验证
- 无需等待后端修复

### 切换机制
```typescript
const api = USE_MOCK_API ? mockApi : realApi
```

---

## 🔄 决策模板

```markdown
## ADR-XXX: [决策标题]
**日期**: YYYY-MM-DD  
**状态**: 💡 提议 / 🚧 讨论中 / ✅ 已采纳 / ❌ 已拒绝

### 背景
[为什么需要做这个决策]

### 决策
[具体选择了什么]

### 原因
[为什么做出这个选择]

### 替代方案
[考虑过哪些其他选项]

### 后果
[这个决策会带来什么影响]

### 风险
[潜在的问题和缓解措施]
```

---

## ADR-008: 文件格式自适应解析
**日期**: 2025-07-04  
**状态**: ✅ 已采纳

### 背景
用户上传的聊天记录格式多样，原有解析器只支持特定WhatsApp格式，导致许多文件解析失败

### 决策
实现自适应格式检测算法，支持多种聊天记录格式

### 实现
```python
patterns = [
    # WhatsApp格式1: [2024/1/1, 10:30:45] 张三: 消息内容
    # WhatsApp格式2: 1/1/24, 10:30 - 张三: 消息内容
    # 微信格式: 2024-01-01 10:30:45 张三\n消息内容
    # 通用格式: 2024-01-01 10:30 张三: 消息内容
    # 简单格式: 张三: 消息内容
]
# 自动选择匹配最多的格式
```

### 原因
1. **提高兼容性** - 支持更多用户的文件
2. **改善体验** - 减少"未能解析"错误
3. **灵活扩展** - 易于添加新格式

### 后果
- ✅ 解析成功率大幅提升
- ✅ 支持无时间戳的简单对话
- ⚠️ 可能误判某些特殊格式

---

## ADR-009: React状态管理最佳实践
**日期**: 2025-07-04  
**状态**: ✅ 已采纳

### 背景
发现React闭包陷阱导致进度条卡在10%

### 决策
使用函数式状态更新避免闭包问题

### 实现
```javascript
// ❌ 错误：闭包中的progress始终是旧值
setProgress(Math.min(90, progress + 10))

// ✅ 正确：函数式更新获取最新值
setProgress(prevProgress => Math.min(90, prevProgress + 10))
```

### 原因
1. **避免stale closure** - 确保获取最新状态
2. **React最佳实践** - 官方推荐的模式
3. **减少bug** - 避免难以调试的状态问题

---

## ADR-010: 聊天会话管理架构
**日期**: 2025-07-04  
**状态**: ✅ 已采纳

### 背景
需要管理用户与不同人格的多个对话会话

### 决策
使用独立的Chat模型管理对话会话

### 实现
```python
class Chat(Document):
    user_id: PydanticObjectId
    persona_id: PydanticObjectId
    title: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
```

### 原因
1. **会话隔离** - 每个对话独立管理
2. **历史跟踪** - 保留完整对话历史
3. **易于导出** - 支持对话导出和备份
4. **性能优化** - 按需加载对话内容

### 后果
- ✅ 清晰的对话管理
- ✅ 支持多个并行对话
- ⚠️ 需要额外的数据库空间

---

## ADR-011: Azure OpenAI o3模型集成
**日期**: 2025-07-04  
**状态**: ✅ 已采纳

### 背景
用户提供了Azure OpenAI o3模型的访问权限

### 决策
使用Azure OpenAI o3模型进行对话生成，同时保留mock embeddings

### 实现
```python
# o3模型特殊配置
response = await client.chat.completions.create(
    model="o3",
    messages=messages,
    max_completion_tokens=500  # o3使用这个参数而非max_tokens
    # temperature参数不支持，使用默认值
)
```

### 原因
1. **最新模型** - o3是OpenAI的最新模型
2. **更好的性能** - 提供更高质量的对话
3. **灵活配置** - 可以根据需要切换模型

### 后果
- ✅ 高质量的AI对话
- ✅ 保持了系统的稳定性
- ⚠️ 需要注意o3模型的特殊参数
- ⚠️ Embedding仍使用mock实现

---

## ADR-005: API路径兼容性策略
**日期**: 2025-07-07  
**状态**: ✅ 已实施

### 背景
前后端开发过程中出现API路径不一致：
- 前端期望：`/api/auth/login`
- 后端实际：`/api/auth/token`（OAuth2标准）
- 注册需要username字段，但前端只传email
- 人格管理缺少创建路由

### 决策
创建**API适配器层**而非修改现有代码

### 实施方案
1. 创建`backend/api/adapter.py`处理路径映射
2. 修改`UserBase` schema让username可选
3. 在`AuthService`中自动从email生成username
4. 补充缺失的API路由（如personas的POST）

### 原因
1. **向后兼容**: 不破坏现有API
2. **最小改动**: 前后端都不需要大规模修改
3. **灵活性**: 可以逐步迁移到统一标准
4. **降低风险**: 新老API可以共存

### 替代方案
- **方案A**: 修改前端所有API调用 - 工作量大，易遗漏
- **方案B**: 修改后端路由 - 破坏现有API，影响其他客户端
- **方案C**: 使用API网关 - 过度设计，增加复杂度

### 实施结果
✅ 成功实施，所有功能正常工作
- 注册无需手动输入username
- 登录支持两种路径
- 人格创建功能恢复

### 经验教训
1. API设计初期就应该前后端对齐
2. 遵循RESTful标准但也要考虑实际使用
3. 适配器模式是处理兼容性的好方法

---
*最后更新: 2025-07-07*