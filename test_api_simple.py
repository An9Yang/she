#!/usr/bin/env python3
"""
简单API测试 - 诊断问题
"""

import requests
import json
import time

API_BASE = "http://localhost:8000/api"

# 1. 测试健康检查
print("1. 健康检查...")
try:
    resp = requests.get("http://localhost:8000/health")
    print(f"  状态: {resp.status_code}")
    print(f"  响应: {resp.json()}")
except Exception as e:
    print(f"  错误: {e}")

# 2. 测试注册
print("\n2. 测试注册...")
user_data = {
    "email": f"test_{int(time.time())}@example.com",
    "username": f"test_{int(time.time())}",
    "password": "Test123456!"
}
print(f"  发送数据: {json.dumps(user_data, indent=2)}")

try:
    resp = requests.post(f"{API_BASE}/auth/register", json=user_data)
    print(f"  状态码: {resp.status_code}")
    print(f"  响应: {resp.text}")
    
    if resp.status_code == 500:
        print("\n  💡 提示: 检查后端日志获取详细错误信息")
        
except Exception as e:
    print(f"  错误: {e}")

# 3. 测试API文档
print("\n3. API文档...")
try:
    resp = requests.get("http://localhost:8000/docs")
    print(f"  状态: {resp.status_code}")
    if resp.status_code == 200:
        print("  ✅ API文档可访问: http://localhost:8000/docs")
except Exception as e:
    print(f"  错误: {e}")