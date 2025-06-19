#!/bin/bash

# 图像生成Flask服务启动脚本

echo "=== 图像生成Flask服务启动脚本 ==="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到Python3，请先安装Python3"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source venv/bin/activate

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt

# 检查配置文件
if [ ! -f ".env" ]; then
    echo "创建环境配置文件..."
    cp config.env .env
    echo "请编辑 .env 文件配置你的API密钥"
fi

# 启动服务
echo "启动Flask服务..."
python app.py 