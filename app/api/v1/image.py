#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像生成API
"""

from flask import Blueprint, request, current_app
from app.utils.response import ApiResponse
from app.utils.validators import RequestValidator, Validator
from app.services.image_service import ImageService

# 创建蓝图
image_bp = Blueprint('image', __name__)


@image_bp.route('/generate', methods=['POST'])
def generate_image():
    """
    图像生成接口
    
    请求体:
    {
        "reference_url": "参考图像URL",
        "prompt": "生成提示词",
        "model": "模型名称(可选)"
    }
    
    响应:
    {
        "success": true,
        "message": "图像生成成功",
        "result": {
            "image_url": "生成的图像URL",
            "model": "使用的模型",
            "prompt": "使用的提示词",
            "reference_url": "参考图像URL"
        }
    }
    """
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return ApiResponse.validation_error(
                {"request": "请求体不能为空"}
            )
        
        # 参数验证
        validator = RequestValidator(data)
        validator.validate_field('reference_url', Validator.validate_required)
        validator.validate_field('reference_url', Validator.validate_url)
        validator.validate_field('prompt', Validator.validate_required)
        validator.validate_field('prompt', Validator.validate_string, min_length=1, max_length=1000)
        
        # 可选参数
        model = data.get('model', current_app.config.get('QIANFAN_MODEL'))
        
        if not validator.is_valid():
            return ApiResponse.validation_error(validator.get_errors())
        
        validated_data = validator.get_validated_data()
        
        # 记录请求
        current_app.logger.info(
            f"收到图像生成请求 - URL: {validated_data['reference_url']}, "
            f"提示词: {validated_data['prompt']}, 模型: {model}"
        )
        
        # 调用服务
        image_service = ImageService()
        result = image_service.generate_image(
            reference_url=validated_data['reference_url'],
            prompt=validated_data['prompt'],
            model=model
        )
        
        if result['success']:
            return ApiResponse.success(
                data={
                    "image_url": result['image_url'],
                    "model": model,
                    "prompt": validated_data['prompt'],
                    "reference_url": validated_data['reference_url']
                },
                message="图像生成成功"
            )
        else:
            return ApiResponse.error(
                message=result['message'],
                error_type="generation_failed",
                details=result.get('details')
            )
    
    except Exception as e:
        current_app.logger.error(f"图像生成接口异常: {str(e)}")
        return ApiResponse.internal_error("图像生成服务异常")


@image_bp.route('/models', methods=['GET'])
def get_available_models():
    """
    获取可用的图像生成模型列表
    
    响应:
    {
        "success": true,
        "message": "获取成功",
        "result": {
            "models": [
                {
                    "name": "irag-1.0",
                    "description": "千帆图像生成模型",
                    "is_default": true
                }
            ],
            "default_model": "irag-1.0"
        }
    }
    """
    try:
        models = [
            {
                "name": current_app.config.get('QIANFAN_MODEL', 'irag-1.0'),
                "description": "千帆图像生成模型",
                "is_default": True
            }
        ]
        
        return ApiResponse.success(
            data={
                "models": models,
                "default_model": current_app.config.get('QIANFAN_MODEL', 'irag-1.0')
            },
            message="获取模型列表成功"
        )
    
    except Exception as e:
        current_app.logger.error(f"获取模型列表异常: {str(e)}")
        return ApiResponse.internal_error("获取模型列表失败")
