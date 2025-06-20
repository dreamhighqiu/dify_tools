#!/bin/bash
# 统一Flask服务启动脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python() {
    print_info "检查Python版本..."
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    python_version=$(python3 --version | cut -d' ' -f2)
    print_success "Python版本: $python_version"
}

# 检查虚拟环境
check_venv() {
    print_info "检查虚拟环境..."
    
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "虚拟环境已激活: $VIRTUAL_ENV"
    else
        print_warning "虚拟环境未激活"
        
        if [[ -d "venv" ]]; then
            print_info "发现虚拟环境目录，尝试激活..."
            source venv/bin/activate
            print_success "虚拟环境已激活"
        else
            print_info "创建虚拟环境..."
            python3 -m venv venv
            source venv/bin/activate
            print_success "虚拟环境已创建并激活"
        fi
    fi
}

# 安装依赖
install_dependencies() {
    print_info "安装依赖包..."
    
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
        print_success "依赖包安装完成"
    else
        print_error "requirements.txt 文件不存在"
        exit 1
    fi
}

# 检查环境变量
check_env() {
    print_info "检查环境配置..."
    
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            print_warning ".env 文件不存在，从 .env.example 复制..."
            cp .env.example .env
            print_warning "请编辑 .env 文件配置相关参数"
        else
            print_error ".env.example 文件不存在"
            exit 1
        fi
    else
        print_success "环境配置文件存在"
    fi
}

# 运行测试
run_tests() {
    print_info "运行测试..."
    
    if command -v pytest &> /dev/null; then
        pytest tests/ -v
        print_success "测试完成"
    else
        print_warning "pytest 未安装，跳过测试"
    fi
}

# 启动服务
start_service() {
    print_info "启动Flask服务..."
    
    # 设置环境变量
    export FLASK_ENV=${FLASK_ENV:-development}
    export FLASK_HOST=${FLASK_HOST:-0.0.0.0}
    export FLASK_PORT=${FLASK_PORT:-5000}
    
    print_info "服务配置:"
    print_info "  - 环境: $FLASK_ENV"
    print_info "  - 地址: $FLASK_HOST:$FLASK_PORT"
    
    # 启动服务
    python run.py
}

# 显示帮助信息
show_help() {
    echo "统一Flask服务启动脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  start     启动服务（默认）"
    echo "  test      只运行测试"
    echo "  demo      运行演示脚本"
    echo "  install   只安装依赖"
    echo "  help      显示帮助信息"
    echo ""
    echo "环境变量:"
    echo "  FLASK_ENV    运行环境 (development/testing/production)"
    echo "  FLASK_HOST   监听地址 (默认: 0.0.0.0)"
    echo "  FLASK_PORT   监听端口 (默认: 5000)"
    echo ""
    echo "示例:"
    echo "  $0 start                    # 启动开发服务器"
    echo "  FLASK_ENV=production $0     # 启动生产服务器"
    echo "  FLASK_PORT=8080 $0          # 在8080端口启动"
    echo "  $0 test                     # 只运行测试"
    echo "  $0 demo                     # 运行API演示"
}

# 运行演示
run_demo() {
    print_info "运行API演示..."
    
    # 检查服务是否运行
    port=${FLASK_PORT:-5000}
    if ! curl -s "http://localhost:$port/health" > /dev/null; then
        print_error "服务未运行，请先启动服务"
        print_info "在另一个终端运行: $0 start"
        exit 1
    fi
    
    python demo.py "http://localhost:$port"
}

# 主函数
main() {
    echo "🚀 统一Flask服务启动脚本"
    echo "=================================="
    
    case "${1:-start}" in
        "start")
            check_python
            check_venv
            install_dependencies
            check_env
            start_service
            ;;
        "test")
            check_python
            check_venv
            install_dependencies
            run_tests
            ;;
        "demo")
            check_python
            check_venv
            run_demo
            ;;
        "install")
            check_python
            check_venv
            install_dependencies
            check_env
            print_success "安装完成"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
