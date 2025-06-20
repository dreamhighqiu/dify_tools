#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask应用启动入口
"""

import os
from app import create_app
from app.config import config

# 获取环境配置
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config[config_name])

if __name__ == '__main__':
    # 从配置中获取启动参数
    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)
    debug = app.config.get('DEBUG', True)
    
    app.logger.info("=" * 60)
    app.logger.info("🚀 启动Flask应用")
    app.logger.info("=" * 60)
    app.logger.info(f"📡 服务地址: {host}:{port}")
    app.logger.info(f"🔧 调试模式: {debug}")
    app.logger.info(f"🌍 运行环境: {config_name}")
    app.logger.info(f"🎨 千帆模型: {app.config.get('QIANFAN_MODEL')}")
    app.logger.info(f"🌐 千帆端点: {app.config.get('QIANFAN_BASE_URL')}")
    app.logger.info("📋 可用接口:")
    app.logger.info("   - GET  /health                         - 健康检查")
    app.logger.info("   - POST /api/v1/image/generate          - 图像生成")
    app.logger.info("   - GET  /api/v1/image/models            - 获取模型列表")
    app.logger.info("   - POST /api/v1/database/execute        - SQL执行")
    app.logger.info("   - POST /api/v1/database/test-connection - 连接测试")
    app.logger.info("   - POST /api/v1/database/network-test   - 网络测试")
    app.logger.info("=" * 60)
    
    # 启动应用
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True
    )
