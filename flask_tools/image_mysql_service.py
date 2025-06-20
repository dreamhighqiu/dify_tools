#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一Flask服务
集成图生图和MySQL执行功能
"""

import os
import time
import logging
from flask import Flask, request, jsonify
import httpx
from openai import OpenAI
import pymysql

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 图生图配置
QIANFAN_API_KEY = os.getenv('QIANFAN_API_KEY', 'bce-v3/ALTAK-7oUi1siGoK7hNjrn1VAiu/0104429890324ef528e32261e0fdd8b934c39fdc')
QIANFAN_BASE_URL = os.getenv('QIANFAN_BASE_URL', 'https://qianfan.baidubce.com/v2')
QIANFAN_MODEL = os.getenv('QIANFAN_MODEL', 'irag-1.0')

# ==================== 图生图功能 ====================

def generate_image(reference_url: str, prompt: str) -> str:
    """
    生成图像

    Args:
        reference_url: 参考图像URL
        prompt: 生成提示词

    Returns:
        生成的图像URL，失败时返回None
    """
    http_client = None
    try:
        # 创建HTTP客户端
        http_client = httpx.Client(
            timeout=60.0,
            trust_env=False  # 禁用环境代理检测
        )

        # 创建OpenAI客户端
        client = OpenAI(
            api_key=QIANFAN_API_KEY,
            base_url=QIANFAN_BASE_URL,
            http_client=http_client
        )

        # 请求参数
        extra_data = {
            "refer_image": reference_url,
        }

        # 重试配置
        max_retries = 3
        base_delay = 2

        for attempt in range(max_retries):
            try:
                logger.info(f"调用千帆API (尝试 {attempt + 1}/{max_retries}) - 模型: {QIANFAN_MODEL}")
                logger.info(f"参考图像: {reference_url}")
                logger.info(f"提示词: {prompt}")

                response = client.images.generate(
                    model=QIANFAN_MODEL,
                    prompt=prompt,
                    extra_body=extra_data
                )

                result_url = response.data[0].url
                logger.info(f"图像生成成功: {result_url}")
                return result_url

            except Exception as e:
                error_type = type(e).__name__
                logger.error(f"图像生成失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")

                # 处理速率限制错误
                if "RateLimitError" in error_type or "429" in str(e):
                    if attempt < max_retries - 1:
                        delay = base_delay * (2 ** attempt)  # 指数退避
                        logger.warning(f"遇到速率限制，等待 {delay} 秒后重试...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error("达到最大重试次数，速率限制问题未解决")
                else:
                    # 非速率限制错误，直接返回
                    logger.error(f"API调用错误: {error_type}")
                    break

        return None

    finally:
        # 确保HTTP客户端被正确关闭
        if http_client:
            http_client.close()

# ==================== MySQL执行功能 ====================

def execute_sql(sql: str, connection_info: dict):
    """
    执行传入的 SQL 语句，并返回查询结果

    Args:
        sql: 要执行的 SQL 语句
        connection_info: 数据库连接信息字典
            - host: 数据库地址
            - user: 数据库用户名
            - password: 数据库密码
            - database: 数据库名称
            - port: 数据库端口（可选，默认为 3306）
            - charset: 字符编码（可选，默认为 "utf8mb4"）

    Returns:
        SELECT查询返回结果列表，其他操作返回受影响行数，出错返回None
    """
    connection = None
    try:
        # 从 connection_info 中获取各项参数，设置默认值
        host = connection_info.get("host", "localhost")
        user = connection_info.get("user")
        password = connection_info.get("password")
        database = connection_info.get("database")
        port = connection_info.get("port", 3306)
        charset = connection_info.get("charset", "utf8mb4")

        logger.info(f"连接数据库: {user}@{host}:{port}/{database}")

        # 建立数据库连接
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            charset=charset,
            cursorclass=pymysql.cursors.DictCursor  # 返回字典格式结果
        )

        with connection.cursor() as cursor:
            logger.info(f"执行SQL: {sql}")
            cursor.execute(sql)

            # 判断是否为 SELECT 查询语句
            if sql.strip().lower().startswith("select"):
                result = cursor.fetchall()
                logger.info(f"查询返回 {len(result)} 条记录")
            else:
                connection.commit()  # 非查询语句需要提交事务
                result = cursor.rowcount  # 返回受影响的行数
                logger.info(f"操作影响 {result} 行")

        return result

    except Exception as e:
        logger.error(f"执行 SQL 语句时出错: {str(e)}")
        return None

    finally:
        if connection:
            connection.close()
            logger.info("数据库连接已关闭")

# ==================== Flask路由 ====================

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "unified-service",
        "version": "1.0.0",
        "features": ["image-generation", "mysql-execution"],
        "qianfan_model": QIANFAN_MODEL
    })

@app.route('/get_img_info', methods=['POST'])
def get_img_info():
    """
    图生图接口

    请求体:
    {
        "url": "参考图像URL",
        "prompt": "生成提示词"
    }

    响应:
    {
        "success": true/false,
        "result": "生成图像URL或null",
        "message": "详细信息"
    }
    """
    try:
        # 获取请求数据
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({
                "success": False,
                "result": None,
                "message": "请求体格式错误，请发送有效的JSON数据"
            }), 400

        if not data:
            return jsonify({
                "success": False,
                "result": None,
                "message": "请求体不能为空"
            }), 400

        # 参数验证
        reference_url = data.get("url", "").strip()
        prompt = data.get("prompt", "").strip()

        if not reference_url:
            return jsonify({
                "success": False,
                "result": None,
                "message": "参考图像URL不能为空"
            }), 400

        if not prompt:
            return jsonify({
                "success": False,
                "result": None,
                "message": "生成提示词不能为空"
            }), 400

        # 记录请求信息
        logger.info(f"收到图生图请求 - URL: {reference_url}, 提示词: {prompt}")

        # 调用图像生成
        result_url = generate_image(reference_url, prompt)

        if result_url:
            return jsonify({
                "success": True,
                "result": result_url,
                "message": "图像生成成功"
            })
        else:
            return jsonify({
                "success": False,
                "result": None,
                "message": "图像生成失败，请稍后重试"
            }), 500

    except Exception as e:
        logger.error(f"图生图接口调用异常: {str(e)}")
        return jsonify({
            "success": False,
            "result": None,
            "message": "服务器内部错误"
        }), 500

@app.route('/execute_sql', methods=['POST'])
def execute_sql_api():
    """
    SQL执行接口

    请求体:
    {
        "sql": "SQL语句",
        "connection_info": {
            "host": "数据库地址",
            "user": "用户名",
            "password": "密码",
            "database": "数据库名",
            "port": 3306,
            "charset": "utf8mb4"
        }
    }

    响应:
    {
        "success": true/false,
        "result": "查询结果或受影响行数",
        "message": "详细信息"
    }
    """
    try:
        # 获取请求数据
        try:
            data = request.get_json(force=True)
        except Exception:
            return jsonify({
                "success": False,
                "result": None,
                "message": "请求体格式错误，请发送有效的JSON数据"
            }), 400

        if not data:
            return jsonify({
                "success": False,
                "result": None,
                "message": "请求体不能为空"
            }), 400

        # 参数验证
        sql = data.get("sql", "").strip()
        connection_info = data.get("connection_info")

        if not sql:
            return jsonify({
                "success": False,
                "result": None,
                "message": "SQL语句不能为空"
            }), 400

        if not connection_info or not isinstance(connection_info, dict):
            return jsonify({
                "success": False,
                "result": None,
                "message": "数据库连接信息不能为空且必须是字典格式"
            }), 400

        # 验证必要的连接参数
        required_fields = ["host", "user", "password", "database"]
        for field in required_fields:
            if not connection_info.get(field):
                return jsonify({
                    "success": False,
                    "result": None,
                    "message": f"缺少必要的连接参数: {field}"
                }), 400

        # 记录请求信息
        logger.info(f"收到SQL执行请求 - SQL: {sql[:100]}...")

        # 执行SQL
        result = execute_sql(sql, connection_info)

        if result is not None:
            return jsonify({
                "success": True,
                "result": result,
                "message": "SQL执行成功"
            })
        else:
            return jsonify({
                "success": False,
                "result": None,
                "message": "SQL执行失败，请检查SQL语句和连接信息"
            }), 500

    except Exception as e:
        logger.error(f"SQL执行接口调用异常: {str(e)}")
        return jsonify({
            "success": False,
            "result": None,
            "message": "服务器内部错误"
        }), 500
# ==================== 错误处理 ====================

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "success": False,
        "result": None,
        "message": "接口不存在"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """405错误处理"""
    return jsonify({
        "success": False,
        "result": None,
        "message": "请求方法不允许"
    }), 405

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        "success": False,
        "result": None,
        "message": "服务器内部错误"
    }), 500

# ==================== 服务启动 ====================

if __name__ == '__main__':
    # 服务配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    logger.info("=" * 60)
    logger.info("🚀 启动统一Flask服务")
    logger.info("=" * 60)
    logger.info(f"📡 服务地址: {host}:{port}")
    logger.info(f"🔧 调试模式: {debug}")
    logger.info(f"🎨 图生图模型: {QIANFAN_MODEL}")
    logger.info(f"🌐 千帆API端点: {QIANFAN_BASE_URL}")
    logger.info("📋 可用接口:")
    logger.info("   - GET  /health        - 健康检查")
    logger.info("   - POST /get_img_info  - 图生图")
    logger.info("   - POST /execute_sql   - SQL执行")
    logger.info("=" * 60)

    # 启动Flask服务
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True  # 支持多线程
    )