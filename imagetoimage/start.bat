@echo off
chcp 65001 >nul

echo === 图像生成Flask服务启动脚本 ===

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt

REM 检查配置文件
if not exist ".env" (
    echo 创建环境配置文件...
    copy config.env .env
    echo 请编辑 .env 文件配置你的API密钥
)

REM 启动服务
echo 启动Flask服务...
python app.py

pause 