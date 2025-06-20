#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API接口测试
"""

import pytest
import json
from app import create_app
from app.config import TestingConfig


@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app(TestingConfig)
    return app


@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()


class TestHealthAPI:
    """健康检查API测试"""
    
    def test_health_check(self, client):
        """测试健康检查接口"""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'service' in data
        assert 'version' in data
        assert 'features' in data


class TestImageAPI:
    """图像生成API测试"""
    
    def test_generate_image_missing_data(self, client):
        """测试缺少请求数据"""
        response = client.post('/api/v1/image/generate')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_generate_image_invalid_data(self, client):
        """测试无效请求数据"""
        response = client.post(
            '/api/v1/image/generate',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_generate_image_missing_fields(self, client):
        """测试缺少必填字段"""
        test_data = {"prompt": "test prompt"}
        response = client.post(
            '/api/v1/image/generate',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'reference_url' in str(data)
    
    def test_generate_image_invalid_url(self, client):
        """测试无效URL"""
        test_data = {
            "reference_url": "invalid-url",
            "prompt": "test prompt"
        }
        response = client.post(
            '/api/v1/image/generate',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_get_models(self, client):
        """测试获取模型列表"""
        response = client.get('/api/v1/image/models')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'data' in data
        assert 'models' in data['data']


class TestDatabaseAPI:
    """数据库API测试"""
    
    def test_execute_sql_missing_data(self, client):
        """测试缺少请求数据"""
        response = client.post('/api/v1/database/execute')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_execute_sql_missing_fields(self, client):
        """测试缺少必填字段"""
        test_data = {"sql": "SELECT 1"}
        response = client.post(
            '/api/v1/database/execute',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'connection' in str(data)
    
    def test_execute_sql_invalid_connection(self, client):
        """测试无效连接信息"""
        test_data = {
            "sql": "SELECT 1",
            "connection": {}
        }
        response = client.post(
            '/api/v1/database/execute',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False
    
    def test_test_connection_missing_data(self, client):
        """测试连接测试缺少数据"""
        response = client.post('/api/v1/database/test-connection')
        assert response.status_code == 400
        
        data = json.loads(response.data)
        assert data['success'] is False


class TestErrorHandling:
    """错误处理测试"""
    
    def test_404_error(self, client):
        """测试404错误"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['code'] == 404
    
    def test_405_error(self, client):
        """测试405错误"""
        response = client.get('/api/v1/image/generate')
        assert response.status_code == 405
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert data['code'] == 405
