#!/usr/bin/env python3
"""
完整用户流程测试
测试从注册到对话的完整流程
"""
import asyncio
import httpx
import json
import os
from datetime import datetime
from pathlib import Path
import time

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_step(step: int, title: str):
    print(f"\n{Colors.BLUE}{Colors.BOLD}步骤 {step}: {title}{Colors.END}")
    print("-" * 50)

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

class FullFlowTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.client = httpx.AsyncClient(timeout=60.0)
        self.token = None
        self.user_data = None
        self.persona_id = None
        self.ux_feedback = []
        
    async def close(self):
        await self.client.aclose()
    
    def record_ux_feedback(self, feedback: str, severity: str = "info"):
        """记录用户体验反馈"""
        self.ux_feedback.append({
            "feedback": feedback,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        })
    
    async def step1_register(self) -> bool:
        """步骤1: 用户注册"""
        print_step(1, "用户注册")
        
        # 生成唯一用户数据
        timestamp = str(time.time()).replace('.', '')
        self.user_data = {
            "email": f"user_{timestamp}@example.com",
            "password": "SecurePass123!",
            "username": f"user_{timestamp}",
            "nickname": "测试用户小明"
        }
        
        print_info(f"注册邮箱: {self.user_data['email']}")
        
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/auth/register",
                json=self.user_data
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"注册成功！用户ID: {data['user']['id']}")
                print_info(f"响应时间: {response_time:.2f}秒")
                
                # UX反馈
                if response_time > 1:
                    self.record_ux_feedback(
                        f"注册响应时间较长({response_time:.2f}秒)，建议优化",
                        "warning"
                    )
                
                self.record_ux_feedback(
                    "注册成功后应该自动登录，避免用户重复输入",
                    "suggestion"
                )
                
                return True
            else:
                print_error(f"注册失败: {response.status_code}")
                print_error(f"错误详情: {response.text}")
                
                # UX反馈
                if "already exists" in response.text:
                    self.record_ux_feedback(
                        "用户已存在的错误提示不够友好，应该提供找回密码链接",
                        "important"
                    )
                
                return False
                
        except Exception as e:
            print_error(f"注册异常: {str(e)}")
            return False
    
    async def step2_login(self) -> bool:
        """步骤2: 用户登录"""
        print_step(2, "用户登录")
        
        if not self.user_data:
            print_error("没有用户数据，跳过登录")
            return False
        
        print_info(f"使用账号登录: {self.user_data['email']}")
        
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": self.user_data["email"],
                    "password": self.user_data["password"]
                }
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                print_success("登录成功！")
                print_info(f"Token类型: {data['token_type']}")
                print_info(f"响应时间: {response_time:.2f}秒")
                
                # 设置认证头
                self.client.headers["Authorization"] = f"Bearer {self.token}"
                
                # UX反馈
                self.record_ux_feedback(
                    "缺少'记住我'选项，用户需要频繁登录",
                    "important"
                )
                
                self.record_ux_feedback(
                    "应该支持第三方登录（微信、Google等）",
                    "suggestion"
                )
                
                return True
            else:
                print_error(f"登录失败: {response.status_code}")
                print_error(f"错误详情: {response.text}")
                
                # UX反馈
                if response.status_code == 401:
                    self.record_ux_feedback(
                        "密码错误提示应该更具体（如：剩余尝试次数）",
                        "warning"
                    )
                
                return False
                
        except Exception as e:
            print_error(f"登录异常: {str(e)}")
            return False
    
    async def step3_upload_chat(self) -> bool:
        """步骤3: 上传聊天记录"""
        print_step(3, "上传聊天记录")
        
        # 创建测试聊天文件
        chat_data = {
            "messages": [
                {
                    "sender": "小明",
                    "content": "你好！最近怎么样？",
                    "timestamp": "2024-01-01 10:00:00"
                },
                {
                    "sender": "AI助手",
                    "content": "我很好，谢谢关心！今天有什么可以帮助你的吗？",
                    "timestamp": "2024-01-01 10:00:30"
                },
                {
                    "sender": "小明",
                    "content": "我想了解一下人工智能的发展",
                    "timestamp": "2024-01-01 10:01:00"
                },
                {
                    "sender": "AI助手",
                    "content": "人工智能近年来发展迅速，特别是在自然语言处理领域...",
                    "timestamp": "2024-01-01 10:01:30"
                }
            ]
        }
        
        # 写入临时文件
        temp_file = "test_chat_history.json"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        
        print_info(f"上传文件: {temp_file}")
        print_info(f"消息数量: {len(chat_data['messages'])}")
        
        try:
            start_time = time.time()
            with open(temp_file, "rb") as f:
                files = {"file": (temp_file, f, "application/json")}
                response = await self.client.post(
                    f"{self.base_url}/api/upload",
                    files=files
                )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                print_success("文件上传成功！")
                print_info(f"处理消息数: {data.get('message_count', 'N/A')}")
                print_info(f"响应时间: {response_time:.2f}秒")
                
                # UX反馈
                self.record_ux_feedback(
                    "上传进度没有实时显示，大文件时用户体验不好",
                    "important"
                )
                
                self.record_ux_feedback(
                    "应该支持拖拽上传和批量上传",
                    "suggestion"
                )
                
                self.record_ux_feedback(
                    "上传前应该预览文件内容，确认格式正确",
                    "suggestion"
                )
                
                return True
            else:
                print_error(f"上传失败: {response.status_code}")
                print_error(f"错误详情: {response.text}")
                
                # UX反馈
                if response.status_code == 413:
                    self.record_ux_feedback(
                        "文件大小限制错误应该在上传前就提示",
                        "important"
                    )
                
                return False
                
        except Exception as e:
            print_error(f"上传异常: {str(e)}")
            return False
        finally:
            # 清理临时文件
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    async def step4_create_persona(self) -> bool:
        """步骤4: 创建AI人格"""
        print_step(4, "创建AI人格")
        
        persona_data = {
            "name": "知识助手",
            "description": "一个友好、专业的AI知识助手",
            "avatar": "🤖"
        }
        
        print_info(f"人格名称: {persona_data['name']}")
        print_info(f"人格描述: {persona_data['description']}")
        
        try:
            start_time = time.time()
            response = await self.client.post(
                f"{self.base_url}/api/personas/",  # 注意末尾的斜杠
                json=persona_data
            )
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.persona_id = data["id"]
                print_success(f"人格创建成功！ID: {self.persona_id}")
                print_info(f"响应时间: {response_time:.2f}秒")
                
                # UX反馈
                self.record_ux_feedback(
                    "创建人格后应该立即引导用户开始对话",
                    "important"
                )
                
                self.record_ux_feedback(
                    "应该提供人格模板供选择（如：助手、朋友、导师等）",
                    "suggestion"
                )
                
                return True
            else:
                print_error(f"创建失败: {response.status_code}")
                print_error(f"错误详情: {response.text}")
                return False
                
        except Exception as e:
            print_error(f"创建异常: {str(e)}")
            return False
    
    async def step5_chat(self) -> bool:
        """步骤5: 与AI对话"""
        print_step(5, "与AI对话")
        
        if not self.persona_id:
            print_error("没有人格ID，无法对话")
            return False
        
        # 测试多轮对话
        test_messages = [
            "你好，请介绍一下自己",
            "你最擅长什么领域？",
            "能给我一些学习建议吗？"
        ]
        
        success_count = 0
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n{Colors.CYAN}对话轮次 {i}:{Colors.END}")
            print(f"用户: {message}")
            
            try:
                start_time = time.time()
                response = await self.client.post(
                    f"{self.base_url}/api/chat/{self.persona_id}/message",
                    json={"message": message}
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    ai_response = data.get("content", "")
                    print(f"AI: {ai_response[:100]}...")
                    print_info(f"响应时间: {response_time:.2f}秒")
                    success_count += 1
                    
                    # UX反馈
                    if response_time > 3:
                        self.record_ux_feedback(
                            f"AI响应时间过长({response_time:.2f}秒)，需要加载动画",
                            "important"
                        )
                    
                    if i == 1 and len(ai_response) < 50:
                        self.record_ux_feedback(
                            "AI初始回复过于简短，应该更详细地介绍自己",
                            "warning"
                        )
                    
                else:
                    print_error(f"对话失败: {response.status_code}")
                    
                await asyncio.sleep(1)  # 避免请求过快
                
            except Exception as e:
                print_error(f"对话异常: {str(e)}")
        
        # UX反馈
        self.record_ux_feedback(
            "缺少对话历史记录功能，用户无法查看之前的对话",
            "important"
        )
        
        self.record_ux_feedback(
            "应该支持消息编辑和删除功能",
            "suggestion"
        )
        
        self.record_ux_feedback(
            "需要支持导出对话记录",
            "suggestion"
        )
        
        return success_count >= 2  # 至少2轮对话成功
    
    async def step6_test_error_handling(self) -> bool:
        """步骤6: 测试错误处理"""
        print_step(6, "错误处理测试")
        
        print_info("测试各种错误场景...")
        
        # 1. 无效的token
        print("\n1. 测试无效Token:")
        self.client.headers["Authorization"] = "Bearer invalid_token"
        try:
            response = await self.client.get(f"{self.base_url}/api/personas")
            if response.status_code == 401:
                print_success("正确拒绝无效Token")
                
                # UX反馈
                self.record_ux_feedback(
                    "Token过期应该自动刷新，而不是让用户重新登录",
                    "important"
                )
            else:
                print_warning(f"未正确处理无效Token: {response.status_code}")
        except Exception as e:
            print_error(f"异常: {str(e)}")
        
        # 恢复正确的token
        self.client.headers["Authorization"] = f"Bearer {self.token}"
        
        # 2. 不存在的资源
        print("\n2. 测试访问不存在的资源:")
        try:
            response = await self.client.get(f"{self.base_url}/api/personas/nonexistent")
            if response.status_code == 404:
                print_success("正确返回404")
            else:
                print_warning(f"未正确处理不存在的资源: {response.status_code}")
        except Exception as e:
            print_error(f"异常: {str(e)}")
        
        # 3. 无效的请求数据
        print("\n3. 测试无效请求数据:")
        try:
            response = await self.client.post(
                f"{self.base_url}/api/personas/",
                json={"invalid": "data"}
            )
            if response.status_code >= 400:
                print_success("正确拒绝无效数据")
                
                # UX反馈
                error_msg = response.text
                if "Field required" in error_msg:
                    self.record_ux_feedback(
                        "字段验证错误信息应该本地化（中文）",
                        "warning"
                    )
            else:
                print_warning(f"未正确验证数据: {response.status_code}")
        except Exception as e:
            print_error(f"异常: {str(e)}")
        
        return True
    
    def generate_ux_report(self):
        """生成用户体验报告"""
        print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}用户体验反馈报告{Colors.END}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
        
        # 按严重程度分组
        important = [f for f in self.ux_feedback if f["severity"] == "important"]
        warnings = [f for f in self.ux_feedback if f["severity"] == "warning"]
        suggestions = [f for f in self.ux_feedback if f["severity"] == "suggestion"]
        
        if important:
            print(f"\n{Colors.RED}{Colors.BOLD}重要问题 (需要优先解决):{Colors.END}")
            for i, feedback in enumerate(important, 1):
                print(f"{i}. {feedback['feedback']}")
        
        if warnings:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}警告问题 (影响体验):{Colors.END}")
            for i, feedback in enumerate(warnings, 1):
                print(f"{i}. {feedback['feedback']}")
        
        if suggestions:
            print(f"\n{Colors.CYAN}{Colors.BOLD}优化建议 (提升体验):{Colors.END}")
            for i, feedback in enumerate(suggestions, 1):
                print(f"{i}. {feedback['feedback']}")
        
        # 保存报告
        report = {
            "test_time": datetime.now().isoformat(),
            "total_feedback": len(self.ux_feedback),
            "by_severity": {
                "important": len(important),
                "warning": len(warnings),
                "suggestion": len(suggestions)
            },
            "feedback_items": self.ux_feedback
        }
        
        with open("ux_feedback_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n{Colors.GREEN}详细报告已保存到 ux_feedback_report.json{Colors.END}")

async def main():
    """主测试函数"""
    print(f"{Colors.BOLD}🚀 Second Self 完整用户流程测试{Colors.END}")
    print("=" * 60)
    print("测试从用户注册到AI对话的完整流程")
    print("同时收集用户体验改进建议")
    print("=" * 60)
    
    tester = FullFlowTester()
    
    try:
        # 执行测试步骤
        steps = [
            ("用户注册", tester.step1_register),
            ("用户登录", tester.step2_login),
            ("上传聊天记录", tester.step3_upload_chat),
            ("创建AI人格", tester.step4_create_persona),
            ("AI对话", tester.step5_chat),
            ("错误处理", tester.step6_test_error_handling),
        ]
        
        passed_steps = 0
        total_steps = len(steps)
        
        for step_name, step_func in steps:
            result = await step_func()
            if result:
                passed_steps += 1
                print_success(f"{step_name} - 通过")
            else:
                print_error(f"{step_name} - 失败")
                # 继续测试其他步骤，收集更多信息
            
            await asyncio.sleep(1)  # 步骤间暂停
        
        # 显示测试结果
        print(f"\n{Colors.BOLD}测试结果总结:{Colors.END}")
        print(f"总步骤数: {total_steps}")
        print(f"通过步骤: {passed_steps}")
        print(f"失败步骤: {total_steps - passed_steps}")
        print(f"通过率: {passed_steps/total_steps*100:.1f}%")
        
        if passed_steps == total_steps:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ 全流程测试通过！{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  部分步骤失败，请查看详情{Colors.END}")
        
        # 生成用户体验报告
        tester.generate_ux_report()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}测试被中断{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}测试出错: {str(e)}{Colors.END}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())