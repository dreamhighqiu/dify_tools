#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1版本蓝图
"""

from flask import Blueprint
from app.api.v1.image import image_bp
from app.api.v1.database import database_bp

# 创建v1蓝图
api_v1 = Blueprint('api_v1', __name__)

# 注册子蓝图
api_v1.register_blueprint(image_bp, url_prefix='/image')
api_v1.register_blueprint(database_bp, url_prefix='/database')
