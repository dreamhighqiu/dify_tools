#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
"""

import requests
import json

def test_health_check():
    """测试健康检查接口"""
    try:
        response = requests.get('http://localhost:5000/health')
        print("健康检查测试:")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
        print("-" * 50)
    except Exception as e:
        print(f"健康检查测试失败: {e}")

def test_image_generation():
    """测试图像生成接口"""
    url = "http://localhost:5000/get_img_info"
    
    # 测试数据
    test_data = {
        "url": "https://example.com/test-image.jpg",
        "prompt": "一只可爱的小猫"
    }
    
    try:
        print("图像生成测试:")
        print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=test_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        print("-" * 50)
    except Exception as e:
        print(f"图像生成测试失败: {e}")

def test_invalid_request():
    """测试无效请求"""
    url = "http://localhost:5000/get_img_info"
    
    # 测试缺少参数
    test_data = {
        "url": "https://example.com/test-image.jpg"
        # 缺少prompt参数
    }
    
    try:
        print("无效请求测试:")
        print(f"请求数据: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        response = requests.post(url, json=test_data)
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        print("-" * 50)
    except Exception as e:
        print(f"无效请求测试失败: {e}")

if __name__ == "__main__":
    print("开始API测试...")
    print("=" * 50)
    
    # 运行测试
    test_health_check()
    test_image_generation()
    test_invalid_request()
    
    print("测试完成!") 