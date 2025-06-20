#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置管理
"""

import os
from datetime import timedelta


class Config:
    """基础配置类"""
    
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SERVICE_NAME = os.environ.get('SERVICE_NAME') or 'unified-flask-service'
    VERSION = os.environ.get('VERSION') or '1.0.0'
    ENVIRONMENT = os.environ.get('ENVIRONMENT') or 'development'
    
    # 服务器配置
    HOST = os.environ.get('FLASK_HOST') or '0.0.0.0'
    PORT = int(os.environ.get('FLASK_PORT') or 5000)
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 功能特性
    FEATURES = ['image-generation', 'mysql-execution']
    
    # 千帆API配置
    QIANFAN_API_KEY = os.environ.get('QIANFAN_API_KEY') or 'bce-v3/ALTAK-7oUi1siGoK7hNjrn1VAiu/0104429890324ef528e32261e0fdd8b934c39fdc'
    QIANFAN_BASE_URL = os.environ.get('QIANFAN_BASE_URL') or 'https://qianfan.baidubce.com/v2'
    QIANFAN_MODEL = os.environ.get('QIANFAN_MODEL') or 'irag-1.0'
    QIANFAN_TIMEOUT = int(os.environ.get('QIANFAN_TIMEOUT') or 60)
    QIANFAN_MAX_RETRIES = int(os.environ.get('QIANFAN_MAX_RETRIES') or 3)
    
    # 数据库配置
    MYSQL_DEFAULT_CHARSET = os.environ.get('MYSQL_DEFAULT_CHARSET') or 'utf8mb4'
    MYSQL_DEFAULT_PORT = int(os.environ.get('MYSQL_DEFAULT_PORT') or 3306)
    MYSQL_CONNECTION_TIMEOUT = int(os.environ.get('MYSQL_CONNECTION_TIMEOUT') or 30)
    
    # 日志配置
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FORMAT = os.environ.get('LOG_FORMAT') or '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = os.environ.get('LOG_FILE')  # 如果设置则输出到文件
    
    # 安全配置
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT') or '100/hour'
    
    # 请求配置
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH') or 16 * 1024 * 1024)  # 16MB
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        pass


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    ENVIRONMENT = 'development'
    LOG_LEVEL = 'DEBUG'


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    ENVIRONMENT = 'testing'
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    ENVIRONMENT = 'production'
    LOG_LEVEL = 'ERROR'
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # 生产环境特殊配置
        import logging
        from logging.handlers import RotatingFileHandler
        
        if not app.debug and not app.testing:
            # 文件日志
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler(
                'logs/app.log', 
                maxBytes=10240000, 
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
            ))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('应用启动')


# 配置映射
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
