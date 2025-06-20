#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API测试脚本
"""

import requests
import json
import time

def test_health():
    """测试健康检查接口"""
    print("🔍 测试健康检查接口")
    print("-" * 30)
    
    urls = [
        "http://localhost:5000/health",
        "http://127.0.0.1:5000/health",
        "http://0.0.0.0:5000/health"
    ]
    
    for url in urls:
        try:
            print(f"测试: {url}")
            response = requests.get(url, timeout=5)
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
                print("✅ 健康检查成功")
                return True
            else:
                print(f"❌ 状态码错误: {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("❌ 连接失败 - 服务可能未启动")
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
        
        print()
    
    return False

def test_image_models():
    """测试图像模型接口"""
    print("🔍 测试图像模型接口")
    print("-" * 30)
    
    url = "http://localhost:5000/api/v1/image/models"
    
    try:
        print(f"测试: {url}")
        response = requests.get(url, timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
            print("✅ 模型列表获取成功")
            return True
        else:
            print(f"❌ 状态码错误: {response.status_code}")
            print(f"响应内容: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 服务可能未启动")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()
    return False

def test_root():
    """测试根路径"""
    print("🔍 测试根路径")
    print("-" * 30)
    
    url = "http://localhost:5000/"
    
    try:
        print(f"测试: {url}")
        response = requests.get(url, timeout=5)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text[:200]}...")
        
        if response.status_code == 404:
            print("ℹ️ 根路径返回404是正常的（未定义根路由）")
        
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败 - 服务可能未启动")
    except Exception as e:
        print(f"❌ 请求失败: {str(e)}")
    
    print()

def main():
    """主函数"""
    print("🧪 Flask API测试工具")
    print("=" * 40)
    
    # 等待服务启动
    print("等待服务启动...")
    time.sleep(2)
    
    # 测试健康检查
    health_ok = test_health()
    
    if health_ok:
        # 测试其他接口
        test_image_models()
    else:
        print("⚠️ 健康检查失败，跳过其他测试")
    
    # 测试根路径
    test_root()
    
    print("=" * 40)
    print("🎯 测试完成")
    
    if not health_ok:
        print("\n💡 故障排除建议:")
        print("1. 检查服务是否启动: ps aux | grep python")
        print("2. 检查端口监听: netstat -tulpn | grep :5000")
        print("3. 运行诊断脚本: python debug_404.py")
        print("4. 查看服务日志")

if __name__ == "__main__":
    main()
