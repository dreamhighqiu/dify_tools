#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图生图Flask服务
提供基于千帆API的图像生成接口
"""

import os
import time
import logging
from flask import Flask, request, jsonify
import httpx
from openai import OpenAI

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)

# 配置
API_KEY = os.getenv('QIANFAN_API_KEY', 'bce-v3/ALTAK-7oUi1siGoK7hNjrn1VAiu/0104429890324ef528e32261e0fdd8b934c39fdc')
BASE_URL = os.getenv('QIANFAN_BASE_URL', 'https://qianfan.baidubce.com/v2')
MODEL_NAME = os.getenv('QIANFAN_MODEL', 'irag-1.0')

def generate_image(reference_url: str, prompt: str) -> str:
    """
    生成图像
    
    Args:
        reference_url: 参考图像URL
        prompt: 生成提示词
        
    Returns:
        生成的图像URL，失败时返回None
    """
    # 创建HTTP客户端
    http_client = httpx.Client(
        timeout=60.0,
        trust_env=False  # 禁用环境代理检测
    )

    # 创建OpenAI客户端
    client = OpenAI(
        api_key=API_KEY,
        base_url=BASE_URL,
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
            logger.info(f"调用千帆API (尝试 {attempt + 1}/{max_retries}) - 模型: {MODEL_NAME}")
            logger.info(f"参考图像: {reference_url}")
            logger.info(f"提示词: {prompt}")

            response = client.images.generate(
                model=MODEL_NAME,
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
        finally:
            # 确保HTTP客户端被正确关闭
            http_client.close()
    
    return None

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "image-generation-service",
        "version": "1.0.0",
        "model": MODEL_NAME
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
        "result": "生成图像URL或错误信息",
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
        logger.error(f"接口调用异常: {str(e)}")
        return jsonify({
            "success": False,
            "result": None,
            "message": "服务器内部错误"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "success": False,
        "result": None,
        "message": "接口不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        "success": False,
        "result": None,
        "message": "服务器内部错误"
    }), 500

if __name__ == '__main__':
    # 服务配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    logger.info(f"启动图生图服务 - Host: {host}, Port: {port}, Debug: {debug}")
    logger.info(f"使用模型: {MODEL_NAME}")
    logger.info(f"API端点: {BASE_URL}")
    
    # 启动Flask服务
    app.run(
        host=host,
        port=port,
        debug=debug,
        threaded=True  # 支持多线程
    )
