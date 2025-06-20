#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用导入诊断脚本
"""

import sys
import os
import traceback
import importlib.util

def print_info(msg):
    print(f"[INFO] {msg}")

def print_error(msg):
    print(f"[ERROR] {msg}")

def print_success(msg):
    print(f"[SUCCESS] {msg}")

def check_python_environment():
    """检查Python环境"""
    print_info("=== Python环境检查 ===")
    print_info(f"Python版本: {sys.version}")
    print_info(f"Python路径: {sys.executable}")
    print_info(f"当前工作目录: {os.getcwd()}")
    print_info(f"Python路径: {sys.path[:3]}...")  # 只显示前3个路径
    
    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("在虚拟环境中")
    else:
        print_info("使用系统Python")
    
    # 检查conda环境
    conda_env = os.environ.get('CONDA_DEFAULT_ENV')
    if conda_env:
        print_success(f"Conda环境: {conda_env}")
    
    print()

def check_required_modules():
    """检查必需的模块"""
    print_info("=== 依赖模块检查 ===")
    
    required_modules = [
        'flask',
        'flask_cors', 
        'python_dotenv',
        'pymysql',
        'openai',
        'httpx'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print_success(f"✅ {module}")
        except ImportError as e:
            print_error(f"❌ {module}: {e}")
            missing_modules.append(module)
    
    if missing_modules:
        print_error(f"缺少模块: {missing_modules}")
        print_info("安装命令: pip install " + " ".join(missing_modules))
    
    print()

def check_app_structure():
    """检查应用结构"""
    print_info("=== 应用结构检查 ===")
    
    required_files = [
        'run.py',
        'app/__init__.py',
        'app/config.py',
        'app/utils/logger.py',
        'app/api/__init__.py',
        '.env'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print_success(f"✅ {file_path}")
        else:
            print_error(f"❌ {file_path} 不存在")
    
    print()

def test_step_by_step_import():
    """逐步测试导入"""
    print_info("=== 逐步导入测试 ===")
    
    # 测试基础模块
    try:
        import flask
        print_success("✅ flask 导入成功")
    except Exception as e:
        print_error(f"❌ flask 导入失败: {e}")
        return
    
    # 测试app模块
    try:
        import app
        print_success("✅ app 模块导入成功")
    except Exception as e:
        print_error(f"❌ app 模块导入失败: {e}")
        print_error(f"详细错误: {traceback.format_exc()}")
        return
    
    # 测试app.config
    try:
        from app.config import Config
        print_success("✅ app.config 导入成功")
    except Exception as e:
        print_error(f"❌ app.config 导入失败: {e}")
        print_error(f"详细错误: {traceback.format_exc()}")
        return
    
    # 测试app.utils.logger
    try:
        from app.utils.logger import setup_logger
        print_success("✅ app.utils.logger 导入成功")
    except Exception as e:
        print_error(f"❌ app.utils.logger 导入失败: {e}")
        print_error(f"详细错误: {traceback.format_exc()}")
        return
    
    # 测试app.api
    try:
        from app.api import register_blueprints
        print_success("✅ app.api 导入成功")
    except Exception as e:
        print_error(f"❌ app.api 导入失败: {e}")
        print_error(f"详细错误: {traceback.format_exc()}")
        return
    
    # 测试create_app
    try:
        from app import create_app
        print_success("✅ create_app 导入成功")
    except Exception as e:
        print_error(f"❌ create_app 导入失败: {e}")
        print_error(f"详细错误: {traceback.format_exc()}")
        return
    
    # 测试run.py
    try:
        import run
        print_success("✅ run 模块导入成功")
    except Exception as e:
        print_error(f"❌ run 模块导入失败: {e}")
        print_error(f"详细错误: {traceback.format_exc()}")
        return
    
    # 测试app实例
    try:
        from run import app
        print_success("✅ app 实例导入成功")
        print_success(f"App名称: {app.name}")
        print_success(f"App配置: {app.config.get('ENVIRONMENT', 'unknown')}")
    except Exception as e:
        print_error(f"❌ app 实例导入失败: {e}")
        print_error(f"详细错误: {traceback.format_exc()}")
        return
    
    print()

def check_environment_variables():
    """检查环境变量"""
    print_info("=== 环境变量检查 ===")
    
    # 检查.env文件
    if os.path.exists('.env'):
        print_success("✅ .env 文件存在")
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print_success("✅ .env 文件加载成功")
        except Exception as e:
            print_error(f"❌ .env 文件加载失败: {e}")
    else:
        print_error("❌ .env 文件不存在")
    
    # 检查关键环境变量
    important_vars = ['FLASK_ENV', 'QIANFAN_API_KEY', 'QIANFAN_SECRET_KEY']
    for var in important_vars:
        value = os.environ.get(var)
        if value:
            print_success(f"✅ {var}: {'*' * min(len(value), 10)}")
        else:
            print_info(f"⚠️ {var}: 未设置")
    
    print()

def main():
    """主函数"""
    print("🔍 Flask应用导入诊断")
    print("=" * 50)
    
    # 检查Python环境
    check_python_environment()
    
    # 检查依赖模块
    check_required_modules()
    
    # 检查应用结构
    check_app_structure()
    
    # 检查环境变量
    check_environment_variables()
    
    # 逐步测试导入
    test_step_by_step_import()
    
    print("=" * 50)
    print("🎯 诊断完成")
    print()
    print("💡 如果发现问题，请根据上述信息进行修复：")
    print("1. 安装缺少的依赖: pip install -r requirements.txt")
    print("2. 检查文件是否存在")
    print("3. 检查环境变量配置")
    print("4. 查看详细错误信息")

if __name__ == "__main__":
    main()
