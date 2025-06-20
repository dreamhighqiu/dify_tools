#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MySQL连接诊断脚本
"""

import socket
import time
import subprocess
import sys
import pymysql
import telnetlib

def print_info(msg):
    print(f"[INFO] {msg}")

def print_success(msg):
    print(f"[SUCCESS] ✅ {msg}")

def print_error(msg):
    print(f"[ERROR] ❌ {msg}")

def print_warning(msg):
    print(f"[WARNING] ⚠️ {msg}")

def test_basic_connectivity():
    """测试基本网络连通性"""
    print_info("=== 1. 基本网络连通性测试 ===")
    
    host = "3.96.167.248"
    port = 3306
    
    # Ping测试
    print_info(f"Ping测试: {host}")
    try:
        result = subprocess.run(['ping', '-c', '3', host], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print_success("Ping测试成功")
            # 提取延迟信息
            lines = result.stdout.split('\n')
            for line in lines:
                if 'time=' in line:
                    print_info(f"   {line.strip()}")
        else:
            print_error("Ping测试失败")
            print_info(f"   错误: {result.stderr}")
    except subprocess.TimeoutExpired:
        print_error("Ping测试超时")
    except Exception as e:
        print_error(f"Ping测试异常: {str(e)}")
    
    print()
    
    # TCP端口连接测试
    print_info(f"TCP端口连接测试: {host}:{port}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        start_time = time.time()
        result = sock.connect_ex((host, port))
        connect_time = time.time() - start_time
        sock.close()
        
        if result == 0:
            print_success(f"TCP连接成功 (耗时: {connect_time:.3f}秒)")
        else:
            print_error(f"TCP连接失败 (错误码: {result})")
    except Exception as e:
        print_error(f"TCP连接测试异常: {str(e)}")
    
    print()

def test_telnet_connection():
    """测试Telnet连接"""
    print_info("=== 2. Telnet连接测试 ===")
    
    host = "3.96.167.248"
    port = 3306
    
    try:
        print_info(f"尝试Telnet连接: {host}:{port}")
        tn = telnetlib.Telnet()
        start_time = time.time()
        tn.open(host, port, timeout=10)
        connect_time = time.time() - start_time
        
        # 读取MySQL握手包
        response = tn.read_some()
        tn.close()
        
        print_success(f"Telnet连接成功 (耗时: {connect_time:.3f}秒)")
        print_info(f"   收到数据长度: {len(response)} 字节")
        
        # 检查是否是MySQL握手包
        if len(response) > 0 and response[0] in [0x0a, 0x09]:  # MySQL协议版本
            print_success("   检测到MySQL协议握手包")
        else:
            print_warning("   未检测到标准MySQL协议握手包")
            
    except Exception as e:
        print_error(f"Telnet连接失败: {str(e)}")
    
    print()

def test_pymysql_connection():
    """测试PyMySQL连接"""
    print_info("=== 3. PyMySQL连接测试 ===")
    
    connection_configs = [
        {
            "name": "标准连接",
            "config": {
                "host": "3.96.167.248",
                "port": 3306,
                "user": "ai_mysql",
                "password": "qianwei123",
                "database": "ai_db",
                "charset": "utf8mb4",
                "connect_timeout": 10
            }
        },
        {
            "name": "长超时连接",
            "config": {
                "host": "3.96.167.248",
                "port": 3306,
                "user": "ai_mysql",
                "password": "qianwei123",
                "database": "ai_db",
                "charset": "utf8mb4",
                "connect_timeout": 30
            }
        },
        {
            "name": "无SSL连接",
            "config": {
                "host": "3.96.167.248",
                "port": 3306,
                "user": "ai_mysql",
                "password": "qianwei123",
                "database": "ai_db",
                "charset": "utf8mb4",
                "connect_timeout": 10,
                "ssl_disabled": True
            }
        }
    ]
    
    for test_config in connection_configs:
        print_info(f"测试: {test_config['name']}")
        
        try:
            start_time = time.time()
            connection = pymysql.connect(**test_config['config'])
            connect_time = time.time() - start_time
            
            # 测试查询
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION() as version, NOW() as current_time")
                result = cursor.fetchone()
                
            connection.close()
            
            print_success(f"   连接成功 (耗时: {connect_time:.3f}秒)")
            print_info(f"   MySQL版本: {result[0]}")
            print_info(f"   服务器时间: {result[1]}")
            
        except pymysql.Error as e:
            print_error(f"   PyMySQL连接失败: {str(e)}")
            print_info(f"   错误类型: {type(e).__name__}")
            
        except Exception as e:
            print_error(f"   连接异常: {str(e)}")
        
        print()

def test_network_routes():
    """测试网络路由"""
    print_info("=== 4. 网络路由测试 ===")
    
    host = "3.96.167.248"
    
    try:
        print_info(f"Traceroute到: {host}")
        
        # 尝试traceroute (macOS/Linux)
        try:
            result = subprocess.run(['traceroute', '-m', '10', host], 
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                print_success("Traceroute成功")
                lines = result.stdout.split('\n')[:10]  # 只显示前10跳
                for line in lines:
                    if line.strip():
                        print_info(f"   {line.strip()}")
            else:
                print_warning("Traceroute未完成")
        except:
            # 尝试tracert (Windows)
            try:
                result = subprocess.run(['tracert', '-h', '10', host], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0:
                    print_success("Tracert成功")
                    lines = result.stdout.split('\n')[:10]
                    for line in lines:
                        if line.strip():
                            print_info(f"   {line.strip()}")
            except:
                print_warning("无法执行路由跟踪")
                
    except Exception as e:
        print_error(f"路由测试异常: {str(e)}")
    
    print()

def test_dns_resolution():
    """测试DNS解析"""
    print_info("=== 5. DNS解析测试 ===")
    
    host = "3.96.167.248"
    
    try:
        print_info(f"解析主机: {host}")
        
        # 检查是否已经是IP地址
        try:
            socket.inet_aton(host)
            print_info("   目标已经是IP地址，无需DNS解析")
        except socket.error:
            # 需要DNS解析
            start_time = time.time()
            ip = socket.gethostbyname(host)
            resolve_time = time.time() - start_time
            print_success(f"   DNS解析成功: {host} -> {ip} (耗时: {resolve_time:.3f}秒)")
        
        # 反向DNS解析
        try:
            start_time = time.time()
            hostname = socket.gethostbyaddr(host)
            resolve_time = time.time() - start_time
            print_success(f"   反向DNS解析: {host} -> {hostname[0]} (耗时: {resolve_time:.3f}秒)")
        except:
            print_info("   反向DNS解析失败（正常情况）")
            
    except Exception as e:
        print_error(f"DNS解析异常: {str(e)}")
    
    print()

def check_local_network():
    """检查本地网络配置"""
    print_info("=== 6. 本地网络配置检查 ===")
    
    try:
        # 获取本地IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        
        print_info(f"本地IP地址: {local_ip}")
        
        # 检查默认网关
        try:
            if sys.platform.startswith('darwin') or sys.platform.startswith('linux'):
                result = subprocess.run(['route', '-n', 'get', 'default'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'gateway:' in line:
                            gateway = line.split(':')[1].strip()
                            print_info(f"默认网关: {gateway}")
                            break
        except:
            print_info("无法获取默认网关信息")
            
    except Exception as e:
        print_error(f"本地网络检查异常: {str(e)}")
    
    print()

def provide_solutions():
    """提供解决方案"""
    print_info("=== 7. 可能的解决方案 ===")
    
    print("🔧 网络连接问题解决方案:")
    print()
    print("1. 检查防火墙设置:")
    print("   - 确保本地防火墙允许出站3306端口")
    print("   - 确保目标服务器防火墙允许入站3306端口")
    print()
    print("2. 检查MySQL服务器配置:")
    print("   - 确认MySQL服务正在运行")
    print("   - 检查bind-address配置（应该是0.0.0.0或具体IP）")
    print("   - 确认端口3306正确开放")
    print()
    print("3. 网络环境检查:")
    print("   - 如果在公司网络，检查是否有代理或限制")
    print("   - 尝试使用VPN或其他网络环境")
    print("   - 联系网络管理员确认端口访问权限")
    print()
    print("4. MySQL用户权限:")
    print("   - 确认用户ai_mysql有远程连接权限")
    print("   - 检查MySQL用户表中的host字段")
    print("   - 执行: SELECT user,host FROM mysql.user WHERE user='ai_mysql';")
    print()
    print("5. 临时解决方案:")
    print("   - 增加连接超时时间")
    print("   - 使用SSH隧道连接")
    print("   - 尝试不同的网络环境")

def main():
    """主函数"""
    print("🔍 MySQL连接问题诊断工具")
    print("=" * 60)
    print()
    
    # 基本连通性测试
    test_basic_connectivity()
    
    # Telnet测试
    test_telnet_connection()
    
    # PyMySQL连接测试
    test_pymysql_connection()
    
    # 网络路由测试
    test_network_routes()
    
    # DNS解析测试
    test_dns_resolution()
    
    # 本地网络检查
    check_local_network()
    
    # 提供解决方案
    provide_solutions()
    
    print("=" * 60)
    print("🎯 诊断完成")

if __name__ == "__main__":
    main()
