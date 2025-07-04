#!/usr/bin/env python3
"""
简单上传测试
"""

import requests
import json
import time
from pathlib import Path

API_BASE = "http://localhost:8000/api"

# 1. 注册用户
print("1. 注册用户...")
user_data = {
    "email": f"upload_test_{int(time.time())}@example.com",
    "username": f"upload_test_{int(time.time())}",
    "password": "Test123456!"
}

resp = requests.post(f"{API_BASE}/auth/register", json=user_data)
print(f"  状态: {resp.status_code}")
if resp.status_code != 200:
    print(f"  错误: {resp.text}")
    exit(1)

# 2. 登录
print("\n2. 登录...")
login_data = {
    "username": user_data["email"],
    "password": user_data["password"]
}

resp = requests.post(f"{API_BASE}/auth/token", data=login_data)
print(f"  状态: {resp.status_code}")
if resp.status_code != 200:
    print(f"  错误: {resp.text}")
    exit(1)

token = resp.json()["access_token"]
print(f"  Token: {token[:20]}...")

# 3. 创建测试文件
print("\n3. 创建测试文件...")
test_data = {
    "messages": [
        {
            "sender": "Alice",
            "content": "Hey! How are you?",
            "timestamp": "2024-01-01T10:00:00Z"
        },
        {
            "sender": "Bob",
            "content": "I'm good! You?",
            "timestamp": "2024-01-01T10:01:00Z"
        }
    ]
}

test_file = Path("test_upload.json")
with open(test_file, 'w') as f:
    json.dump(test_data, f)
print(f"  创建文件: {test_file}")

# 4. 上传文件
print("\n4. 上传文件...")
headers = {
    "Authorization": f"Bearer {token}"
}

with open(test_file, 'rb') as f:
    files = {'file': ('test_chat.json', f, 'application/json')}
    resp = requests.post(f"{API_BASE}/upload", files=files, headers=headers)

print(f"  状态: {resp.status_code}")
print(f"  响应: {resp.text}")

# 清理
test_file.unlink()
print("\n✅ 测试完成")