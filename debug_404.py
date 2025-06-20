#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
404错误调试脚本
"""

import requests
import socket
import subprocess
import sys
import time

def print_info(msg):
    print(f"[INFO] {msg}")

def print_success(msg):
    print(f"[SUCCESS] {msg}")

def print_error(msg):
    print(f"[ERROR] {msg}")

def print_warning(msg):
    print(f"[WARNING] {msg}")

def check_port_listening():
    """检查端口监听状态"""
    print_info("=== 检查端口监听状态 ===")
    
    ports_to_check = [5000, 5001, 8080, 8000]
    
    for port in ports_to_check:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            print_success(f"✅ 端口 {port} 正在监听")
            
            # 尝试获取进程信息
            try:
                cmd = f"lsof -i :{port} 2>/dev/null || netstat -tulpn 2>/dev/null | grep :{port}"
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                if result.stdout:
                    print_info(f"   进程信息: {result.stdout.strip()}")
            except:
                pass
        else:
            print_warning(f"⚠️ 端口 {port} 未监听")
    
    print()

def test_urls():
    """测试不同的URL"""
    print_info("=== 测试URL访问 ===")
    
    base_urls = [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://0.0.0.0:5000"
    ]
    
    endpoints = [
        "/health",
        "/",
        "/api/v1/image/models"
    ]
    
    for base_url in base_urls:
        print_info(f"测试基础URL: {base_url}")
        
        for endpoint in endpoints:
            full_url = base_url + endpoint
            try:
                response = requests.get(full_url, timeout=5)
                print_success(f"✅ {full_url} -> {response.status_code}")
                if response.status_code == 200:
                    print_info(f"   响应: {response.text[:100]}...")
            except requests.exceptions.ConnectionError:
                print_error(f"❌ {full_url} -> 连接失败")
            except requests.exceptions.Timeout:
                print_error(f"❌ {full_url} -> 超时")
            except Exception as e:
                print_error(f"❌ {full_url} -> {str(e)}")
        
        print()

def check_flask_routes():
    """检查Flask路由"""
    print_info("=== 检查Flask路由 ===")
    
    try:
        from run import app
        
        print_success("✅ Flask应用导入成功")
        print_info(f"应用名称: {app.name}")
        print_info(f"调试模式: {app.debug}")
        
        # 获取所有路由
        print_info("注册的路由:")
        for rule in app.url_map.iter_rules():
            methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
            print_info(f"   {methods:10} {rule.rule}")
        
        # 测试应用上下文中的路由
        with app.test_client() as client:
            print_info("测试路由响应:")
            
            test_routes = ['/health', '/', '/api/v1/image/models']
            
            for route in test_routes:
                try:
                    response = client.get(route)
                    print_success(f"✅ {route} -> {response.status_code}")
                    if response.status_code == 200:
                        print_info(f"   响应: {response.get_data(as_text=True)[:100]}...")
                except Exception as e:
                    print_error(f"❌ {route} -> {str(e)}")
        
    except Exception as e:
        print_error(f"❌ Flask应用检查失败: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print()

def check_process_info():
    """检查进程信息"""
    print_info("=== 检查Python进程 ===")
    
    try:
        # 查找Python进程
        cmd = "ps aux | grep python | grep -v grep"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print_info("运行中的Python进程:")
            for line in result.stdout.strip().split('\n'):
                if 'run.py' in line or 'flask' in line or 'gunicorn' in line:
                    print_info(f"   {line}")
        else:
            print_warning("未找到相关Python进程")
            
    except Exception as e:
        print_error(f"进程检查失败: {str(e)}")
    
    print()

def check_network_config():
    """检查网络配置"""
    print_info("=== 检查网络配置 ===")
    
    try:
        # 检查本地网络接口
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        
        print_info(f"主机名: {hostname}")
        print_info(f"本地IP: {local_ip}")
        
        # 检查localhost解析
        localhost_ip = socket.gethostbyname('localhost')
        print_info(f"localhost解析: {localhost_ip}")
        
    except Exception as e:
        print_error(f"网络配置检查失败: {str(e)}")
    
    print()

def provide_solutions():
    """提供解决方案"""
    print_info("=== 可能的解决方案 ===")
    
    print("1. 检查服务是否真的在运行:")
    print("   ps aux | grep python")
    print("   netstat -tulpn | grep :5000")
    print()
    
    print("2. 检查防火墙设置:")
    print("   sudo ufw status")
    print("   sudo iptables -L")
    print()
    
    print("3. 尝试不同的启动方式:")
    print("   python run.py")
    print("   flask run --host=0.0.0.0 --port=5000")
    print("   gunicorn -b 0.0.0.0:5000 run:app")
    print()
    
    print("4. 检查配置文件:")
    print("   cat .env")
    print("   python -c \"from app.config import Config; print(Config.HOST, Config.PORT)\"")
    print()
    
    print("5. 测试本地连接:")
    print("   curl -v http://localhost:5000/health")
    print("   curl -v http://127.0.0.1:5000/health")
    print("   telnet localhost 5000")
    print()

def main():
    """主函数"""
    print("🔍 Flask 404错误诊断工具")
    print("=" * 50)
    
    # 检查端口监听
    check_port_listening()
    
    # 检查进程信息
    check_process_info()
    
    # 检查网络配置
    check_network_config()
    
    # 检查Flask路由
    check_flask_routes()
    
    # 测试URL访问
    test_urls()
    
    # 提供解决方案
    provide_solutions()
    
    print("=" * 50)
    print("🎯 诊断完成")

if __name__ == "__main__":
    main()
