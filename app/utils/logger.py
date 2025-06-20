#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志配置工具
"""

import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logger(app):
    """
    设置应用日志
    
    Args:
        app: Flask应用实例
    """
    # 设置日志级别
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO').upper())
    app.logger.setLevel(log_level)
    
    # 清除默认处理器
    app.logger.handlers.clear()
    
    # 创建格式化器
    formatter = logging.Formatter(app.config.get('LOG_FORMAT'))
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    app.logger.addHandler(console_handler)
    
    # 文件处理器（如果配置了日志文件）
    log_file = app.config.get('LOG_FILE')
    if log_file:
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        app.logger.addHandler(file_handler)
    
    # 设置第三方库日志级别
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    app.logger.info(f"日志系统初始化完成 - 级别: {app.config.get('LOG_LEVEL')}")


def get_logger(name):
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        logging.Logger: 日志器实例
    """
    return logging.getLogger(name)
