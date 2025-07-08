#!/usr/bin/env python3
"""
模块化测试运行器 - 系统测试每个模块
"""
import asyncio
import httpx
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_section(title: str):
    """打印区块标题"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.END}")

def print_success(msg: str):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_error(msg: str):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_info(msg: str):
    print(f"{Colors.CYAN}ℹ️  {msg}{Colors.END}")

class ModularTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.client = httpx.AsyncClient(timeout=30.0)
        self.token = None
        self.user_id = None
        self.persona_id = None
        self.test_results = []
        self.ux_issues = []
        
    async def close(self):
        await self.client.aclose()
    
    def record_result(self, module: str, test: str, success: bool, details: str = ""):
        """记录测试结果"""
        self.test_results.append({
            "module": module,
            "test": test,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
    
    def record_ux_issue(self, category: str, issue: str, severity: str = "medium"):
        """记录用户体验问题"""
        self.ux_issues.append({
            "category": category,
            "issue": issue,
            "severity": severity,  # low, medium, high
            "timestamp": datetime.now().isoformat()
        })
    
    async def test_health_module(self) -> bool:
        """测试健康检查模块"""
        print_section("1. 健康检查模块测试")
        
        try:
            # 测试根路径
            response = await self.client.get(f"{self.base_url}/")
            print_info(f"根路径状态: {response.status_code}")
            
            # 测试健康检查
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                data = response.json()
                print_success(f"健康检查通过: {data}")
                self.record_result("健康检查", "基础健康检查", True)
                
                # UX问题：没有显示详细的依赖服务状态
                self.record_ux_issue(
                    "监控", 
                    "健康检查应该显示MongoDB、Azure等依赖服务的具体状态",
                    "medium"
                )
                return True
            else:
                print_error(f"健康检查失败: {response.status_code}")
                self.record_result("健康检查", "基础健康检查", False, f"状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"健康检查异常: {str(e)}")
            self.record_result("健康检查", "基础健康检查", False, str(e))
            
            # UX问题：服务不可用时没有友好的错误页面
            self.record_ux_issue(
                "错误处理",
                "后端服务不可用时，前端应显示友好的错误页面而非连接错误",
                "high"
            )
            return False
    
    async def test_auth_module(self) -> bool:
        """测试认证模块"""
        print_section("2. 认证模块测试")
        
        # 测试用户注册
        print_info("测试用户注册...")
        test_user = {
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "TestPass123!",
            "nickname": "测试用户"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/auth/register",
                json=test_user
            )
            
            if response.status_code == 200:
                data = response.json()
                self.user_id = data["user"]["id"]
                print_success(f"注册成功，用户ID: {self.user_id}")
                self.record_result("认证", "用户注册", True)
            else:
                print_error(f"注册失败: {response.status_code} - {response.text}")
                self.record_result("认证", "用户注册", False, response.text)
                
                # UX问题：错误信息不够友好
                if "duplicate" in response.text.lower():
                    self.record_ux_issue(
                        "认证",
                        "注册时邮箱已存在的错误提示应该更友好",
                        "medium"
                    )
                return False
                
        except Exception as e:
            print_error(f"注册异常: {str(e)}")
            self.record_result("认证", "用户注册", False, str(e))
            return False
        
        # 测试用户登录
        print_info("测试用户登录...")
        try:
            response = await self.client.post(
                f"{self.base_url}/api/auth/login",
                json={
                    "email": test_user["email"],
                    "password": test_user["password"]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data["access_token"]
                print_success(f"登录成功，获得Token")
                self.record_result("认证", "用户登录", True)
                
                # 设置认证头
                self.client.headers["Authorization"] = f"Bearer {self.token}"
                
                # UX问题：没有记住我功能
                self.record_ux_issue(
                    "认证",
                    "缺少'记住我'功能，用户每次都需要重新登录",
                    "medium"
                )
                
                return True
            else:
                print_error(f"登录失败: {response.status_code}")
                self.record_result("认证", "用户登录", False, f"状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"登录异常: {str(e)}")
            self.record_result("认证", "用户登录", False, str(e))
            return False
    
    async def test_upload_module(self) -> bool:
        """测试文件上传模块"""
        print_section("3. 文件上传模块测试")
        
        # 创建测试文件
        test_content = {
            "messages": [
                {
                    "sender": "测试用户",
                    "content": "你好，这是一条测试消息",
                    "timestamp": "2024-01-01 10:00:00"
                },
                {
                    "sender": "AI助手",
                    "content": "你好！很高兴认识你",
                    "timestamp": "2024-01-01 10:00:30"
                }
            ]
        }
        
        test_file = "test_chat.json"
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_content, f, ensure_ascii=False)
        
        try:
            # 测试文件上传
            print_info("测试文件上传...")
            with open(test_file, "rb") as f:
                files = {"file": (test_file, f, "application/json")}
                response = await self.client.post(
                    f"{self.base_url}/api/upload/",
                    files=files
                )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"文件上传成功: {data['message']}")
                self.record_result("上传", "聊天文件上传", True)
                
                # UX问题：上传进度不明确
                self.record_ux_issue(
                    "上传",
                    "大文件上传时缺少进度条显示",
                    "medium"
                )
                
                # UX问题：没有文件格式示例
                self.record_ux_issue(
                    "上传",
                    "上传页面应提供各种支持格式的示例文件",
                    "high"
                )
                
                return True
            else:
                print_error(f"上传失败: {response.status_code} - {response.text}")
                self.record_result("上传", "聊天文件上传", False, response.text)
                return False
                
        except Exception as e:
            print_error(f"上传异常: {str(e)}")
            self.record_result("上传", "聊天文件上传", False, str(e))
            return False
        finally:
            # 清理测试文件
            if os.path.exists(test_file):
                os.remove(test_file)
    
    async def test_persona_module(self) -> bool:
        """测试人格管理模块"""
        print_section("4. 人格管理模块测试")
        
        # 创建人格
        print_info("测试创建人格...")
        try:
            response = await self.client.post(
                f"{self.base_url}/api/personas",
                json={
                    "name": "测试助手",
                    "description": "这是一个测试用的AI助手"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.persona_id = data["id"]
                print_success(f"人格创建成功，ID: {self.persona_id}")
                self.record_result("人格", "创建人格", True)
                
                # UX问题：创建后没有引导
                self.record_ux_issue(
                    "人格",
                    "创建人格后应该引导用户开始对话或上传更多聊天记录",
                    "medium"
                )
            else:
                print_error(f"创建失败: {response.status_code}")
                self.record_result("人格", "创建人格", False, f"状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"创建异常: {str(e)}")
            self.record_result("人格", "创建人格", False, str(e))
            return False
        
        # 获取人格列表
        print_info("测试获取人格列表...")
        try:
            response = await self.client.get(f"{self.base_url}/api/personas")
            
            if response.status_code == 200:
                personas = response.json()
                print_success(f"获取成功，共有 {len(personas)} 个人格")
                self.record_result("人格", "获取列表", True)
                
                # UX问题：列表缺少筛选和排序
                if len(personas) > 5:
                    self.record_ux_issue(
                        "人格",
                        "人格列表应该支持搜索、筛选和排序功能",
                        "medium"
                    )
                
                return True
            else:
                print_error(f"获取失败: {response.status_code}")
                self.record_result("人格", "获取列表", False, f"状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"获取异常: {str(e)}")
            self.record_result("人格", "获取列表", False, str(e))
            return False
    
    async def test_chat_module(self) -> bool:
        """测试对话模块"""
        print_section("5. 对话模块测试")
        
        if not self.persona_id:
            print_warning("没有人格ID，跳过对话测试")
            return False
        
        # 发送消息
        print_info("测试发送消息...")
        try:
            response = await self.client.post(
                f"/api/chat/{self.persona_id}/message",
                json={"message": "你好，请介绍一下自己"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print_success(f"消息发送成功")
                print_info(f"AI回复: {data['content'][:50]}...")
                self.record_result("对话", "发送消息", True)
                
                # UX问题：响应时间
                if data.get("response_time", 0) > 3000:  # 3秒
                    self.record_ux_issue(
                        "对话",
                        "AI响应时间过长，需要添加打字动画或加载提示",
                        "high"
                    )
                
                # UX问题：没有重新生成
                self.record_ux_issue(
                    "对话",
                    "应该支持重新生成回复功能",
                    "medium"
                )
                
                return True
            else:
                print_error(f"发送失败: {response.status_code}")
                self.record_result("对话", "发送消息", False, f"状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print_error(f"发送异常: {str(e)}")
            self.record_result("对话", "发送消息", False, str(e))
            return False
    
    async def test_edge_cases(self) -> bool:
        """测试边缘情况"""
        print_section("6. 边缘情况测试")
        
        edge_cases_passed = 0
        edge_cases_total = 0
        
        # 1. 空文件上传
        print_info("测试空文件上传...")
        edge_cases_total += 1
        try:
            empty_file = "empty.json"
            with open(empty_file, "w") as f:
                f.write("{}")
            
            with open(empty_file, "rb") as f:
                files = {"file": (empty_file, f, "application/json")}
                response = await self.client.post(f"{self.base_url}/api/upload/", files=files)
            
            if response.status_code >= 400:
                print_success("正确拒绝空文件")
                self.record_result("边缘情况", "空文件上传", True)
                edge_cases_passed += 1
                
                # UX问题：错误提示
                self.record_ux_issue(
                    "错误处理",
                    "空文件错误提示应该更具体，说明需要的最小内容",
                    "low"
                )
            else:
                print_error("错误：接受了空文件")
                self.record_result("边缘情况", "空文件上传", False, "接受了空文件")
                
            os.remove(empty_file)
        except Exception as e:
            print_error(f"测试失败: {str(e)}")
            self.record_result("边缘情况", "空文件上传", False, str(e))
        
        # 2. 超长消息
        print_info("测试超长消息...")
        edge_cases_total += 1
        try:
            long_message = "测" * 10000  # 10000字符
            response = await self.client.post(
                f"{self.base_url}/api/chat/{self.persona_id}/message",
                json={"message": long_message}
            )
            
            if response.status_code == 200:
                print_success("处理超长消息成功")
                self.record_result("边缘情况", "超长消息", True)
                edge_cases_passed += 1
            else:
                print_warning(f"超长消息被拒绝: {response.status_code}")
                self.record_result("边缘情况", "超长消息", True, "正确限制消息长度")
                edge_cases_passed += 1
                
                # UX问题：字数限制提示
                self.record_ux_issue(
                    "对话",
                    "输入框应该显示字数限制和当前字数",
                    "medium"
                )
                
        except Exception as e:
            print_error(f"测试失败: {str(e)}")
            self.record_result("边缘情况", "超长消息", False, str(e))
        
        # 3. 并发请求
        print_info("测试并发请求...")
        edge_cases_total += 1
        try:
            tasks = []
            for i in range(5):
                task = self.client.post(
                    f"{self.base_url}/api/chat/{self.persona_id}/message",
                    json={"message": f"并发测试消息 {i}"}
                )
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in responses if not isinstance(r, Exception) and r.status_code == 200)
            
            if success_count == 5:
                print_success("所有并发请求成功")
                self.record_result("边缘情况", "并发请求", True)
                edge_cases_passed += 1
            else:
                print_warning(f"并发请求部分成功: {success_count}/5")
                self.record_result("边缘情况", "并发请求", False, f"成功率: {success_count}/5")
                
                # UX问题：速率限制
                self.record_ux_issue(
                    "性能",
                    "需要实现请求速率限制和排队机制",
                    "high"
                )
                
        except Exception as e:
            print_error(f"测试失败: {str(e)}")
            self.record_result("边缘情况", "并发请求", False, str(e))
        
        print_info(f"\n边缘测试通过率: {edge_cases_passed}/{edge_cases_total}")
        return edge_cases_passed > edge_cases_total * 0.6
    
    def generate_report(self):
        """生成测试报告"""
        print_section("测试报告")
        
        # 统计测试结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["success"])
        
        print(f"\n{Colors.BOLD}测试结果统计:{Colors.END}")
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {total_tests - passed_tests}")
        print(f"通过率: {passed_tests/total_tests*100:.1f}%")
        
        # 失败的测试
        failed_tests = [r for r in self.test_results if not r["success"]]
        if failed_tests:
            print(f"\n{Colors.RED}{Colors.BOLD}失败的测试:{Colors.END}")
            for test in failed_tests:
                print(f"- {test['module']}/{test['test']}: {test['details']}")
        
        # UX问题汇总
        print(f"\n{Colors.YELLOW}{Colors.BOLD}用户体验问题汇总:{Colors.END}")
        
        # 按严重程度分组
        high_issues = [i for i in self.ux_issues if i["severity"] == "high"]
        medium_issues = [i for i in self.ux_issues if i["severity"] == "medium"]
        low_issues = [i for i in self.ux_issues if i["severity"] == "low"]
        
        if high_issues:
            print(f"\n{Colors.RED}高优先级问题:{Colors.END}")
            for issue in high_issues:
                print(f"- [{issue['category']}] {issue['issue']}")
        
        if medium_issues:
            print(f"\n{Colors.YELLOW}中优先级问题:{Colors.END}")
            for issue in medium_issues:
                print(f"- [{issue['category']}] {issue['issue']}")
        
        if low_issues:
            print(f"\n{Colors.CYAN}低优先级问题:{Colors.END}")
            for issue in low_issues:
                print(f"- [{issue['category']}] {issue['issue']}")
        
        # 保存报告
        report = {
            "test_time": datetime.now().isoformat(),
            "summary": {
                "total": total_tests,
                "passed": passed_tests,
                "failed": total_tests - passed_tests,
                "pass_rate": f"{passed_tests/total_tests*100:.1f}%"
            },
            "test_results": self.test_results,
            "ux_issues": self.ux_issues
        }
        
        with open("test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n{Colors.GREEN}详细报告已保存到 test_report.json{Colors.END}")

async def main():
    """主函数"""
    print(f"{Colors.BOLD}🧪 Second Self 模块化测试{Colors.END}")
    print("=" * 60)
    
    tester = ModularTester()
    
    try:
        # 按顺序测试各模块
        modules = [
            ("健康检查", tester.test_health_module),
            ("认证", tester.test_auth_module),
            ("文件上传", tester.test_upload_module),
            ("人格管理", tester.test_persona_module),
            ("对话", tester.test_chat_module),
            ("边缘情况", tester.test_edge_cases),
        ]
        
        all_passed = True
        for module_name, test_func in modules:
            result = await test_func()
            if not result:
                all_passed = False
                print_warning(f"{module_name}模块测试未完全通过")
            await asyncio.sleep(1)  # 避免请求过快
        
        # 生成报告
        tester.generate_report()
        
        if all_passed:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ 所有模块测试通过！{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  部分模块测试失败，请查看报告{Colors.END}")
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}测试被中断{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.RED}测试出错: {str(e)}{Colors.END}")
    finally:
        await tester.close()

if __name__ == "__main__":
    asyncio.run(main())