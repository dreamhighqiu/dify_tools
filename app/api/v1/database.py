#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库操作API
"""

from flask import Blueprint, request, current_app
from app.utils.response import ApiResponse
from app.utils.validators import RequestValidator, Validator
from app.services.database_service import DatabaseService
import socket
import time

# 创建蓝图
database_bp = Blueprint('database', __name__)


@database_bp.route('/execute', methods=['POST'])
def execute_sql():
    """
    SQL执行接口

    请求体格式1（推荐 - 嵌套格式）:
    {
        "sql": "SQL语句",
        "connection": {
            "host": "数据库地址",
            "port": 3306,
            "user": "用户名",
            "password": "密码",
            "database": "数据库名",
            "charset": "utf8mb4"
        },
        "timeout": 30
    }

    请求体格式2（扁平化格式）:
    {
        "sql": "SQL语句",
        "host": "数据库地址",
        "port": 3306,
        "user": "用户名",
        "password": "密码",
        "database": "数据库名",
        "charset": "utf8mb4",
        "timeout": 30
    }

    响应:
    {
        "success": true,
        "message": "SQL执行成功",
        "result": {
            "data": "查询结果或受影响行数",
            "execution_time": 0.123,
            "row_count": 10,
            "sql": "执行的SQL语句"
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return ApiResponse.validation_error(
                {"request": "请求体不能为空"}
            )
        
        # 参数验证 - 支持两种格式
        validator = RequestValidator(data)
        validator.validate_field('sql', Validator.validate_required)
        validator.validate_field('sql', Validator.validate_string, min_length=1, max_length=10000)

        # 检查是否使用嵌套格式（推荐）或扁平化格式
        if 'connection' in data:
            # 嵌套格式：{"sql": "...", "connection": {"host": "...", ...}}
            validator.validate_field('connection', Validator.validate_required)
            validator.validate_field('connection', Validator.validate_dict,
                                   required_keys=['host', 'user', 'password', 'database'])

            if not validator.is_valid():
                return ApiResponse.validation_error(validator.get_errors())

            validated_data = validator.get_validated_data()
            connection_data = validated_data['connection']
        else:
            # 扁平化格式：{"sql": "...", "host": "...", "user": "...", ...}
            validator.validate_field('host', Validator.validate_required)
            validator.validate_field('user', Validator.validate_required)
            validator.validate_field('password', Validator.validate_required)
            validator.validate_field('database', Validator.validate_required)

            if not validator.is_valid():
                return ApiResponse.validation_error(validator.get_errors())

            validated_data = validator.get_validated_data()
            # 构建连接信息
            connection_data = {
                'host': validated_data['host'],
                'user': validated_data['user'],
                'password': validated_data['password'],
                'database': validated_data['database']
            }
            # 可选字段
            if 'port' in validated_data:
                connection_data['port'] = validated_data['port']
            if 'charset' in validated_data:
                connection_data['charset'] = validated_data['charset']

        # 验证连接信息的具体字段
        connection_validator = RequestValidator(connection_data)
        connection_validator.validate_field('host', Validator.validate_string, min_length=1)
        connection_validator.validate_field('user', Validator.validate_string, min_length=1)
        connection_validator.validate_field('password', Validator.validate_string)
        connection_validator.validate_field('database', Validator.validate_string, min_length=1)

        # 可选字段
        if 'port' in connection_data:
            connection_validator.validate_field('port', Validator.validate_integer,
                                              min_value=1, max_value=65535)

        if not connection_validator.is_valid():
            return ApiResponse.validation_error(
                {f"connection.{k}": v for k, v in connection_validator.get_errors().items()}
            )
        
        # 获取超时设置
        timeout = data.get('timeout', current_app.config.get('MYSQL_CONNECTION_TIMEOUT', 30))
        
        # 记录请求（不记录敏感信息）
        safe_connection = {k: v for k, v in connection_data.items() if k != 'password'}
        current_app.logger.info(
            f"收到SQL执行请求 - SQL: {validated_data['sql'][:100]}..., "
            f"连接: {safe_connection}"
        )
        
        # 调用服务
        db_service = DatabaseService()
        result = db_service.execute_sql(
            sql=validated_data['sql'],
            connection_info=connection_data,
            timeout=timeout
        )
        
        if result['success']:
            return ApiResponse.success(
                data={
                    "data": result['result'],
                    "execution_time": result.get('execution_time'),
                    "row_count": result.get('row_count'),
                    "sql": validated_data['sql']
                },
                message="SQL执行成功"
            )
        else:
            return ApiResponse.error(
                message=result['message'],
                error_type="execution_failed",
                details=result.get('details')
            )
    
    except Exception as e:
        current_app.logger.error(f"SQL执行接口异常: {str(e)}")
        return ApiResponse.internal_error("数据库服务异常")


@database_bp.route('/test-connection', methods=['POST'])
def test_connection():
    """
    测试数据库连接
    
    请求体:
    {
        "connection": {
            "host": "数据库地址",
            "port": 3306,
            "user": "用户名",
            "password": "密码",
            "database": "数据库名",
            "charset": "utf8mb4"
        }
    }
    
    响应:
    {
        "success": true,
        "message": "连接测试成功",
        "result": {
            "connected": true,
            "server_version": "8.0.25",
            "response_time": 0.123
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return ApiResponse.validation_error(
                {"request": "请求体不能为空"}
            )
        
        # 参数验证
        validator = RequestValidator(data)
        validator.validate_field('connection', Validator.validate_required)
        validator.validate_field('connection', Validator.validate_dict, 
                               required_keys=['host', 'user', 'password', 'database'])
        
        if not validator.is_valid():
            return ApiResponse.validation_error(validator.get_errors())
        
        validated_data = validator.get_validated_data()
        
        # 验证连接信息的具体字段
        connection_validator = RequestValidator(validated_data['connection'])
        connection_validator.validate_field('host', Validator.validate_string, min_length=1)
        connection_validator.validate_field('user', Validator.validate_string, min_length=1)
        connection_validator.validate_field('password', Validator.validate_string)
        connection_validator.validate_field('database', Validator.validate_string, min_length=1)
        
        if not connection_validator.is_valid():
            return ApiResponse.validation_error(
                {f"connection.{k}": v for k, v in connection_validator.get_errors().items()}
            )
        
        # 记录请求（不记录敏感信息）
        safe_connection = {k: v for k, v in validated_data['connection'].items() if k != 'password'}
        current_app.logger.info(f"收到连接测试请求 - 连接: {safe_connection}")
        
        # 调用服务
        db_service = DatabaseService()
        result = db_service.test_connection(validated_data['connection'])
        
        if result['success']:
            return ApiResponse.success(
                data={
                    "connected": True,
                    "server_version": result.get('server_version'),
                    "response_time": result.get('response_time')
                },
                message="连接测试成功"
            )
        else:
            return ApiResponse.error(
                message=result['message'],
                error_type="connection_failed",
                details=result.get('details')
            )
    
    except Exception as e:
        current_app.logger.error(f"连接测试接口异常: {str(e)}")
        return ApiResponse.internal_error("连接测试服务异常")


@database_bp.route('/network-test', methods=['POST'])
def network_test():
    """
    网络连接测试

    请求体:
    {
        "host": "数据库地址",
        "port": 3306
    }

    响应:
    {
        "success": true,
        "message": "网络测试成功",
        "result": {
            "tcp_connected": true,
            "response_time": 0.123,
            "host": "3.96.167.248",
            "port": 3306
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return ApiResponse.validation_error(
                {"request": "请求体不能为空"}
            )

        # 参数验证
        validator = RequestValidator(data)
        validator.validate_field('host', Validator.validate_required)
        validator.validate_field('host', Validator.validate_string, min_length=1)

        # 端口可选，默认3306
        port = data.get('port', 3306)
        if 'port' in data:
            validator.validate_field('port', Validator.validate_integer,
                                   min_value=1, max_value=65535)

        if not validator.is_valid():
            return ApiResponse.validation_error(validator.get_errors())

        validated_data = validator.get_validated_data()
        host = validated_data['host']

        current_app.logger.info(f"网络连接测试: {host}:{port}")

        # TCP连接测试
        start_time = time.time()
        tcp_connected = False
        error_message = None

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)  # 30秒超时
            result = sock.connect_ex((host, port))
            sock.close()

            response_time = time.time() - start_time
            tcp_connected = (result == 0)

            if not tcp_connected:
                error_message = f"TCP连接失败，错误码: {result}"

        except Exception as e:
            response_time = time.time() - start_time
            error_message = f"网络连接异常: {str(e)}"

        # 返回结果
        if tcp_connected:
            return ApiResponse.success(
                data={
                    "tcp_connected": True,
                    "response_time": response_time,
                    "host": host,
                    "port": port
                },
                message="网络连接测试成功"
            )
        else:
            return ApiResponse.error(
                message=f"网络连接测试失败: {error_message}",
                error_type="network_error",
                details={
                    "tcp_connected": False,
                    "response_time": response_time,
                    "host": host,
                    "port": port,
                    "error": error_message
                }
            )

    except Exception as e:
        current_app.logger.error(f"网络测试接口异常: {str(e)}")
        return ApiResponse.internal_error("网络测试服务异常")
