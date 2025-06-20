#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用工厂模式
"""

import os
import logging
from flask import Flask
from flask_cors import CORS

from app.config import Config
from app.utils.logger import setup_logger
from app.api import register_blueprints


def create_app(config_class=Config):
    """
    应用工厂函数
    
    Args:
        config_class: 配置类
        
    Returns:
        Flask应用实例
    """
    # 创建Flask应用
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(config_class)
    
    # 设置日志
    setup_logger(app)
    
    # 启用CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图
    register_blueprints(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 健康检查
    @app.route('/health')
    def health_check():
        """健康检查接口"""
        return {
            "status": "healthy",
            "service": app.config.get('SERVICE_NAME', 'flask-service'),
            "version": app.config.get('VERSION', '1.0.0'),
            "environment": app.config.get('ENVIRONMENT', 'development'),
            "features": app.config.get('FEATURES', [])
        }
    
    app.logger.info(f"Flask应用创建成功 - 环境: {app.config.get('ENVIRONMENT')}")
    
    return app


def register_error_handlers(app):
    """注册全局错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {
            "success": False,
            "error": "Bad Request",
            "message": "请求参数错误",
            "code": 400
        }, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {
            "success": False,
            "error": "Unauthorized",
            "message": "未授权访问",
            "code": 401
        }, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {
            "success": False,
            "error": "Forbidden",
            "message": "禁止访问",
            "code": 403
        }, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            "success": False,
            "error": "Not Found",
            "message": "接口不存在",
            "code": 404
        }, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {
            "success": False,
            "error": "Method Not Allowed",
            "message": "请求方法不允许",
            "code": 405
        }, 405
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return {
            "success": False,
            "error": "Rate Limit Exceeded",
            "message": "请求频率超限",
            "code": 429
        }, 429
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f"服务器内部错误: {str(error)}")
        return {
            "success": False,
            "error": "Internal Server Error",
            "message": "服务器内部错误",
            "code": 500
        }, 500
