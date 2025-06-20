#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像生成服务
"""

import time
import httpx
from openai import OpenAI
from flask import current_app
from typing import Dict, Any


class ImageService:
    """图像生成服务类"""
    
    def __init__(self):
        """初始化服务"""
        self.api_key = current_app.config.get('QIANFAN_API_KEY')
        self.base_url = current_app.config.get('QIANFAN_BASE_URL')
        self.timeout = current_app.config.get('QIANFAN_TIMEOUT', 60)
        self.max_retries = current_app.config.get('QIANFAN_MAX_RETRIES', 3)
    
    def generate_image(self, reference_url: str, prompt: str, model: str = None) -> Dict[str, Any]:
        """
        生成图像
        
        Args:
            reference_url: 参考图像URL
            prompt: 生成提示词
            model: 模型名称
            
        Returns:
            Dict[str, Any]: 生成结果
        """
        if not model:
            model = current_app.config.get('QIANFAN_MODEL', 'irag-1.0')
        
        http_client = None
        start_time = time.time()
        
        try:
            # 创建HTTP客户端
            http_client = httpx.Client(
                timeout=self.timeout,
                trust_env=False  # 禁用环境代理检测
            )
            
            # 创建OpenAI客户端
            client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                http_client=http_client
            )
            
            # 请求参数
            extra_data = {
                "refer_image": reference_url,
            }
            
            # 重试机制
            base_delay = 2
            last_error = None
            
            for attempt in range(self.max_retries):
                try:
                    current_app.logger.info(
                        f"调用千帆API (尝试 {attempt + 1}/{self.max_retries}) - "
                        f"模型: {model}, 提示词: {prompt}"
                    )
                    
                    response = client.images.generate(
                        model=model,
                        prompt=prompt,
                        extra_body=extra_data
                    )
                    
                    result_url = response.data[0].url
                    execution_time = time.time() - start_time
                    
                    current_app.logger.info(
                        f"图像生成成功 - URL: {result_url}, 耗时: {execution_time:.2f}秒"
                    )
                    
                    return {
                        "success": True,
                        "image_url": result_url,
                        "execution_time": execution_time,
                        "model": model,
                        "attempts": attempt + 1
                    }
                
                except Exception as e:
                    last_error = e
                    error_type = type(e).__name__
                    current_app.logger.warning(
                        f"图像生成失败 (尝试 {attempt + 1}/{self.max_retries}): {str(e)}"
                    )
                    
                    # 处理速率限制错误
                    if "RateLimitError" in error_type or "429" in str(e):
                        if attempt < self.max_retries - 1:
                            delay = base_delay * (2 ** attempt)  # 指数退避
                            current_app.logger.info(f"遇到速率限制，等待 {delay} 秒后重试...")
                            time.sleep(delay)
                            continue
                        else:
                            return {
                                "success": False,
                                "message": "API调用频率超限，请稍后重试",
                                "error_type": "rate_limit_exceeded",
                                "details": {
                                    "attempts": self.max_retries,
                                    "last_error": str(last_error)
                                }
                            }
                    else:
                        # 非速率限制错误，直接返回
                        break
            
            # 所有重试都失败
            execution_time = time.time() - start_time
            return {
                "success": False,
                "message": "图像生成失败",
                "error_type": "generation_failed",
                "details": {
                    "attempts": self.max_retries,
                    "execution_time": execution_time,
                    "last_error": str(last_error)
                }
            }
        
        except Exception as e:
            execution_time = time.time() - start_time
            current_app.logger.error(f"图像生成服务异常: {str(e)}")
            return {
                "success": False,
                "message": "图像生成服务异常",
                "error_type": "service_error",
                "details": {
                    "execution_time": execution_time,
                    "error": str(e)
                }
            }
        
        finally:
            # 确保HTTP客户端被正确关闭
            if http_client:
                http_client.close()
    
    def get_available_models(self) -> Dict[str, Any]:
        """
        获取可用的模型列表
        
        Returns:
            Dict[str, Any]: 模型列表
        """
        try:
            models = [
                {
                    "name": current_app.config.get('QIANFAN_MODEL', 'irag-1.0'),
                    "description": "千帆图像生成模型",
                    "is_default": True,
                    "provider": "Baidu Qianfan"
                }
            ]
            
            return {
                "success": True,
                "models": models,
                "default_model": current_app.config.get('QIANFAN_MODEL', 'irag-1.0')
            }
        
        except Exception as e:
            current_app.logger.error(f"获取模型列表异常: {str(e)}")
            return {
                "success": False,
                "message": "获取模型列表失败",
                "error_type": "service_error",
                "details": {"error": str(e)}
            }
