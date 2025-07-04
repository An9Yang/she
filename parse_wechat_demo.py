"""
微信聊天记录解析示例代码
注意：这是概念验证代码，实际使用需要在虚拟环境中安装依赖
"""

import sqlite3
import json
from datetime import datetime

class WeChatParser:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def parse_messages(self, contact_name):
        """解析特定联系人的聊天记录"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 查询消息（简化版SQL）
        query = """
        SELECT 
            CreateTime,
            Message,
            Type,
            IsSender,
            StrTalker
        FROM MSG
        WHERE StrTalker = ?
        ORDER BY CreateTime
        """
        
        cursor.execute(query, (contact_name,))
        messages = []
        
        for row in cursor.fetchall():
            timestamp, content, msg_type, is_sender, talker = row
            
            # 转换时间戳
            dt = datetime.fromtimestamp(timestamp)
            
            messages.append({
                'time': dt.isoformat(),
                'content': content,
                'type': self._get_message_type(msg_type),
                'sender': 'me' if is_sender else talker,
                'raw_type': msg_type
            })
        
        conn.close()
        return messages
    
    def _get_message_type(self, type_code):
        """消息类型映射"""
        type_map = {
            1: 'text',
            3: 'image',
            34: 'voice',
            43: 'video',
            47: 'emoji',
            49: 'link',
            10000: 'system'
        }
        return type_map.get(type_code, 'unknown')
    
    def extract_text_corpus(self, messages):
        """提取纯文本语料用于AI训练"""
        corpus = []
        for msg in messages:
            if msg['type'] == 'text' and msg['content']:
                corpus.append({
                    'text': msg['content'],
                    'sender': msg['sender'],
                    'time': msg['time']
                })
        return corpus

# 使用示例
if __name__ == "__main__":
    # 注意：实际使用需要先解密数据库
    parser = WeChatParser("decrypted_MSG.db")
    
    # 解析特定联系人的消息
    messages = parser.parse_messages("friend_wxid")
    
    # 提取文本语料
    text_corpus = parser.extract_text_corpus(messages)
    
    # 保存为JSON供AI训练使用
    with open('chat_corpus.json', 'w', encoding='utf-8') as f:
        json.dump(text_corpus, f, ensure_ascii=False, indent=2)
    
    print(f"解析完成，共提取 {len(text_corpus)} 条文本消息")