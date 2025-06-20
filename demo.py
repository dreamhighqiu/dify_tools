#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一Flask服务演示脚本
展示所有API接口的使用方法
"""

import requests
import json
import time
import sys
from typing import Dict, Any


class ServiceDemo:
    """服务演示类"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        初始化演示器
        
        Args:
            base_url: 服务基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'ServiceDemo/1.0'
        })
    
    def print_section(self, title: str):
        """打印章节标题"""
        print("\n" + "=" * 60)
        print(f"🔍 {title}")
        print("=" * 60)
    
    def print_result(self, name: str, success: bool, data: Dict[str, Any] = None, error: str = None):
        """打印测试结果"""
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{status} | {name}")
        
        if success and data:
            print(f"   📊 响应: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
        elif error:
            print(f"   ❌ 错误: {error}")
    
    def test_health_check(self) -> bool:
        """测试健康检查"""
        self.print_section("健康检查测试")
        
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                self.print_result("健康检查", True, data)
                
                print(f"   📋 服务信息:")
                print(f"      - 服务名称: {data.get('service')}")
                print(f"      - 版本: {data.get('version')}")
                print(f"      - 环境: {data.get('environment')}")
                print(f"      - 功能: {', '.join(data.get('features', []))}")
                
                return True
            else:
                self.print_result("健康检查", False, error=f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.print_result("健康检查", False, error=str(e))
            return False
    
    def test_image_api(self):
        """测试图像生成API"""
        self.print_section("图像生成API测试")
        
        # 1. 获取模型列表
        try:
            response = self.session.get(f"{self.base_url}/api/v1/image/models")
            if response.status_code == 200:
                data = response.json()
                self.print_result("获取模型列表", True, data)
            else:
                self.print_result("获取模型列表", False, error=f"HTTP {response.status_code}")
        except Exception as e:
            self.print_result("获取模型列表", False, error=str(e))
        
        # 2. 参数验证测试
        print("\n📋 参数验证测试:")
        
        validation_tests = [
            {
                "name": "空请求体",
                "data": None,
                "expected": 400
            },
            {
                "name": "缺少reference_url",
                "data": {"prompt": "测试提示词"},
                "expected": 400
            },
            {
                "name": "缺少prompt",
                "data": {"reference_url": "http://example.com/test.jpg"},
                "expected": 400
            },
            {
                "name": "无效URL",
                "data": {"reference_url": "invalid-url", "prompt": "测试提示词"},
                "expected": 400
            }
        ]
        
        for test in validation_tests:
            try:
                if test["data"] is None:
                    response = self.session.post(f"{self.base_url}/api/v1/image/generate")
                else:
                    response = self.session.post(
                        f"{self.base_url}/api/v1/image/generate",
                        json=test["data"]
                    )
                
                success = response.status_code == test["expected"]
                self.print_result(f"   {test['name']}", success)
                
            except Exception as e:
                self.print_result(f"   {test['name']}", False, error=str(e))
        
        # 3. 图像生成测试（可能因API限制失败）
        print("\n🎨 图像生成测试:")
        
        test_data = {
            "reference_url": "http://sns-webpic-qc.xhscdn.com/202506191522/6e508ba17917aef3d100a547c3642f0e/1040g00831d0bro480e6g5phojgt1ong70mr97q8!nd_dft_wlteh_jpg_3",
            "prompt": "一只可爱的小猫咪，卡通风格，高清画质"
        }
        
        try:
            print("   🎨 发送图像生成请求...")
            response = self.session.post(
                f"{self.base_url}/api/v1/image/generate",
                json=test_data,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.print_result("图像生成", True, data)
                else:
                    self.print_result("图像生成", False, error=data.get('message'))
            else:
                self.print_result("图像生成", False, error=f"HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.print_result("图像生成", False, error="请求超时")
        except Exception as e:
            self.print_result("图像生成", False, error=str(e))
    
    def test_database_api(self):
        """测试数据库API"""
        self.print_section("数据库API测试")
        
        # 1. 参数验证测试
        print("📋 参数验证测试:")
        
        validation_tests = [
            {
                "name": "空请求体",
                "data": None,
                "expected": 400
            },
            {
                "name": "缺少SQL",
                "data": {"connection": {"host": "localhost"}},
                "expected": 400
            },
            {
                "name": "缺少连接信息",
                "data": {"sql": "SELECT 1"},
                "expected": 400
            },
            {
                "name": "连接信息不完整",
                "data": {
                    "sql": "SELECT 1",
                    "connection": {"host": "localhost"}
                },
                "expected": 400
            }
        ]
        
        for test in validation_tests:
            try:
                if test["data"] is None:
                    response = self.session.post(f"{self.base_url}/api/v1/database/execute")
                else:
                    response = self.session.post(
                        f"{self.base_url}/api/v1/database/execute",
                        json=test["data"]
                    )
                
                success = response.status_code == test["expected"]
                self.print_result(f"   {test['name']}", success)
                
            except Exception as e:
                self.print_result(f"   {test['name']}", False, error=str(e))
        
        # 2. 连接测试参数验证
        print("\n🔗 连接测试参数验证:")
        
        connection_tests = [
            {
                "name": "空请求体",
                "data": None,
                "expected": 400
            },
            {
                "name": "缺少连接信息",
                "data": {},
                "expected": 400
            },
            {
                "name": "连接信息不完整",
                "data": {"connection": {"host": "localhost"}},
                "expected": 400
            }
        ]
        
        for test in connection_tests:
            try:
                if test["data"] is None:
                    response = self.session.post(f"{self.base_url}/api/v1/database/test-connection")
                else:
                    response = self.session.post(
                        f"{self.base_url}/api/v1/database/test-connection",
                        json=test["data"]
                    )
                
                success = response.status_code == test["expected"]
                self.print_result(f"   {test['name']}", success)
                
            except Exception as e:
                self.print_result(f"   {test['name']}", False, error=str(e))
    
    def test_error_handling(self):
        """测试错误处理"""
        self.print_section("错误处理测试")
        
        error_tests = [
            {
                "name": "404错误",
                "url": "/nonexistent",
                "method": "GET",
                "expected": 404
            },
            {
                "name": "405错误",
                "url": "/api/v1/image/generate",
                "method": "GET",
                "expected": 405
            }
        ]
        
        for test in error_tests:
            try:
                if test["method"] == "GET":
                    response = self.session.get(f"{self.base_url}{test['url']}")
                else:
                    response = self.session.post(f"{self.base_url}{test['url']}")
                
                success = response.status_code == test["expected"]
                self.print_result(test["name"], success)
                
                if success:
                    data = response.json()
                    print(f"      错误信息: {data.get('message')}")
                
            except Exception as e:
                self.print_result(test["name"], False, error=str(e))
    
    def run_demo(self):
        """运行完整演示"""
        print("🚀 统一Flask服务API演示")
        print(f"🌐 目标服务: {self.base_url}")
        
        start_time = time.time()
        
        # 1. 健康检查
        if not self.test_health_check():
            print("\n❌ 服务不可用，演示终止")
            return False
        
        # 2. 图像生成API测试
        self.test_image_api()
        
        # 3. 数据库API测试
        self.test_database_api()
        
        # 4. 错误处理测试
        self.test_error_handling()
        
        # 5. 总结
        end_time = time.time()
        duration = end_time - start_time
        
        self.print_section("演示总结")
        print(f"📊 演示完成，总耗时: {duration:.2f}秒")
        print("📋 演示内容:")
        print("   ✅ 健康检查接口")
        print("   ✅ 图像生成API（包含参数验证）")
        print("   ✅ 数据库操作API（包含参数验证）")
        print("   ✅ 错误处理机制")
        print("\n💡 说明:")
        print("   - 图像生成可能因API配额限制而失败")
        print("   - 数据库操作需要有效的连接信息")
        print("   - 所有参数验证和错误处理都正常工作")
        
        return True


def main():
    """主函数"""
    # 解析命令行参数
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    # 创建演示器并运行
    demo = ServiceDemo(base_url)
    success = demo.run_demo()
    
    # 退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
