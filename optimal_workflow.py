"""
Second Self 最佳工作流实现
用户只需上传ZIP，系统自动完成所有处理
"""

import asyncio
import zipfile
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class DataSourceType(Enum):
    WECHAT_BACKUP = "wechat_backup"
    WHATSAPP_EXPORT = "whatsapp_export"
    TELEGRAM_EXPORT = "telegram_export"
    UNKNOWN = "unknown"

@dataclass
class ProcessingResult:
    success: bool
    persona_id: str
    message_count: int
    processing_time: float
    error: Optional[str] = None

class SmartDataProcessor:
    """智能数据处理器 - 自动识别和处理各种聊天记录"""
    
    def __init__(self):
        self.supported_formats = {
            'wechat': ['*.db', 'MSG.db', 'MicroMsg.db'],
            'whatsapp': ['*.txt', '_chat.txt'],
            'telegram': ['result.json', 'ChatExport_*'],
        }
    
    async def process_upload(self, file_path: str, user_id: str) -> ProcessingResult:
        """
        一键处理上传文件
        """
        start_time = asyncio.get_event_loop().time()
        
        try:
            # 1. 智能识别文件类型
            source_type = await self._detect_source_type(file_path)
            print(f"✅ 检测到数据源类型: {source_type.value}")
            
            # 2. 解压（如果需要）
            extracted_path = await self._smart_extract(file_path)
            
            # 3. 根据类型选择处理器
            processor = self._get_processor(source_type)
            
            # 4. 解析聊天记录
            messages = await processor.parse(extracted_path)
            print(f"✅ 解析出 {len(messages)} 条消息")
            
            # 5. 构建人格画像
            persona_id = await self._build_persona(messages, user_id)
            
            # 6. 建立RAG索引
            await self._build_rag_index(persona_id, messages)
            
            # 7. 清理临时文件
            await self._cleanup(extracted_path)
            
            processing_time = asyncio.get_event_loop().time() - start_time
            
            return ProcessingResult(
                success=True,
                persona_id=persona_id,
                message_count=len(messages),
                processing_time=processing_time
            )
            
        except Exception as e:
            return ProcessingResult(
                success=False,
                persona_id="",
                message_count=0,
                processing_time=0,
                error=str(e)
            )
    
    async def _detect_source_type(self, file_path: str) -> DataSourceType:
        """智能检测数据源类型"""
        path = Path(file_path)
        
        # 如果是ZIP文件，先查看内容
        if path.suffix.lower() == '.zip':
            with zipfile.ZipFile(file_path, 'r') as zf:
                file_list = zf.namelist()
                
                # 检查微信特征
                if any('MSG.db' in f or 'MicroMsg.db' in f for f in file_list):
                    return DataSourceType.WECHAT_BACKUP
                
                # 检查WhatsApp特征
                if any('WhatsApp Chat' in f for f in file_list):
                    return DataSourceType.WHATSAPP_EXPORT
                
                # 检查Telegram特征
                if any('result.json' in f for f in file_list):
                    return DataSourceType.TELEGRAM_EXPORT
        
        # 单文件检测
        elif path.suffix.lower() == '.db':
            return DataSourceType.WECHAT_BACKUP
        elif 'whatsapp' in path.name.lower():
            return DataSourceType.WHATSAPP_EXPORT
        
        return DataSourceType.UNKNOWN
    
    async def _smart_extract(self, file_path: str) -> str:
        """智能解压文件"""
        path = Path(file_path)
        
        if path.suffix.lower() == '.zip':
            # 创建临时目录
            temp_dir = tempfile.mkdtemp()
            
            # 解压
            with zipfile.ZipFile(file_path, 'r') as zf:
                zf.extractall(temp_dir)
            
            return temp_dir
        else:
            # 不是压缩文件，直接返回
            return str(path.parent)
    
    async def _build_persona(self, messages: List[Dict], user_id: str) -> str:
        """构建人格画像"""
        from uuid import uuid4
        
        # 分析聊天特征
        analysis = await self._analyze_chat_style(messages)
        
        # 创建人格档案
        persona_id = str(uuid4())
        
        # 保存到数据库
        await self._save_persona({
            'id': persona_id,
            'user_id': user_id,
            'name': analysis['contact_name'],
            'message_count': len(messages),
            'style_features': analysis['style'],
            'emoji_profile': analysis['emojis'],
            'topic_preferences': analysis['topics']
        })
        
        return persona_id
    
    async def _build_rag_index(self, persona_id: str, messages: List[Dict]):
        """构建RAG索引"""
        print("🔨 构建向量索引...")
        
        # 1. 文本嵌入
        embeddings = await self._create_embeddings(messages)
        
        # 2. 存入向量数据库
        await self._store_vectors(persona_id, embeddings)
        
        # 3. 构建关键词索引
        await self._build_keyword_index(persona_id, messages)
        
        # 4. 提取对话模式
        await self._extract_patterns(persona_id, messages)
        
        print("✅ RAG索引构建完成")

# Web API 实现
from fastapi import FastAPI, UploadFile, BackgroundTasks
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/api/upload")
async def upload_chat_data(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    user_id: str
):
    """
    一键上传接口 - 用户只需拖拽文件
    """
    # 保存上传文件
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 异步处理
    processor = SmartDataProcessor()
    task_id = str(uuid4())
    
    background_tasks.add_task(
        processor.process_upload,
        temp_path,
        user_id
    )
    
    return JSONResponse({
        "task_id": task_id,
        "status": "processing",
        "message": "正在处理您的聊天记录，请稍候..."
    })

@app.get("/api/status/{task_id}")
async def check_status(task_id: str):
    """检查处理状态"""
    # 从Redis获取任务状态
    status = await get_task_status(task_id)
    
    if status['completed']:
        return {
            "status": "ready",
            "persona_id": status['persona_id'],
            "message": f"处理完成！共导入 {status['message_count']} 条消息"
        }
    else:
        return {
            "status": "processing",
            "progress": status.get('progress', 0),
            "message": "正在处理中..."
        }

# 前端实现示例
"""
// React组件
const UploadZone = () => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  
  const handleDrop = async (files) => {
    setUploading(true);
    
    // 上传文件
    const formData = new FormData();
    formData.append('file', files[0]);
    
    const response = await fetch('/api/upload', {
      method: 'POST',
      body: formData
    });
    
    const { task_id } = await response.json();
    
    // 轮询状态
    const interval = setInterval(async () => {
      const status = await fetch(`/api/status/${task_id}`);
      const data = await status.json();
      
      if (data.status === 'ready') {
        clearInterval(interval);
        // 跳转到聊天界面
        router.push(`/chat/${data.persona_id}`);
      } else {
        setProgress(data.progress);
      }
    }, 1000);
  };
  
  return (
    <div className="upload-zone" onDrop={handleDrop}>
      <Icon name="upload" size={64} />
      <h2>拖拽您的聊天记录到这里</h2>
      <p>支持微信、WhatsApp、Telegram等导出文件</p>
      <p>ZIP文件无需解压，直接上传即可</p>
      
      {uploading && (
        <ProgressBar value={progress} />
      )}
    </div>
  );
};
"""