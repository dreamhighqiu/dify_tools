#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试MySQL连接
"""

import pymysql
import time
import socket

def test_socket_connection():
    """测试Socket连接"""
    print("🔌 测试Socket连接...")
    
    host = "3.96.167.248"
    port = 3306
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        
        start_time = time.time()
        result = sock.connect_ex((host, port))
        connect_time = time.time() - start_time
        
        sock.close()
        
        if result == 0:
            print(f"✅ Socket连接成功 (耗时: {connect_time:.3f}秒)")
            return True
        else:
            print(f"❌ Socket连接失败 (错误码: {result})")
            return False
            
    except Exception as e:
        print(f"❌ Socket连接异常: {str(e)}")
        return False

def test_mysql_connection_simple():
    """简单MySQL连接测试"""
    print("\n🔗 测试MySQL连接...")
    
    config = {
        "host": "3.96.167.248",
        "port": 3306,
        "user": "ai_mysql",
        "password": "qianwei123",
        "database": "ai_db",
        "connect_timeout": 10
    }
    
    try:
        start_time = time.time()
        connection = pymysql.connect(**config)
        connect_time = time.time() - start_time
        
        print(f"✅ MySQL连接成功 (耗时: {connect_time:.3f}秒)")
        
        # 测试查询
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION() as version")
            result = cursor.fetchone()
            print(f"📊 MySQL版本: {result[0]}")
        
        connection.close()
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL连接失败: {str(e)}")
        print(f"   错误类型: {type(e).__name__}")
        return False
    except Exception as e:
        print(f"❌ 连接异常: {str(e)}")
        return False

def test_mysql_with_different_timeouts():
    """测试不同超时设置"""
    print("\n⏱️ 测试不同超时设置...")
    
    base_config = {
        "host": "3.96.167.248",
        "port": 3306,
        "user": "ai_mysql",
        "password": "qianwei123",
        "database": "ai_db"
    }
    
    timeouts = [5, 10, 30, 60]
    
    for timeout in timeouts:
        print(f"\n测试超时时间: {timeout}秒")
        config = base_config.copy()
        config["connect_timeout"] = timeout
        
        try:
            start_time = time.time()
            connection = pymysql.connect(**config)
            connect_time = time.time() - start_time
            
            connection.close()
            print(f"✅ 连接成功 (耗时: {connect_time:.3f}秒)")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {str(e)}")
    
    return False

def test_mysql_with_ssl_options():
    """测试不同SSL选项"""
    print("\n🔒 测试SSL选项...")
    
    base_config = {
        "host": "3.96.167.248",
        "port": 3306,
        "user": "ai_mysql",
        "password": "qianwei123",
        "database": "ai_db",
        "connect_timeout": 10
    }
    
    ssl_configs = [
        {"name": "默认SSL", "ssl": None},
        {"name": "禁用SSL", "ssl_disabled": True},
        {"name": "要求SSL", "ssl": {"ssl_disabled": False}},
    ]
    
    for ssl_config in ssl_configs:
        print(f"\n测试: {ssl_config['name']}")
        config = base_config.copy()
        
        if "ssl" in ssl_config:
            config["ssl"] = ssl_config["ssl"]
        if "ssl_disabled" in ssl_config:
            config["ssl_disabled"] = ssl_config["ssl_disabled"]
        
        try:
            start_time = time.time()
            connection = pymysql.connect(**config)
            connect_time = time.time() - start_time
            
            connection.close()
            print(f"✅ 连接成功 (耗时: {connect_time:.3f}秒)")
            return True
            
        except Exception as e:
            print(f"❌ 连接失败: {str(e)}")
    
    return False

def test_query_execution():
    """测试查询执行"""
    print("\n📊 测试查询执行...")
    
    config = {
        "host": "3.96.167.248",
        "port": 3306,
        "user": "ai_mysql",
        "password": "qianwei123",
        "database": "ai_db",
        "connect_timeout": 30,
        "read_timeout": 30,
        "write_timeout": 30,
        "charset": "utf8mb4",
        "cursorclass": pymysql.cursors.DictCursor
    }
    
    queries = [
        "SELECT 1 as test",
        "SELECT VERSION() as version",
        "SHOW TABLES",
        "SELECT g.goods_id, g.goods_name, g.price, i.stock_quantity FROM goods g JOIN inventory i ON g.goods_id = i.goods_id LIMIT 5"
    ]
    
    try:
        connection = pymysql.connect(**config)
        print("✅ 数据库连接成功")
        
        for i, query in enumerate(queries, 1):
            print(f"\n{i}. 执行查询: {query}")
            
            try:
                with connection.cursor() as cursor:
                    start_time = time.time()
                    cursor.execute(query)
                    result = cursor.fetchall()
                    execution_time = time.time() - start_time
                    
                    print(f"✅ 查询成功 (耗时: {execution_time:.3f}秒)")
                    print(f"   返回 {len(result)} 条记录")
                    
                    if result and len(result) > 0:
                        print(f"   示例数据: {result[0]}")
                        
            except Exception as e:
                print(f"❌ 查询失败: {str(e)}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

def main():
    """主函数"""
    print("🧪 MySQL连接直接测试")
    print("=" * 50)
    
    # 1. Socket连接测试
    socket_ok = test_socket_connection()
    
    if not socket_ok:
        print("\n❌ Socket连接失败，无法继续测试")
        print("\n💡 建议:")
        print("1. 检查网络连接")
        print("2. 检查防火墙设置")
        print("3. 确认MySQL服务器地址和端口")
        return
    
    # 2. 简单MySQL连接测试
    mysql_ok = test_mysql_connection_simple()
    
    if not mysql_ok:
        print("\n尝试其他连接方式...")
        
        # 3. 不同超时设置测试
        timeout_ok = test_mysql_with_different_timeouts()
        
        if not timeout_ok:
            # 4. SSL选项测试
            ssl_ok = test_mysql_with_ssl_options()
            
            if not ssl_ok:
                print("\n❌ 所有连接方式都失败")
                print("\n💡 建议运行完整诊断:")
                print("python diagnose_mysql_connection.py")
                return
    
    # 5. 查询执行测试
    test_query_execution()
    
    print("\n" + "=" * 50)
    print("🎯 测试完成")

if __name__ == "__main__":
    main()
