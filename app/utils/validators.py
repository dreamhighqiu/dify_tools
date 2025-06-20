#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数验证工具
"""

import re
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse


class ValidationError(Exception):
    """验证错误异常"""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)


class Validator:
    """参数验证器"""
    
    @staticmethod
    def validate_required(value: Any, field_name: str) -> Any:
        """
        验证必填字段
        
        Args:
            value: 字段值
            field_name: 字段名称
            
        Returns:
            验证后的值
            
        Raises:
            ValidationError: 验证失败
        """
        if value is None or (isinstance(value, str) and not value.strip()):
            raise ValidationError(f"{field_name}不能为空", field_name)
        return value
    
    @staticmethod
    def validate_string(value: Any, field_name: str, min_length: int = 0, 
                       max_length: int = None, pattern: str = None) -> str:
        """
        验证字符串
        
        Args:
            value: 字段值
            field_name: 字段名称
            min_length: 最小长度
            max_length: 最大长度
            pattern: 正则表达式模式
            
        Returns:
            验证后的字符串
            
        Raises:
            ValidationError: 验证失败
        """
        if not isinstance(value, str):
            raise ValidationError(f"{field_name}必须是字符串类型", field_name)
        
        value = value.strip()
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name}长度不能少于{min_length}个字符", field_name)
        
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name}长度不能超过{max_length}个字符", field_name)
        
        if pattern and not re.match(pattern, value):
            raise ValidationError(f"{field_name}格式不正确", field_name)
        
        return value
    
    @staticmethod
    def validate_url(value: Any, field_name: str) -> str:
        """
        验证URL
        
        Args:
            value: 字段值
            field_name: 字段名称
            
        Returns:
            验证后的URL
            
        Raises:
            ValidationError: 验证失败
        """
        if not isinstance(value, str):
            raise ValidationError(f"{field_name}必须是字符串类型", field_name)
        
        value = value.strip()
        
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                raise ValidationError(f"{field_name}不是有效的URL", field_name)
        except Exception:
            raise ValidationError(f"{field_name}不是有效的URL", field_name)
        
        return value
    
    @staticmethod
    def validate_integer(value: Any, field_name: str, min_value: int = None, 
                        max_value: int = None) -> int:
        """
        验证整数
        
        Args:
            value: 字段值
            field_name: 字段名称
            min_value: 最小值
            max_value: 最大值
            
        Returns:
            验证后的整数
            
        Raises:
            ValidationError: 验证失败
        """
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name}必须是整数", field_name)
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name}不能小于{min_value}", field_name)
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name}不能大于{max_value}", field_name)
        
        return value
    
    @staticmethod
    def validate_dict(value: Any, field_name: str, required_keys: List[str] = None) -> Dict:
        """
        验证字典
        
        Args:
            value: 字段值
            field_name: 字段名称
            required_keys: 必需的键列表
            
        Returns:
            验证后的字典
            
        Raises:
            ValidationError: 验证失败
        """
        if not isinstance(value, dict):
            raise ValidationError(f"{field_name}必须是字典类型", field_name)
        
        if required_keys:
            missing_keys = [key for key in required_keys if key not in value]
            if missing_keys:
                raise ValidationError(
                    f"{field_name}缺少必需的键: {', '.join(missing_keys)}", 
                    field_name
                )
        
        return value


class RequestValidator:
    """请求验证器"""
    
    def __init__(self, data: Dict[str, Any]):
        """
        初始化验证器
        
        Args:
            data: 请求数据
        """
        self.data = data or {}
        self.errors = {}
        self.validated_data = {}
    
    def validate_field(self, field_name: str, validator_func, *args, **kwargs):
        """
        验证单个字段
        
        Args:
            field_name: 字段名称
            validator_func: 验证函数
            *args: 验证函数参数
            **kwargs: 验证函数关键字参数
        """
        try:
            value = self.data.get(field_name)
            validated_value = validator_func(value, field_name, *args, **kwargs)
            self.validated_data[field_name] = validated_value
        except ValidationError as e:
            self.errors[field_name] = e.message
    
    def is_valid(self) -> bool:
        """
        检查验证是否通过
        
        Returns:
            bool: 验证是否通过
        """
        return len(self.errors) == 0
    
    def get_errors(self) -> Dict[str, str]:
        """
        获取验证错误
        
        Returns:
            Dict[str, str]: 错误字典
        """
        return self.errors
    
    def get_validated_data(self) -> Dict[str, Any]:
        """
        获取验证后的数据
        
        Returns:
            Dict[str, Any]: 验证后的数据
        """
        return self.validated_data
