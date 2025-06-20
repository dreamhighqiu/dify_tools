#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API蓝图注册
"""
from flask import Flask
from app.api.v1 import api_v1


def register_blueprints(app: Flask):
    """
    注册所有蓝图
    
    Args:
        app: Flask应用实例
    """
    # 注册API v1蓝图
    app.register_blueprint(api_v1, url_prefix='/api/v1')
    
    app.logger.info("API蓝图注册完成")
