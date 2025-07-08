#!/usr/bin/env python3
"""
测试正确的聊天流程
"""
import asyncio
import httpx
from datetime import datetime

async def test_chat_flow():
    """测试聊天的正确流程"""
    base_url = "http://localhost:8000"
    client = httpx.AsyncClient(timeout=30.0)
    
    print("🗨️ 测试聊天流程")
    print("=" * 50)
    
    # 1. 创建测试用户
    test_user = {
        "email": f"chat_test_{datetime.now().timestamp()}@example.com",
        "password": "TestPass123!"
    }
    
    response = await client.post(f"{base_url}/api/auth/register", json=test_user)
    if response.status_code != 200:
        print("❌ 注册失败")
        return
        
    # 2. 登录
    response = await client.post(
        f"{base_url}/api/auth/login",
        json={"email": test_user["email"], "password": test_user["password"]}
    )
    
    if response.status_code != 200:
        print("❌ 登录失败")
        return
        
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    print("✅ 登录成功")
    
    # 3. 创建人格
    response = await client.post(
        f"{base_url}/api/personas/",
        json={"name": "测试助手", "avatar_url": None}
    )
    
    if response.status_code != 200:
        print(f"❌ 创建人格失败: {response.status_code}")
        print(f"   详情: {response.text}")
        return
        
    persona_id = response.json()["id"]
    print(f"✅ 人格创建成功，ID: {persona_id}")
    
    # 4. 创建聊天会话
    response = await client.post(
        f"{base_url}/api/chat/",
        json={"persona_id": persona_id, "title": "测试对话"}
    )
    
    if response.status_code != 200:
        print(f"❌ 创建聊天失败: {response.status_code}")
        print(f"   详情: {response.text}")
        return
        
    chat_data = response.json()
    print(f"聊天会话响应: {chat_data}")
    
    # 尝试获取chat_id，可能在不同的字段
    chat_id = chat_data.get("id") or chat_data.get("_id") or chat_data.get("chat_id")
    if not chat_id:
        print(f"❌ 无法获取chat_id，响应内容: {chat_data}")
        return
        
    print(f"✅ 聊天会话创建成功，ID: {chat_id}")
    
    # 5. 发送消息
    response = await client.post(
        f"{base_url}/api/chat/{chat_id}/messages",
        json={"content": "你好，这是测试消息"}
    )
    
    if response.status_code == 200:
        print("✅ 消息发送成功！")
        ai_response = response.json()
        print(f"   AI回复: {ai_response.get('content', '')[:50]}...")
    else:
        print(f"❌ 发送消息失败: {response.status_code}")
        print(f"   详情: {response.text}")
    
    await client.aclose()
    
    print("\n" + "=" * 50)
    print("聊天流程测试完成！")
    print("\n正确的API调用顺序：")
    print("1. 注册用户 -> POST /api/auth/register")
    print("2. 登录获取token -> POST /api/auth/login")
    print("3. 创建人格 -> POST /api/personas/")
    print("4. 创建聊天会话 -> POST /api/chat/")
    print("5. 发送消息 -> POST /api/chat/{chat_id}/messages")

if __name__ == "__main__":
    asyncio.run(test_chat_flow())