#!/usr/bin/env python3
"""
测试所有API端点是否正常工作
"""
import asyncio
import httpx
import json
from datetime import datetime
import os

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.token = None
        self.user_id = None
        self.persona_id = None
        self.chat_id = None
        
    async def test_health(self):
        """测试健康检查"""
        print("\n🏥 测试健康检查...")
        try:
            response = await self.client.get(f"{BASE_URL}/")
            print(f"✅ 健康检查: {response.status_code}")
            print(f"   响应: {response.json()}")
            return True
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
            return False
    
    async def test_auth(self):
        """测试认证功能"""
        print("\n🔐 测试认证功能...")
        
        # 1. 注册
        test_user = {
            "username": f"testuser_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@example.com",
            "password": "TestPass123!"
        }
        
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/auth/register",
                json=test_user
            )
            if response.status_code == 201:
                print(f"✅ 注册成功: {response.status_code}")
                self.user_id = response.json()["id"]
            else:
                print(f"❌ 注册失败: {response.status_code}")
                print(f"   错误: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 注册请求失败: {e}")
            return False
        
        # 2. 登录
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/auth/login",
                data={
                    "username": test_user["username"],
                    "password": test_user["password"]
                }
            )
            if response.status_code == 200:
                print(f"✅ 登录成功: {response.status_code}")
                self.token = response.json()["access_token"]
            else:
                print(f"❌ 登录失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 登录请求失败: {e}")
            return False
        
        # 3. 获取当前用户
        headers = {"Authorization": f"Bearer {self.token}"}
        try:
            response = await self.client.get(
                f"{BASE_URL}/api/auth/me",
                headers=headers
            )
            if response.status_code == 200:
                print(f"✅ 获取用户信息成功: {response.status_code}")
                print(f"   用户: {response.json()['username']}")
            else:
                print(f"❌ 获取用户信息失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取用户信息请求失败: {e}")
            return False
        
        return True
    
    async def test_upload(self):
        """测试文件上传"""
        print("\n📤 测试文件上传...")
        
        # 创建测试文件
        test_content = """[2025-07-07 10:00:00] Alice: Hello! How are you today?
[2025-07-07 10:01:00] Bob: I'm doing great, thanks for asking!
[2025-07-07 10:02:00] Alice: That's wonderful to hear.
[2025-07-07 10:03:00] Bob: How about you?
[2025-07-07 10:04:00] Alice: I'm good too, just working on some projects."""
        
        with open("test_chat.txt", "w") as f:
            f.write(test_content)
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            with open("test_chat.txt", "rb") as f:
                files = {"file": ("test_chat.txt", f, "text/plain")}
                data = {
                    "source_type": "whatsapp",
                    "persona_name": f"Test Persona {datetime.now().strftime('%H%M%S')}"
                }
                
                response = await self.client.post(
                    f"{BASE_URL}/api/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
            
            if response.status_code == 201:
                print(f"✅ 文件上传成功: {response.status_code}")
                result = response.json()
                self.persona_id = result["persona_id"]
                print(f"   人格ID: {self.persona_id}")
                print(f"   消息数: {result['message_count']}")
            else:
                print(f"❌ 文件上传失败: {response.status_code}")
                print(f"   错误: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 文件上传请求失败: {e}")
            return False
        finally:
            # 清理测试文件
            if os.path.exists("test_chat.txt"):
                os.remove("test_chat.txt")
        
        return True
    
    async def test_personas(self):
        """测试人格管理"""
        print("\n👤 测试人格管理...")
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 1. 获取人格列表
        try:
            response = await self.client.get(
                f"{BASE_URL}/api/personas",
                headers=headers
            )
            if response.status_code == 200:
                print(f"✅ 获取人格列表成功: {response.status_code}")
                personas = response.json()
                print(f"   人格数量: {len(personas)}")
            else:
                print(f"❌ 获取人格列表失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 获取人格列表请求失败: {e}")
            return False
        
        # 2. 获取单个人格
        if self.persona_id:
            try:
                response = await self.client.get(
                    f"{BASE_URL}/api/personas/{self.persona_id}",
                    headers=headers
                )
                if response.status_code == 200:
                    print(f"✅ 获取单个人格成功: {response.status_code}")
                    persona = response.json()
                    print(f"   人格名称: {persona['name']}")
                else:
                    print(f"❌ 获取单个人格失败: {response.status_code}")
            except Exception as e:
                print(f"❌ 获取单个人格请求失败: {e}")
        
        return True
    
    async def test_chat(self):
        """测试聊天功能"""
        print("\n💬 测试聊天功能...")
        
        if not self.persona_id:
            print("❌ 需要先创建人格")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        # 1. 创建聊天
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/chats",
                json={
                    "persona_id": self.persona_id,
                    "title": "Test Chat"
                },
                headers=headers
            )
            if response.status_code == 201:
                print(f"✅ 创建聊天成功: {response.status_code}")
                chat = response.json()
                self.chat_id = chat["id"]
                print(f"   聊天ID: {self.chat_id}")
            else:
                print(f"❌ 创建聊天失败: {response.status_code}")
                print(f"   错误: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 创建聊天请求失败: {e}")
            return False
        
        # 2. 发送消息
        try:
            response = await self.client.post(
                f"{BASE_URL}/api/chats/{self.chat_id}/messages",
                json={"content": "Hello! Can you tell me about yourself?"},
                headers=headers
            )
            if response.status_code == 201:
                print(f"✅ 发送消息成功: {response.status_code}")
                message = response.json()
                print(f"   用户消息: {message['content'][:50]}...")
            else:
                print(f"❌ 发送消息失败: {response.status_code}")
                print(f"   错误: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 发送消息请求失败: {e}")
            return False
        
        # 3. 获取聊天历史
        try:
            response = await self.client.get(
                f"{BASE_URL}/api/chats/{self.chat_id}/messages",
                headers=headers
            )
            if response.status_code == 200:
                print(f"✅ 获取聊天历史成功: {response.status_code}")
                messages = response.json()
                print(f"   消息数量: {len(messages)}")
            else:
                print(f"❌ 获取聊天历史失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 获取聊天历史请求失败: {e}")
        
        return True
    
    async def test_mongodb_connection(self):
        """测试MongoDB连接"""
        print("\n🗄️  测试MongoDB连接...")
        
        # 通过API间接测试数据库连接
        headers = {"Authorization": f"Bearer {self.token}"}
        
        try:
            # 尝试获取人格列表，这会查询数据库
            response = await self.client.get(
                f"{BASE_URL}/api/personas",
                headers=headers
            )
            if response.status_code == 200:
                print(f"✅ MongoDB连接正常")
                return True
            else:
                print(f"❌ MongoDB可能有问题: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 数据库测试失败: {e}")
            return False
    
    async def cleanup(self):
        """清理测试数据"""
        if self.token and self.persona_id:
            headers = {"Authorization": f"Bearer {self.token}"}
            try:
                # 删除测试人格
                await self.client.delete(
                    f"{BASE_URL}/api/personas/{self.persona_id}",
                    headers=headers
                )
                print("\n🧹 清理测试数据完成")
            except:
                pass
        
        await self.client.aclose()
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始测试所有API端点...")
        print("=" * 50)
        
        results = {
            "健康检查": await self.test_health(),
            "认证功能": await self.test_auth(),
            "文件上传": await self.test_upload() if self.token else False,
            "人格管理": await self.test_personas() if self.token else False,
            "聊天功能": await self.test_chat() if self.token else False,
            "数据库连接": await self.test_mongodb_connection() if self.token else False,
        }
        
        print("\n" + "=" * 50)
        print("📊 测试结果总结:")
        print("=" * 50)
        
        for test_name, result in results.items():
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{test_name}: {status}")
        
        total = len(results)
        passed = sum(1 for r in results.values() if r)
        print(f"\n总计: {passed}/{total} 通过")
        
        await self.cleanup()
        
        return passed == total


async def main():
    """主函数"""
    print("检查后端服务 http://localhost:8000")
    
    tester = APITester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 所有测试通过！API服务正常工作。")
    else:
        print("\n⚠️  部分测试失败，请检查日志。")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())