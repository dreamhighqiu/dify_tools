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

# 检查并清理端口
check_and_kill_port() {
    local port=${1:-5000}

    print_info "检查端口 $port 使用情况..."

    # 查找占用端口的进程
    local pids=$(lsof -ti:$port 2>/dev/null)

    if [[ -n "$pids" ]]; then
        print_warning "端口 $port 被以下进程占用:"
        lsof -i:$port 2>/dev/null | head -10

        print_info "正在终止占用端口 $port 的进程..."

        # 尝试优雅关闭
        for pid in $pids; do
            if kill -0 $pid 2>/dev/null; then
                print_info "发送TERM信号给进程 $pid"
                kill -TERM $pid 2>/dev/null
            fi
        done

        # 等待2秒
        sleep 2

        # 检查是否还有进程占用端口
        local remaining_pids=$(lsof -ti:$port 2>/dev/null)

        if [[ -n "$remaining_pids" ]]; then
            print_warning "强制终止剩余进程..."
            for pid in $remaining_pids; do
                if kill -0 $pid 2>/dev/null; then
                    print_info "发送KILL信号给进程 $pid"
                    kill -9 $pid 2>/dev/null
                fi
            done

            # 再等待1秒
            sleep 1
        fi

        # 最终检查
        local final_pids=$(lsof -ti:$port 2>/dev/null)
        if [[ -z "$final_pids" ]]; then
            print_success "端口 $port 已清理完成"
        else
            print_error "无法清理端口 $port，请手动处理"
            return 1
        fi
    else
        print_success "端口 $port 可用"
    fi

    return 0
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

    # 检查并清理端口
    if ! check_and_kill_port $FLASK_PORT; then
        print_error "无法清理端口 $FLASK_PORT，启动失败"
        exit 1
    fi

    # 启动服务
    print_info "正在启动Flask服务..."
    python run.py
}

# 显示帮助信息
show_help() {
    echo "统一Flask服务启动脚本"
    echo ""
    echo "用法: $0 [选项] [端口]"
    echo ""
    echo "选项:"
    echo "  start     启动服务（默认）"
    echo "  test      只运行测试"
    echo "  demo      运行演示脚本"
    echo "  install   只安装依赖"
    echo "  kill      清理指定端口的进程"
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
    echo "  $0 kill 5000               # 清理5000端口"
    echo "  $0 kill                     # 清理默认端口(5000)"
    echo ""
    echo "注意:"
    echo "  - 启动服务时会自动清理端口占用"
    echo "  - macOS用户如遇端口5000被占用，可能是AirPlay服务"
    echo "  - 可在系统偏好设置->通用->隔空投送与接力中关闭AirPlay接收器"
}

# 运行演示
run_demo() {
    print_info "运行API演示..."

    # 检查服务是否运行
    port=${FLASK_PORT:-5000}

    print_info "检查服务状态..."
    if ! curl -s "http://localhost:$port/health" > /dev/null; then
        print_error "服务未运行在端口 $port"

        # 尝试检查其他常用端口
        for test_port in 5001 5002 5003; do
            if curl -s "http://localhost:$test_port/health" > /dev/null 2>&1; then
                print_info "发现服务运行在端口 $test_port"
                port=$test_port
                break
            fi
        done

        if ! curl -s "http://localhost:$port/health" > /dev/null; then
            print_error "未找到运行中的服务，请先启动服务"
            print_info "运行命令: $0 start"
            exit 1
        fi
    fi

    print_success "服务运行正常，端口: $port"
    python demo.py "http://localhost:$port"
}

# 清理端口
kill_port() {
    local port=${2:-${FLASK_PORT:-5000}}

    print_info "清理端口 $port..."

    if check_and_kill_port $port; then
        print_success "端口 $port 清理完成"
    else
        print_error "端口 $port 清理失败"
        exit 1
    fi
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
        "kill")
            kill_port "$@"
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
