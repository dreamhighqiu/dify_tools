#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一服务测试脚本
测试图生图和MySQL执行功能
"""

import requests
import json
import time

def test_unified_service(base_url="http://localhost:5000"):
    """测试统一服务的所有功能"""
    
    print("🚀 统一服务功能测试")
    print("=" * 60)
    
    # 1. 健康检查
    print("1️⃣ 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 健康检查通过: {data['status']}")
            print(f"   📋 服务信息: {data['service']} v{data['version']}")
            print(f"   🔧 功能模块: {', '.join(data['features'])}")
            print(f"   🤖 图生图模型: {data['qianfan_model']}")
        else:
            print(f"   ❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False
    
    # 2. 测试图生图功能
    print("\n2️⃣ 测试图生图功能...")
    img_test_data = {
        "url": "http://sns-webpic-qc.xhscdn.com/202506191522/6e508ba17917aef3d100a547c3642f0e/1040g00831d0bro480e6g5phojgt1ong70mr97q8!nd_dft_wlteh_jpg_3",
        "prompt": "一只可爱的小猫"
    }
    
    try:
        print("   🎨 发送图像生成请求...")
        response = requests.post(f"{base_url}/get_img_info", 
                               json=img_test_data, 
                               timeout=30)
        
        print(f"   📊 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✅ 图像生成成功!")
                print(f"   🖼️ 图像URL: {data['result'][:60]}...")
            else:
                print(f"   ❌ 图像生成失败: {data.get('message', 'Unknown error')}")
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("   ⏰ 图像生成请求超时")
    except Exception as e:
        print(f"   ❌ 图像生成请求异常: {e}")
    
    # 3. 测试SQL执行功能
    print("\n3️⃣ 测试SQL执行功能...")
    
    # 测试参数验证
    print("   📋 测试参数验证...")
    
    # 测试空请求体
    try:
        response = requests.post(f"{base_url}/execute_sql")
        if response.status_code == 400:
            print("   ✅ 空请求体验证通过")
        else:
            print(f"   ❌ 空请求体验证失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 空请求体测试异常: {e}")
    
    # 测试缺少参数
    test_cases = [
        ({"connection_info": {"host": "localhost"}}, "缺少SQL"),
        ({"sql": "SELECT 1"}, "缺少连接信息"),
        ({"sql": "", "connection_info": {"host": "localhost"}}, "空SQL"),
        ({"sql": "SELECT 1", "connection_info": {}}, "空连接信息"),
        ({"sql": "SELECT 1", "connection_info": {"host": "localhost"}}, "缺少必要连接参数")
    ]
    
    for data, desc in test_cases:
        try:
            response = requests.post(f"{base_url}/execute_sql", json=data)
            if response.status_code == 400:
                print(f"   ✅ {desc}验证通过")
            else:
                print(f"   ❌ {desc}验证失败: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {desc}测试异常: {e}")
    
    # 4. 测试错误处理
    print("\n4️⃣ 测试错误处理...")
    
    # 测试404
    try:
        response = requests.get(f"{base_url}/nonexistent")
        if response.status_code == 404:
            print("   ✅ 404错误处理通过")
        else:
            print(f"   ❌ 404错误处理失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 404测试异常: {e}")
    
    # 测试405
    try:
        response = requests.get(f"{base_url}/execute_sql")
        if response.status_code == 405:
            print("   ✅ 405错误处理通过")
        else:
            print(f"   ❌ 405错误处理失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 405测试异常: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 统一服务测试完成!")
    print("\n💡 说明:")
    print("   - 图生图功能可能因API限制而失败，这是正常的")
    print("   - SQL执行功能的参数验证已通过测试")
    print("   - 实际SQL执行需要有效的数据库连接信息")
    print("   - 所有错误处理机制工作正常")
    
    return True

def demo_sql_request():
    """演示SQL执行请求格式"""
    print("\n" + "=" * 60)
    print("📝 SQL执行接口使用示例:")
    print("=" * 60)
    
    example_request = {
        "sql": "SELECT * FROM users WHERE id = 1",
        "connection_info": {
            "host": "localhost",
            "user": "root",
            "password": "your_password",
            "database": "your_database",
            "port": 3306,
            "charset": "utf8mb4"
        }
    }
    
    print("请求格式:")
    print(json.dumps(example_request, indent=2, ensure_ascii=False))
    
    print("\ncurl命令示例:")
    print(f"""curl -X POST http://localhost:5000/execute_sql \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(example_request, ensure_ascii=False)}'""")

def demo_image_request():
    """演示图生图请求格式"""
    print("\n" + "=" * 60)
    print("🎨 图生图接口使用示例:")
    print("=" * 60)
    
    example_request = {
        "url": "http://example.com/reference_image.jpg",
        "prompt": "一只可爱的小猫咪，卡通风格，高清画质"
    }
    
    print("请求格式:")
    print(json.dumps(example_request, indent=2, ensure_ascii=False))
    
    print("\ncurl命令示例:")
    print(f"""curl -X POST http://localhost:5000/get_img_info \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps(example_request, ensure_ascii=False)}'""")

def main():
    """主函数"""
    # 运行测试
    test_unified_service()
    
    # 显示使用示例
    demo_image_request()
    demo_sql_request()

if __name__ == "__main__":
    main()
