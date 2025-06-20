#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库服务
"""

import time
import pymysql
from flask import current_app
from typing import Dict, Any


class DatabaseService:
    """数据库服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.default_charset = current_app.config.get('MYSQL_DEFAULT_CHARSET', 'utf8mb4')
        self.default_port = current_app.config.get('MYSQL_DEFAULT_PORT', 3306)
        self.connection_timeout = current_app.config.get('MYSQL_CONNECTION_TIMEOUT', 30)
    
    def execute_sql(self, sql: str, connection_info: Dict[str, Any], timeout: int = None) -> Dict[str, Any]:
        """
        执行SQL语句
        
        Args:
            sql: SQL语句
            connection_info: 数据库连接信息
            timeout: 超时时间
            
        Returns:
            Dict[str, Any]: 执行结果
        """
        if timeout is None:
            timeout = self.connection_timeout
        
        connection = None
        start_time = time.time()
        
        try:
            # 准备连接参数
            conn_params = self._prepare_connection_params(connection_info)
            
            current_app.logger.info(
                f"连接数据库: {conn_params['user']}@{conn_params['host']}:"
                f"{conn_params['port']}/{conn_params['database']}"
            )
            
            # 建立数据库连接
            connection = pymysql.connect(
                **conn_params,
                connect_timeout=max(timeout, 60),  # 最少60秒连接超时
                read_timeout=timeout,
                write_timeout=timeout,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True,  # 自动提交
                ssl_disabled=True  # 禁用SSL以提高连接速度
            )
            
            with connection.cursor() as cursor:
                current_app.logger.info(f"执行SQL: {sql}")
                
                # 执行SQL
                cursor.execute(sql)
                
                # 判断是否为查询语句
                if sql.strip().lower().startswith(('select', 'show', 'describe', 'explain')):
                    result = cursor.fetchall()
                    row_count = len(result)
                    current_app.logger.info(f"查询返回 {row_count} 条记录")
                else:
                    connection.commit()
                    result = cursor.rowcount
                    row_count = result
                    current_app.logger.info(f"操作影响 {result} 行")
                
                execution_time = time.time() - start_time
                
                return {
                    "success": True,
                    "result": result,
                    "row_count": row_count,
                    "execution_time": execution_time,
                    "sql_type": self._get_sql_type(sql)
                }
        
        except pymysql.Error as e:
            execution_time = time.time() - start_time
            error_code = getattr(e, 'args', [None])[0] if hasattr(e, 'args') else None
            error_message = str(e)
            
            current_app.logger.error(f"数据库操作失败: {error_message}")
            
            return {
                "success": False,
                "message": f"数据库操作失败: {error_message}",
                "error_type": "database_error",
                "details": {
                    "error_code": error_code,
                    "execution_time": execution_time,
                    "sql": sql[:100] + "..." if len(sql) > 100 else sql
                }
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            current_app.logger.error(f"SQL执行异常: {str(e)}")
            
            return {
                "success": False,
                "message": f"SQL执行异常: {str(e)}",
                "error_type": "execution_error",
                "details": {
                    "execution_time": execution_time,
                    "error": str(e)
                }
            }
        
        finally:
            if connection:
                connection.close()
                current_app.logger.info("数据库连接已关闭")
    
    def test_connection(self, connection_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试数据库连接
        
        Args:
            connection_info: 数据库连接信息
            
        Returns:
            Dict[str, Any]: 测试结果
        """
        connection = None
        start_time = time.time()
        
        try:
            # 准备连接参数
            conn_params = self._prepare_connection_params(connection_info)
            
            current_app.logger.info(
                f"测试数据库连接: {conn_params['user']}@{conn_params['host']}:"
                f"{conn_params['port']}/{conn_params['database']}"
            )
            
            # 建立数据库连接
            connection = pymysql.connect(
                **conn_params,
                connect_timeout=30,  # 连接测试使用30秒超时
                cursorclass=pymysql.cursors.DictCursor,
                ssl_disabled=True  # 禁用SSL以提高连接速度
            )
            
            # 获取服务器版本
            with connection.cursor() as cursor:
                cursor.execute("SELECT VERSION() as version")
                result = cursor.fetchone()
                server_version = result['version'] if result else "Unknown"
            
            response_time = time.time() - start_time
            
            current_app.logger.info(
                f"数据库连接测试成功 - 版本: {server_version}, 响应时间: {response_time:.3f}秒"
            )
            
            return {
                "success": True,
                "server_version": server_version,
                "response_time": response_time,
                "connection_info": {
                    "host": conn_params['host'],
                    "port": conn_params['port'],
                    "database": conn_params['database'],
                    "charset": conn_params['charset']
                }
            }
        
        except pymysql.Error as e:
            response_time = time.time() - start_time
            error_message = str(e)
            
            current_app.logger.error(f"数据库连接测试失败: {error_message}")
            
            return {
                "success": False,
                "message": f"数据库连接失败: {error_message}",
                "error_type": "connection_error",
                "details": {
                    "response_time": response_time,
                    "error": error_message
                }
            }
        
        except Exception as e:
            response_time = time.time() - start_time
            current_app.logger.error(f"连接测试异常: {str(e)}")
            
            return {
                "success": False,
                "message": f"连接测试异常: {str(e)}",
                "error_type": "test_error",
                "details": {
                    "response_time": response_time,
                    "error": str(e)
                }
            }
        
        finally:
            if connection:
                connection.close()
    
    def _prepare_connection_params(self, connection_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        准备连接参数
        
        Args:
            connection_info: 原始连接信息
            
        Returns:
            Dict[str, Any]: 处理后的连接参数
        """
        return {
            "host": connection_info.get("host", "localhost"),
            "port": connection_info.get("port", self.default_port),
            "user": connection_info.get("user"),
            "password": connection_info.get("password"),
            "database": connection_info.get("database"),
            "charset": connection_info.get("charset", self.default_charset)
        }
    
    def _get_sql_type(self, sql: str) -> str:
        """
        获取SQL语句类型
        
        Args:
            sql: SQL语句
            
        Returns:
            str: SQL类型
        """
        sql_lower = sql.strip().lower()
        
        if sql_lower.startswith('select'):
            return 'SELECT'
        elif sql_lower.startswith('insert'):
            return 'INSERT'
        elif sql_lower.startswith('update'):
            return 'UPDATE'
        elif sql_lower.startswith('delete'):
            return 'DELETE'
        elif sql_lower.startswith('create'):
            return 'CREATE'
        elif sql_lower.startswith('drop'):
            return 'DROP'
        elif sql_lower.startswith('alter'):
            return 'ALTER'
        elif sql_lower.startswith('show'):
            return 'SHOW'
        elif sql_lower.startswith('describe'):
            return 'DESCRIBE'
        elif sql_lower.startswith('explain'):
            return 'EXPLAIN'
        else:
            return 'OTHER'
