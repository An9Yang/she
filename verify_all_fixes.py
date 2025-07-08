#!/usr/bin/env python3
"""
验证所有修复是否生效
"""
import asyncio
import httpx
import json
from datetime import datetime

async def verify_fixes():
    """验证所有修复"""
    base_url = "http://localhost:8000"
    client = httpx.AsyncClient(timeout=30.0)
    
    print("🔍 验证所有修复")
    print("=" * 50)
    
    results = {
        "注册（无username）": False,
        "登录（路径适配）": False,
        "文件上传": False,
        "人格创建": False,
        "聊天功能": False
    }
    
    # 1. 注册测试
    print("\n1. 测试注册（无需username）:")
    test_user = {
        "email": f"verify_{datetime.now().timestamp()}@example.com",
        "password": "TestPass123!"
    }
    
    try:
        response = await client.post(f"{base_url}/api/auth/register", json=test_user)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 注册成功！Username自动生成: {data.get('username')}")
            results["注册（无username）"] = True
            user_email = data.get('email')
        else:
            print(f"❌ 注册失败: {response.status_code}")
            user_email = None
    except Exception as e:
        print(f"❌ 异常: {str(e)}")
        user_email = None
    
    # 2. 登录测试
    if user_email:
        print("\n2. 测试登录（适配路径）:")
        try:
            response = await client.post(
                f"{base_url}/api/auth/login",
                json={"email": user_email, "password": "TestPass123!"}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 登录成功！")
                results["登录（路径适配）"] = True
                token = data.get('access_token')
                client.headers["Authorization"] = f"Bearer {token}"
            else:
                print(f"❌ 登录失败: {response.status_code}")
                token = None
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            token = None
    
    # 3. 文件上传测试
    if token:
        print("\n3. 测试文件上传:")
        test_content = {"messages": [{"sender": "test", "content": "hello", "timestamp": "2024-01-01 10:00:00"}]}
        
        with open("verify_test.json", "w") as f:
            json.dump(test_content, f)
        
        try:
            with open("verify_test.json", "rb") as f:
                files = {"file": ("verify_test.json", f, "application/json")}
                response = await client.post(f"{base_url}/api/upload/", files=files)
            
            if response.status_code == 200:
                print(f"✅ 文件上传成功！")
                results["文件上传"] = True
            else:
                print(f"❌ 上传失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
        finally:
            import os
            if os.path.exists("verify_test.json"):
                os.remove("verify_test.json")
    
    # 4. 人格创建测试
    if token:
        print("\n4. 测试人格创建:")
        persona_data = {
            "name": "验证助手",
            "avatar_url": "https://example.com/avatar.png"
        }
        
        try:
            response = await client.post(f"{base_url}/api/personas/", json=persona_data)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 人格创建成功！ID: {data.get('id')}")
                results["人格创建"] = True
                persona_id = data.get('id')
            else:
                print(f"❌ 创建失败: {response.status_code}")
                print(f"   详情: {response.text}")
                persona_id = None
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
            persona_id = None
    
    # 5. 聊天测试
    if persona_id:
        print("\n5. 测试聊天功能:")
        try:
            response = await client.post(
                f"{base_url}/api/chat/{persona_id}/message",
                json={"message": "你好"}
            )
            if response.status_code == 200:
                print(f"✅ 聊天功能正常！")
                results["聊天功能"] = True
            else:
                print(f"❌ 聊天失败: {response.status_code}")
        except Exception as e:
            print(f"❌ 异常: {str(e)}")
    
    await client.aclose()
    
    # 总结
    print("\n" + "=" * 50)
    print("验证结果总结:")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 所有修复都已生效！产品基本功能正常！")
    else:
        print("\n⚠️  还有一些问题需要解决")

if __name__ == "__main__":
    asyncio.run(verify_fixes())