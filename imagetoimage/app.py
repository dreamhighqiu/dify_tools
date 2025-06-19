#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像生成Flask服务主入口文件
"""

import os
import logging
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__)
    
    # 配置
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['QIANFAN_API_KEY'] = os.getenv('QIANFAN_API_KEY', 'bce-v3/ALTAK-B39KBUm1GxWtwjcNWxxxxxxxx3490d01a03335')
    app.config['QIANFAN_BASE_URL'] = os.getenv('QIANFAN_BASE_URL', 'https://qianfan.baidubce.com/v2')
    
    return app

app = create_app()

def get_img_info(url, prompt):
    """
    调用千帆API生成图像
    
    Args:
        url (str): 参考图像URL
        prompt (str): 图像生成提示词
    
    Returns:
        str: 生成图像的URL，失败时返回None
    """
    try:
        client = OpenAI(
            api_key=app.config['QIANFAN_API_KEY'],
            base_url=app.config['QIANFAN_BASE_URL'],
        )

        # 合并参考图参数到请求
        extra_data = {
            "refer_image": url,
        }
        
        logger.info(f"开始生成图像，参考图: {url}, 提示词: {prompt}")
        
        response = client.images.generate(
            model="irag-1.0",
            prompt=prompt,
            extra_body=extra_data
        )
        
        result_url = response.data[0].url
        logger.info(f"图像生成成功: {result_url}")
        return result_url
        
    except Exception as e:
        logger.error(f"图像生成失败: {str(e)}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "service": "image-generation-service",
        "version": "1.0.0"
    })

@app.route('/get_img_info', methods=['POST'])
def images_info():
    """
    图像生成API接口
    
    请求体:
    {
        "url": "参考图像URL",
        "prompt": "图像生成提示词"
    }
    
    响应:
    {
        "success": true/false,
        "result": "生成图像URL或错误信息"
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "result": "无效的请求数据"
            }), 400

        url = data.get("url")
        prompt = data.get("prompt")

        # 参数验证
        if not url:
            return jsonify({
                "success": False,
                "result": "需要输入图片链接"
            }), 400
            
        if not prompt:
            return jsonify({
                "success": False,
                "result": "需要输入提示词"
            }), 400

        # 调用图像生成服务
        result = get_img_info(url, prompt)
        
        if result:
            return jsonify({
                "success": True,
                "result": result
            })
        else:
            return jsonify({
                "success": False,
                "result": "图像生成失败，请检查参数或稍后重试"
            }), 500
            
    except Exception as e:
        logger.error(f"API调用异常: {str(e)}")
        return jsonify({
            "success": False,
            "result": "服务器内部错误"
        }), 500

@app.errorhandler(404)
def not_found(error):
    """404错误处理"""
    return jsonify({
        "success": False,
        "result": "接口不存在"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """500错误处理"""
    return jsonify({
        "success": False,
        "result": "服务器内部错误"
    }), 500

if __name__ == '__main__':
    # 获取配置
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    logger.info(f"启动Flask服务 - Host: {host}, Port: {port}, Debug: {debug}")
    
    # 启动服务
    app.run(
        host=host,
        port=port,
        debug=debug
    ) 