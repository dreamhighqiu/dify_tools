#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络和MySQL连接测试
"""

import requests
import json
import time

def test_network_connectivity():
    """测试网络连接"""
    print("🌐 测试网络连接")
    print("-" * 30)
    
    url = "http://localhost:5000/api/v1/database/network-test"
    payload = {
        "host": "3.96.167.248",
        "port": 3306
    }
    
    try:
        print(f"测试URL: {url}")
        print(f"请求数据: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 网络连接测试成功")
            return True
        else:
            print("❌ 网络连接测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 网络测试请求失败: {str(e)}")
        return False

def test_mysql_connection():
    """测试MySQL连接"""
    print("\n🔗 测试MySQL连接")
    print("-" * 30)
    
    url = "http://localhost:5000/api/v1/database/test-connection"
    payload = {
        "connection": {
            "host": "3.96.167.248",
            "port": 3306,
            "user": "ai_mysql",
            "password": "qianwei123",
            "database": "ai_db",
            "charset": "utf8mb4"
        }
    }
    
    try:
        print(f"测试URL: {url}")
        print("请求数据: (隐藏密码)")
        
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=90  # 增加超时时间
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ MySQL连接测试成功")
            return True
        else:
            print("❌ MySQL连接测试失败")
            return False
            
    except Exception as e:
        print(f"❌ MySQL连接测试请求失败: {str(e)}")
        return False

def test_sql_execution():
    """测试SQL执行"""
    print("\n📊 测试SQL执行")
    print("-" * 30)
    
    url = "http://localhost:5000/api/v1/database/execute"
    
    # 测试简单查询
    simple_payload = {
        "sql": "SELECT 1 as test_value, NOW() as current_time",
        "host": "3.96.167.248",
        "port": 3306,
        "user": "ai_mysql",
        "password": "qianwei123",
        "database": "ai_db",
        "charset": "utf8mb4",
        "timeout": 60
    }
    
    try:
        print("1. 测试简单查询")
        print(f"SQL: {simple_payload['sql']}")
        
        response = requests.post(
            url,
            json=simple_payload,
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 简单查询成功")
        else:
            print("❌ 简单查询失败")
            return False
            
    except Exception as e:
        print(f"❌ 简单查询请求失败: {str(e)}")
        return False
    
    # 测试复杂查询
    complex_payload = {
        "sql": "SELECT g.goods_id, g.goods_name, g.price, i.stock_quantity FROM goods g JOIN inventory i ON g.goods_id = i.goods_id LIMIT 5",
        "host": "3.96.167.248",
        "port": 3306,
        "user": "ai_mysql",
        "password": "qianwei123",
        "database": "ai_db",
        "charset": "utf8mb4",
        "timeout": 60
    }
    
    try:
        print("\n2. 测试复杂查询")
        print(f"SQL: {complex_payload['sql']}")
        
        response = requests.post(
            url,
            json=complex_payload,
            headers={"Content-Type": "application/json"},
            timeout=90
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if response.status_code == 200:
            print("✅ 复杂查询成功")
            return True
        else:
            print("❌ 复杂查询失败")
            return False
            
    except Exception as e:
        print(f"❌ 复杂查询请求失败: {str(e)}")
        return False

def test_health_check():
    """测试健康检查"""
    print("\n❤️ 测试健康检查")
    print("-" * 30)
    
    url = "http://localhost:5000/health"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
            print("✅ 健康检查成功")
            return True
        else:
            print("❌ 健康检查失败")
            return False
            
    except Exception as e:
        print(f"❌ 健康检查请求失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🧪 网络和MySQL连接综合测试")
    print("=" * 50)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 1. 健康检查
    health_ok = test_health_check()
    
    if not health_ok:
        print("\n❌ 服务未正常启动，请检查服务状态")
        return
    
    # 2. 网络连接测试
    network_ok = test_network_connectivity()
    
    if not network_ok:
        print("\n❌ 网络连接失败，无法继续MySQL测试")
        print("\n💡 建议:")
        print("1. 检查目标服务器是否可达")
        print("2. 检查防火墙设置")
        print("3. 确认端口3306是否开放")
        return
    
    # 3. MySQL连接测试
    mysql_ok = test_mysql_connection()
    
    if not mysql_ok:
        print("\n❌ MySQL连接失败")
        print("\n💡 建议:")
        print("1. 检查MySQL服务是否运行")
        print("2. 检查用户权限设置")
        print("3. 检查MySQL配置文件")
        return
    
    # 4. SQL执行测试
    sql_ok = test_sql_execution()
    
    if sql_ok:
        print("\n🎉 所有测试通过！")
        print("✅ 网络连接正常")
        print("✅ MySQL连接正常")
        print("✅ SQL执行正常")
    else:
        print("\n⚠️ SQL执行测试失败")
    
    print("\n" + "=" * 50)
    print("🎯 测试完成")

if __name__ == "__main__":
    main()
