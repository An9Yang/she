#!/usr/bin/env python3
"""
完整用户流程测试
测试: 注册 -> 登录 -> 上传文件 -> 生成人格 -> 对话
"""

import asyncio
import aiohttp
import json
import time
from pathlib import Path

API_BASE_URL = "http://localhost:8000/api"

class UserFlowTest:
    def __init__(self):
        self.session = None
        self.token = None
        self.user_email = f"test_{int(time.time())}@example.com"
        self.password = "Test123456!"
        self.persona_id = None
        self.chat_id = None
        
    async def setup(self):
        """初始化session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """清理session"""
        if self.session:
            await self.session.close()
    
    async def test_register(self):
        """测试注册"""
        print("📝 测试注册...")
        data = {
            "email": self.user_email,
            "username": f"test_{int(time.time())}",
            "password": self.password,
            "name": "Test User"
        }
        
        async with self.session.post(f"{API_BASE_URL}/auth/register", json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"  ✅ 注册成功: {result['email']}")
                return True
            else:
                error = await resp.text()
                print(f"  ❌ 注册失败: {error}")
                return False
    
    async def test_login(self):
        """测试登录"""
        print("\n🔐 测试登录...")
        # OAuth2密码模式需要form-data格式
        data = aiohttp.FormData()
        data.add_field('username', self.user_email)
        data.add_field('password', self.password)
        
        async with self.session.post(f"{API_BASE_URL}/auth/token", data=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                self.token = result['access_token']
                print(f"  ✅ 登录成功，获得token")
                # 设置后续请求的认证头
                self.session.headers.update({"Authorization": f"Bearer {self.token}"})
                return True
            else:
                error = await resp.text()
                print(f"  ❌ 登录失败: {error}")
                return False
    
    async def test_upload(self):
        """测试文件上传"""
        print("\n📤 测试文件上传...")
        
        # 创建测试聊天数据
        test_data = {
            "messages": [
                {
                    "sender": "Alice",
                    "content": "Hey! How are you doing today?",
                    "timestamp": "2024-01-01T10:00:00Z"
                },
                {
                    "sender": "Bob",
                    "content": "I'm good! Just working on some coding projects. You?",
                    "timestamp": "2024-01-01T10:01:00Z"
                },
                {
                    "sender": "Alice",
                    "content": "Same here! Working on a React app. It's challenging but fun!",
                    "timestamp": "2024-01-01T10:02:00Z"
                },
                {
                    "sender": "Bob",
                    "content": "React is great! Are you using hooks?",
                    "timestamp": "2024-01-01T10:03:00Z"
                },
                {
                    "sender": "Alice",
                    "content": "Yes! useState and useEffect mostly. Still learning though 😅",
                    "timestamp": "2024-01-01T10:04:00Z"
                }
            ],
            "metadata": {
                "platform": "test",
                "participants": ["Alice", "Bob"]
            }
        }
        
        # 创建临时JSON文件
        test_file = Path("test_chat_upload.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        try:
            # 上传文件
            data = aiohttp.FormData()
            data.add_field('file',
                          open(test_file, 'rb'),
                          filename='test_chat.json',
                          content_type='application/json')
            
            # 需要更新headers来处理multipart，注意URL结尾的斜杠
            headers = {'Authorization': f'Bearer {self.token}'}
            async with self.session.post(
                f"{API_BASE_URL}/upload/",  # 注意结尾的斜杠
                data=data,
                headers=headers
            ) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    print(f"  ✅ 文件上传成功")
                    print(f"  📊 解析出 {result.get('message_count', 0)} 条消息")
                    
                    # 如果返回了persona_id
                    if 'persona_id' in result:
                        self.persona_id = result['persona_id']
                        print(f"  🎭 生成人格ID: {self.persona_id}")
                    
                    return True
                else:
                    error = await resp.text()
                    print(f"  ❌ 上传失败: {error}")
                    return False
        finally:
            # 清理临时文件
            if test_file.exists():
                test_file.unlink()
    
    async def test_list_personas(self):
        """测试获取人格列表"""
        print("\n🎭 测试获取人格列表...")
        
        async with self.session.get(f"{API_BASE_URL}/personas/") as resp:
            if resp.status == 200:
                personas = await resp.json()
                print(f"  ✅ 获取成功，共 {len(personas)} 个人格")
                
                if personas and not self.persona_id:
                    # MongoDB返回的是_id字段
                    self.persona_id = personas[0].get('_id', personas[0].get('id'))
                    print(f"  📌 使用第一个人格: {personas[0].get('name', 'Unknown')}")
                
                return True
            else:
                error = await resp.text()
                print(f"  ❌ 获取失败: {error}")
                return False
    
    async def test_create_chat(self):
        """测试创建对话"""
        print("\n💬 测试创建对话...")
        
        if not self.persona_id:
            print("  ⚠️  没有可用的人格ID")
            return False
        
        data = {
            "persona_id": self.persona_id,
            "title": "测试对话"
        }
        
        async with self.session.post(f"{API_BASE_URL}/chat/", json=data) as resp:
            if resp.status == 200:
                result = await resp.json()
                self.chat_id = result.get('_id', result.get('id'))
                print(f"  ✅ 创建对话成功，ID: {self.chat_id}")
                return True
            else:
                error = await resp.text()
                print(f"  ❌ 创建对话失败: {error}")
                return False
    
    async def test_send_message(self):
        """测试发送消息"""
        print("\n📨 测试发送消息...")
        
        if not self.chat_id:
            print("  ⚠️  没有可用的对话ID")
            return False
        
        data = {
            "content": "Hello! How are you today?"
        }
        
        async with self.session.post(
            f"{API_BASE_URL}/chat/{self.chat_id}/messages",
            json=data
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"  ✅ 发送成功")
                print(f"  🤖 AI回复: {result.get('content', '')[:100]}...")
                return True
            else:
                error = await resp.text()
                print(f"  ❌ 发送失败: {error}")
                return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=== 开始完整用户流程测试 ===\n")
        
        await self.setup()
        
        try:
            # 运行测试序列
            tests = [
                self.test_register,
                self.test_login,
                self.test_upload,
                self.test_list_personas,
                self.test_create_chat,
                self.test_send_message
            ]
            
            results = []
            for test in tests:
                result = await test()
                results.append(result)
                if not result:
                    print("\n❌ 测试中断：前置步骤失败")
                    break
            
            # 测试总结
            print("\n=== 测试总结 ===")
            passed = sum(results)
            total = len(results)
            print(f"通过: {passed}/{total}")
            
            if passed == total:
                print("✅ 所有测试通过！")
                return True
            else:
                print("❌ 部分测试失败")
                return False
                
        finally:
            await self.cleanup()

async def main():
    # 检查后端是否运行
    print("🔍 检查后端服务...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as resp:
                if resp.status == 200:
                    print("✅ 后端服务正常\n")
                else:
                    print("❌ 后端服务异常")
                    return
    except:
        print("❌ 无法连接到后端服务")
        print("💡 请先运行: ./start_services.sh")
        return
    
    # 运行测试
    tester = UserFlowTest()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())