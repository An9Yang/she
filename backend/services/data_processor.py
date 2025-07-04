"""
数据处理服务 - 处理上传的聊天记录
"""

import os
import json
import zipfile
import chardet
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from pathlib import Path
import re

from backend.models.persona import Persona, PersonaStatus
from backend.models.message import Message
from backend.services.message_service import MessageService
from backend.services.rag_service import RAGService
from backend.core.config import settings
from beanie import PydanticObjectId

logger = logging.getLogger(__name__)


class DataProcessorService:
    """数据处理服务"""
    
    def __init__(self):
        self.supported_formats = {
            '.txt': self._parse_txt_chat,
            '.json': self._parse_json_chat,
            '.csv': self._parse_csv_chat,
            '.html': self._parse_html_chat,
            '.db': self._parse_db_chat,
            '.zip': self._process_zip_file
        }
        self.message_service = MessageService()
        self.rag_service = RAGService()
    
    async def process_chat_data(
        self,
        file_path: str,
        user_id: str,
        task_id: str
    ) -> Dict:
        """处理聊天数据的主入口"""
        try:
            logger.info(f"开始处理文件: {file_path}")
            
            # 1. 检测文件类型
            file_ext = Path(file_path).suffix.lower()
            if file_ext not in self.supported_formats:
                raise ValueError(f"不支持的文件类型: {file_ext}")
            
            # 2. 创建Persona记录
            persona = await self._create_persona(user_id, file_path)
            
            # 3. 解析聊天记录
            messages = await self.supported_formats[file_ext](file_path)
            logger.info(f"解析出 {len(messages)} 条消息")
            
            if not messages:
                await self._update_persona_status(persona, PersonaStatus.ERROR)
                raise ValueError("未能解析出任何消息")
            
            # 4. 数据清洗和分析
            cleaned_messages = self._clean_messages(messages)
            persona_info = self._analyze_persona_info(cleaned_messages)
            
            # 5. 保存消息到数据库（包含向量生成）
            await self._save_messages_with_embeddings(cleaned_messages, persona.id)
            
            # 7. 更新Persona信息
            await self._update_persona_info(persona, persona_info, len(cleaned_messages))
            
            # 8. 清理临时文件
            self._cleanup_temp_file(file_path)
            
            logger.info(f"处理完成: {persona.name}")
            return {
                "status": "success",
                "persona_id": str(persona.id),
                "message_count": len(cleaned_messages)
            }
            
        except Exception as e:
            logger.error(f"处理失败: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _create_persona(self, user_id: str, file_path: str) -> Persona:
        """创建Persona记录"""
        persona = Persona(
            user_id=PydanticObjectId(user_id),
            name=f"导入的对话_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            status=PersonaStatus.PROCESSING
        )
        await persona.save()
        return persona
    
    def _detect_encoding(self, file_path: str) -> str:
        """检测文件编码"""
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # 读取前10KB
            result = chardet.detect(raw_data)
            return result['encoding'] or 'utf-8'
    
    async def _parse_txt_chat(self, file_path: str) -> List[Dict]:
        """解析TXT格式的聊天记录（如WhatsApp导出）"""
        messages = []
        encoding = self._detect_encoding(file_path)
        
        # WhatsApp格式: [2024/1/1, 10:30:45] 张三: 消息内容
        pattern = r'\[(\d{4}/\d{1,2}/\d{1,2},\s*\d{1,2}:\d{2}:\d{2})\]\s*([^:]+):\s*(.*)'
        
        with open(file_path, 'r', encoding=encoding) as f:
            content = f.read()
            matches = re.findall(pattern, content)
            
            for match in matches:
                timestamp_str, sender, content = match
                messages.append({
                    'timestamp': self._parse_timestamp(timestamp_str),
                    'sender': sender.strip(),
                    'content': content.strip()
                })
        
        return messages
    
    async def _parse_json_chat(self, file_path: str) -> List[Dict]:
        """解析JSON格式的聊天记录"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        messages = []
        # 支持多种JSON结构
        if isinstance(data, list):
            messages = data
        elif isinstance(data, dict) and 'messages' in data:
            messages = data['messages']
        
        # 标准化字段名
        standardized = []
        for msg in messages:
            standardized.append({
                'timestamp': msg.get('timestamp') or msg.get('time') or msg.get('date'),
                'sender': msg.get('sender') or msg.get('from') or msg.get('author'),
                'content': msg.get('content') or msg.get('text') or msg.get('message')
            })
        
        return standardized
    
    async def _parse_csv_chat(self, file_path: str) -> List[Dict]:
        """解析CSV格式的聊天记录"""
        import csv
        messages = []
        encoding = self._detect_encoding(file_path)
        
        with open(file_path, 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            for row in reader:
                messages.append({
                    'timestamp': row.get('timestamp') or row.get('date'),
                    'sender': row.get('sender') or row.get('from'),
                    'content': row.get('content') or row.get('message')
                })
        
        return messages
    
    async def _parse_html_chat(self, file_path: str) -> List[Dict]:
        """解析HTML格式的聊天记录（如微信导出）"""
        # TODO: 实现HTML解析
        # 使用BeautifulSoup解析
        return []
    
    async def _parse_db_chat(self, file_path: str) -> List[Dict]:
        """解析数据库格式的聊天记录（如微信.db）"""
        # TODO: 实现数据库解析
        # 需要先解密，然后读取SQLite
        return []
    
    async def _process_zip_file(self, file_path: str) -> List[Dict]:
        """处理ZIP压缩包"""
        messages = []
        temp_dir = Path(file_path).parent / f"temp_{Path(file_path).stem}"
        
        try:
            # 解压文件
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # 递归处理解压后的文件
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_ext = Path(file_path).suffix.lower()
                    
                    if file_ext in self.supported_formats and file_ext != '.zip':
                        try:
                            file_messages = await self.supported_formats[file_ext](file_path)
                            messages.extend(file_messages)
                        except Exception as e:
                            logger.warning(f"处理文件失败 {file}: {e}")
            
            # 清理临时目录
            import shutil
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            logger.error(f"解压失败: {e}")
            raise
        
        return messages
    
    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """解析时间戳"""
        # 尝试多种时间格式
        formats = [
            '%Y/%m/%d, %H:%M:%S',
            '%Y-%m-%d %H:%M:%S',
            '%Y年%m月%d日 %H:%M:%S',
            '%d/%m/%Y, %H:%M:%S',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str.strip(), fmt)
            except:
                continue
        
        # 如果都失败，返回当前时间
        return datetime.now()
    
    def _clean_messages(self, messages: List[Dict]) -> List[Dict]:
        """清洗消息数据"""
        cleaned = []
        for msg in messages:
            # 过滤空消息
            if not msg.get('content') or not msg.get('content').strip():
                continue
            
            # 过滤系统消息
            if msg.get('sender', '').lower() in ['system', '系统消息']:
                continue
            
            cleaned.append({
                'content': msg['content'].strip(),
                'sender': msg['sender'],
                'timestamp': msg.get('timestamp') or datetime.now()
            })
        
        return cleaned
    
    def _analyze_persona_info(self, messages: List[Dict]) -> Dict:
        """分析人格信息"""
        # 找出最常见的发送者（非用户）
        from collections import Counter
        senders = Counter(msg['sender'] for msg in messages)
        
        # 假设出现次数第二多的是对方（第一多的可能是用户）
        most_common = senders.most_common(2)
        persona_name = most_common[1][0] if len(most_common) > 1 else most_common[0][0]
        
        # 获取时间范围
        timestamps = [msg['timestamp'] for msg in messages if isinstance(msg.get('timestamp'), datetime)]
        date_start = min(timestamps) if timestamps else None
        date_end = max(timestamps) if timestamps else None
        
        return {
            'name': persona_name,
            'date_range_start': date_start,
            'date_range_end': date_end
        }
    
    async def _save_messages_with_embeddings(self, messages: List[Dict], persona_id: PydanticObjectId):
        """保存消息到数据库（包含向量生成）"""
        # 准备消息数据
        messages_data = []
        for msg in messages:
            messages_data.append({
                'content': msg['content'],
                'sender': msg['sender'],
                'timestamp': msg.get('timestamp', datetime.now()),
                'metadata': msg.get('metadata', {})
            })
        
        # 使用MessageService批量创建消息（会自动生成向量）
        if messages_data:
            await self.message_service.batch_create_messages(
                persona_id=str(persona_id),
                messages_data=messages_data
            )
    
    async def _update_persona_info(self, persona: Persona, info: Dict, message_count: int):
        """更新Persona信息"""
        persona.name = info['name']
        persona.message_count = message_count
        persona.date_range_start = info.get('date_range_start')
        persona.date_range_end = info.get('date_range_end')
        persona.status = PersonaStatus.READY
        
        # 使用RAG服务分析对话模式
        patterns = await self.rag_service.analyze_conversation_patterns(
            persona_id=str(persona.id),
            sample_size=100
        )
        
        if patterns:
            persona.personality_traits = patterns.get('emotional_patterns', {})
            persona.speaking_style = {
                'response_patterns': patterns.get('response_patterns', {}),
                'topic_transitions': patterns.get('topic_transitions', [])
            }
        
        await persona.save()
    
    async def _update_persona_status(self, persona: Persona, status: PersonaStatus):
        """更新Persona状态"""
        persona.status = status
        await persona.save()
    
    def _cleanup_temp_file(self, file_path: str):
        """清理临时文件"""
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"清理文件失败: {e}")