#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库API测试脚本
"""

import requests
import json

def test_database_api():
    """测试数据库API的两种格式"""
    
    base_url = "http://localhost:5000"
    
    # 测试数据
    sql_query = "SELECT g.goods_id, g.goods_name, g.price, i.stock_quantity FROM goods g JOIN inventory i ON g.goods_id = i.goods_id"
    
    connection_info = {
        "host": "3.96.167.248",
        "port": 3306,
        "user": "ai_mysql",
        "password": "qianwei123",
        "database": "ai_db",
        "charset": "utf8mb4"
    }
    
    print("🧪 测试数据库API")
    print("=" * 50)
    
    # 格式1：嵌套格式（推荐）
    print("1️⃣ 测试嵌套格式（推荐）")
    print("-" * 30)
    
    nested_payload = {
        "sql": sql_query,
        "connection": connection_info,
        "timeout": 30
    }
    
    print("请求格式:")
    print(json.dumps(nested_payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/database/execute",
            json=nested_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print("响应:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print("✅ 嵌套格式测试成功")
        else:
            print("❌ 嵌套格式测试失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print("\n" + "=" * 50)
    
    # 格式2：扁平化格式
    print("2️⃣ 测试扁平化格式")
    print("-" * 30)
    
    flat_payload = {
        "sql": sql_query,
        "host": connection_info["host"],
        "port": connection_info["port"],
        "user": connection_info["user"],
        "password": connection_info["password"],
        "database": connection_info["database"],
        "charset": connection_info["charset"],
        "timeout": 30
    }
    
    print("请求格式:")
    print(json.dumps(flat_payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/database/execute",
            json=flat_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print("响应:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print("✅ 扁平化格式测试成功")
        else:
            print("❌ 扁平化格式测试失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print("\n" + "=" * 50)

def test_connection_api():
    """测试连接测试API"""
    
    base_url = "http://localhost:5000"
    
    connection_info = {
        "host": "3.96.167.248",
        "port": 3306,
        "user": "ai_mysql",
        "password": "qianwei123",
        "database": "ai_db"
    }
    
    print("3️⃣ 测试连接测试API")
    print("-" * 30)
    
    payload = {
        "connection": connection_info
    }
    
    print("请求格式:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/database/test-connection",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"状态码: {response.status_code}")
        print("响应:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        if response.status_code == 200:
            print("✅ 连接测试成功")
        else:
            print("❌ 连接测试失败")
            
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")

def test_validation_errors():
    """测试参数验证错误"""
    
    base_url = "http://localhost:5000"
    
    print("\n" + "=" * 50)
    print("4️⃣ 测试参数验证")
    print("-" * 30)
    
    # 测试缺少必需参数
    invalid_payloads = [
        {
            "name": "缺少sql参数",
            "data": {
                "host": "localhost",
                "user": "root",
                "password": "password",
                "database": "test"
            }
        },
        {
            "name": "缺少连接信息",
            "data": {
                "sql": "SELECT 1"
            }
        },
        {
            "name": "空请求体",
            "data": {}
        }
    ]
    
    for test_case in invalid_payloads:
        print(f"测试: {test_case['name']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/database/execute",
                json=test_case['data'],
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            print(f"状态码: {response.status_code}")
            if response.status_code == 400:
                print("✅ 正确返回400错误")
                error_response = response.json()
                print(f"错误信息: {error_response.get('message', 'N/A')}")
            else:
                print("❌ 未返回预期的400错误")
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
        
        print()

def main():
    """主函数"""
    print("🔧 数据库API修复验证")
    print("=" * 60)
    
    # 测试数据库执行API
    test_database_api()
    
    # 测试连接测试API
    test_connection_api()
    
    # 测试参数验证
    test_validation_errors()
    
    print("=" * 60)
    print("🎯 测试完成")
    print()
    print("💡 使用说明:")
    print("1. 推荐使用嵌套格式（connection对象）")
    print("2. 也支持扁平化格式（直接在根级别传递连接参数）")
    print("3. 两种格式功能完全相同")

if __name__ == "__main__":
    main()
