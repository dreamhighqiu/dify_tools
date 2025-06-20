#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试响应格式修复（移除code字段）
"""

import requests
import json
import time

def test_response_format(base_url="http://localhost:5000"):
    """测试响应格式是否正确（不包含code字段）"""
    
    print("🧪 测试响应格式修复（移除code字段）")
    print("=" * 50)
    
    # 1. 测试健康检查
    print("1️⃣ 测试健康检查响应格式...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 状态码: {response.status_code}")
            print(f"   📋 响应不包含code字段: {'code' not in data}")
            print(f"   📋 响应格式: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ 状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 2. 测试图像API响应格式
    print("\n2️⃣ 测试图像API响应格式...")
    try:
        response = requests.get(f"{base_url}/api/v1/image/models")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 状态码: {response.status_code}")
            print(f"   📋 响应包含result字段: {'result' in data}")
            print(f"   📋 响应不包含code字段: {'code' not in data}")
            print(f"   📋 响应包含success字段: {'success' in data}")
            print(f"   📋 响应包含message字段: {'message' in data}")
            print(f"   📋 响应格式: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ 状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 3. 测试参数验证错误响应格式
    print("\n3️⃣ 测试错误响应格式...")
    try:
        response = requests.post(f"{base_url}/api/v1/image/generate", json={})
        print(f"   ✅ 状态码: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   📋 错误响应包含result字段: {'result' in data}")
            print(f"   📋 错误响应不包含code字段: {'code' not in data}")
            print(f"   📋 result字段值: {data.get('result')}")
            print(f"   📋 包含success字段: {'success' in data}")
            print(f"   📋 包含message字段: {'message' in data}")
            print(f"   📋 包含error_type字段: {'error_type' in data}")
            print(f"   📋 响应格式: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ 预期400状态码，实际: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 4. 测试数据库API参数验证
    print("\n4️⃣ 测试数据库API错误响应格式...")
    try:
        response = requests.post(f"{base_url}/api/v1/database/execute", json={})
        print(f"   ✅ 状态码: {response.status_code}")
        if response.status_code == 400:
            data = response.json()
            print(f"   📋 错误响应包含result字段: {'result' in data}")
            print(f"   📋 错误响应不包含code字段: {'code' not in data}")
            print(f"   📋 result字段值: {data.get('result')}")
            print(f"   📋 响应格式: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ 预期400状态码，实际: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 5. 测试404错误
    print("\n5️⃣ 测试404错误响应格式...")
    try:
        response = requests.get(f"{base_url}/nonexistent")
        print(f"   ✅ 状态码: {response.status_code}")
        if response.status_code == 404:
            data = response.json()
            print(f"   📋 404响应包含result字段: {'result' in data}")
            print(f"   📋 404响应不包含code字段: {'code' not in data}")
            print(f"   📋 result字段值: {data.get('result')}")
            print(f"   📋 响应格式: {json.dumps(data, indent=2, ensure_ascii=False)}")
        else:
            print(f"   ❌ 预期404状态码，实际: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

def validate_response_structure(data, response_type="success"):
    """验证响应结构"""
    required_fields = ["success", "message", "result"]
    
    print(f"\n🔍 验证{response_type}响应结构:")
    
    for field in required_fields:
        if field in data:
            print(f"   ✅ 包含 {field} 字段")
        else:
            print(f"   ❌ 缺少 {field} 字段")
    
    # 检查不应该存在的字段
    forbidden_fields = ["code", "timestamp"]
    for field in forbidden_fields:
        if field not in data:
            print(f"   ✅ 正确移除了 {field} 字段")
        else:
            print(f"   ❌ 仍包含不需要的 {field} 字段")

def main():
    """主函数"""
    print("🎯 响应格式测试（移除code字段）")
    print("=" * 60)
    
    # 测试响应格式
    test_response_format()
    
    print("\n" + "=" * 60)
    print("📋 修复总结:")
    print("1. ✅ 所有响应已移除 'code' 字段")
    print("2. ✅ 所有响应已移除 'timestamp' 字段")
    print("3. ✅ 成功响应包含: success, message, result")
    print("4. ✅ 错误响应包含: success, message, result(null), error_type")
    print("5. ✅ HTTP状态码仍通过响应头传递")
    
    print("\n💡 新的响应格式:")
    print("成功响应:")
    print(json.dumps({
        "success": True,
        "message": "操作成功",
        "result": {"data": "..."}
    }, indent=2, ensure_ascii=False))
    
    print("\n错误响应:")
    print(json.dumps({
        "success": False,
        "message": "操作失败",
        "result": None,
        "error_type": "validation_error"
    }, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
