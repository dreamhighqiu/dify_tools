#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一响应格式工具
"""

from flask import jsonify
from typing import Any, Optional, Dict


class ResponseCode:
    """响应状态码常量"""
    SUCCESS = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    RATE_LIMIT = 429
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503


class ApiResponse:
    """API响应工具类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功", code: int = ResponseCode.SUCCESS):
        """
        成功响应

        Args:
            data: 响应数据
            message: 响应消息
            code: HTTP状态码

        Returns:
            Flask响应对象
        """
        response_data = {
            "success": True,
            "message": message,
            "result": data
        }
        return jsonify(response_data), code
    
    @staticmethod
    def error(message: str = "操作失败", code: int = ResponseCode.BAD_REQUEST,
              error_type: str = None, details: Dict = None):
        """
        错误响应

        Args:
            message: 错误消息
            code: HTTP状态码
            error_type: 错误类型
            details: 错误详情

        Returns:
            Flask响应对象
        """
        response_data = {
            "success": False,
            "message": message,
            "result": None,
            "error_type": error_type,
            "details": details
        }
        return jsonify(response_data), code
    
    @staticmethod
    def validation_error(errors: Dict, message: str = "参数验证失败"):
        """
        参数验证错误响应
        
        Args:
            errors: 验证错误详情
            message: 错误消息
            
        Returns:
            Flask响应对象
        """
        return ApiResponse.error(
            message=message,
            code=ResponseCode.BAD_REQUEST,
            error_type="validation_error",
            details=errors
        )
    
    @staticmethod
    def not_found(message: str = "资源不存在"):
        """
        资源不存在响应
        
        Args:
            message: 错误消息
            
        Returns:
            Flask响应对象
        """
        return ApiResponse.error(
            message=message,
            code=ResponseCode.NOT_FOUND,
            error_type="not_found"
        )
    
    @staticmethod
    def unauthorized(message: str = "未授权访问"):
        """
        未授权响应
        
        Args:
            message: 错误消息
            
        Returns:
            Flask响应对象
        """
        return ApiResponse.error(
            message=message,
            code=ResponseCode.UNAUTHORIZED,
            error_type="unauthorized"
        )
    
    @staticmethod
    def rate_limit(message: str = "请求频率超限"):
        """
        频率限制响应
        
        Args:
            message: 错误消息
            
        Returns:
            Flask响应对象
        """
        return ApiResponse.error(
            message=message,
            code=ResponseCode.RATE_LIMIT,
            error_type="rate_limit"
        )
    
    @staticmethod
    def internal_error(message: str = "服务器内部错误"):
        """
        服务器内部错误响应
        
        Args:
            message: 错误消息
            
        Returns:
            Flask响应对象
        """
        return ApiResponse.error(
            message=message,
            code=ResponseCode.INTERNAL_ERROR,
            error_type="internal_error"
        )
