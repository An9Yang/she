"""
工具函数
"""

from bson import ObjectId
from typing import Any, Dict

def mongo_to_dict(obj: Any) -> Dict[str, Any]:
    """
    将MongoDB文档转换为字典，处理ObjectId
    """
    if hasattr(obj, 'dict'):
        data = obj.dict()
    elif hasattr(obj, '__dict__'):
        data = obj.__dict__
    else:
        return obj
    
    # 处理_id字段
    if '_id' in data and isinstance(data['_id'], ObjectId):
        data['id'] = str(data['_id'])
        del data['_id']
    
    # 处理其他ObjectId字段
    for key, value in data.items():
        if isinstance(value, ObjectId):
            data[key] = str(value)
    
    return data