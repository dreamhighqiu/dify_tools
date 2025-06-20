#!/bin/bash
# 生产环境Flask服务启动脚本
# 专为conda环境和生产部署设计

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

print_header() {
    echo -e "${PURPLE}[PRODUCTION]${NC} $1"
}

# 配置变量
CONDA_ENV_NAME=${CONDA_ENV:-"venv312"}
FLASK_ENV=${FLASK_ENV:-"production"}
FLASK_HOST=${FLASK_HOST:-"0.0.0.0"}
FLASK_PORT=${FLASK_PORT:-"5000"}
WORKERS=${WORKERS:-4}
TIMEOUT=${TIMEOUT:-30}
LOG_LEVEL=${LOG_LEVEL:-"info"}
PID_FILE=${PID_FILE:-"/tmp/flask_service.pid"}
LOG_DIR=${LOG_DIR:-"./logs"}

# 显示配置信息
show_config() {
    print_header "生产环境配置"
    echo "=================================="
    echo "🐍 Conda环境: $CONDA_ENV_NAME"
    echo "🌍 Flask环境: $FLASK_ENV"
    echo "🌐 监听地址: $FLASK_HOST:$FLASK_PORT"
    echo "👥 Worker数量: $WORKERS"
    echo "⏱️ 超时时间: ${TIMEOUT}s"
    echo "📊 日志级别: $LOG_LEVEL"
    echo "📁 日志目录: $LOG_DIR"
    echo "📄 PID文件: $PID_FILE"
    echo "=================================="
}

# 检查conda环境
check_conda() {
    print_info "检查conda环境..."
    
    if ! command -v conda &> /dev/null; then
        print_error "conda命令不可用，请确保conda已正确安装"
        exit 1
    fi
    
    # 初始化conda
    eval "$(conda shell.bash hook)"
    
    # 检查环境是否存在
    if ! conda env list | grep -q "^$CONDA_ENV_NAME "; then
        print_error "conda环境 '$CONDA_ENV_NAME' 不存在"
        print_info "可用的conda环境:"
        conda env list
        exit 1
    fi
    
    # 激活环境
    print_info "激活conda环境: $CONDA_ENV_NAME"
    conda activate "$CONDA_ENV_NAME"
    
    if [[ "$CONDA_DEFAULT_ENV" == "$CONDA_ENV_NAME" ]]; then
        print_success "conda环境激活成功: $CONDA_DEFAULT_ENV"
    else
        print_error "conda环境激活失败"
        exit 1
    fi
}

# 检查依赖
check_dependencies() {
    print_info "检查生产环境依赖..."

    # 检查必要的包
    local required_packages=("flask" "gunicorn")
    local missing_packages=()

    for package in "${required_packages[@]}"; do
        if ! python -c "import $package" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done

    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        print_warning "缺少以下依赖包: ${missing_packages[*]}"

        read -p "是否自动安装缺少的依赖? (Y/n): " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Nn]$ ]]; then
            print_error "请手动安装依赖: pip install ${missing_packages[*]}"
            exit 1
        else
            print_info "正在安装缺少的依赖..."

            for package in "${missing_packages[@]}"; do
                print_info "安装 $package..."
                if pip install "$package"; then
                    print_success "$package 安装成功"
                else
                    print_error "$package 安装失败"
                    exit 1
                fi
            done

            print_success "所有依赖安装完成"
        fi
    else
        print_success "依赖检查通过"
    fi
}

# 创建日志目录
setup_logging() {
    print_info "设置日志目录..."
    
    if [[ ! -d "$LOG_DIR" ]]; then
        mkdir -p "$LOG_DIR"
        print_success "日志目录已创建: $LOG_DIR"
    else
        print_success "日志目录已存在: $LOG_DIR"
    fi
}

# 检查并清理端口
check_port() {
    print_info "检查端口 $FLASK_PORT..."
    
    local pids=$(lsof -ti:$FLASK_PORT 2>/dev/null)
    
    if [[ -n "$pids" ]]; then
        print_warning "端口 $FLASK_PORT 被占用，进程ID: $pids"
        
        # 检查是否是我们的服务
        if [[ -f "$PID_FILE" ]]; then
            local old_pid=$(cat "$PID_FILE")
            if echo "$pids" | grep -q "$old_pid"; then
                print_info "发现旧的服务进程，正在停止..."
                stop_service
                sleep 2
            fi
        fi
        
        # 再次检查端口
        pids=$(lsof -ti:$FLASK_PORT 2>/dev/null)
        if [[ -n "$pids" ]]; then
            print_error "端口 $FLASK_PORT 仍被占用，请手动处理"
            exit 1
        fi
    fi
    
    print_success "端口 $FLASK_PORT 可用"
}

# 启动服务
start_service() {
    print_header "启动生产服务"
    
    # 检查环境
    check_conda
    check_dependencies
    setup_logging
    check_port
    
    # 设置环境变量
    export FLASK_ENV="$FLASK_ENV"
    export FLASK_HOST="$FLASK_HOST"
    export FLASK_PORT="$FLASK_PORT"
    
    print_info "启动Gunicorn服务器..."
    
    # 启动gunicorn
    gunicorn \
        --bind "$FLASK_HOST:$FLASK_PORT" \
        --workers "$WORKERS" \
        --timeout "$TIMEOUT" \
        --log-level "$LOG_LEVEL" \
        --access-logfile "$LOG_DIR/access.log" \
        --error-logfile "$LOG_DIR/error.log" \
        --pid "$PID_FILE" \
        --daemon \
        run:app
    
    # 检查启动状态
    sleep 2
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            print_success "服务启动成功，PID: $pid"
            print_info "访问地址: http://$FLASK_HOST:$FLASK_PORT"
            print_info "健康检查: http://$FLASK_HOST:$FLASK_PORT/health"
        else
            print_error "服务启动失败"
            exit 1
        fi
    else
        print_error "PID文件未创建，服务可能启动失败"
        exit 1
    fi
}

# 停止服务
stop_service() {
    print_info "停止服务..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        
        if kill -0 "$pid" 2>/dev/null; then
            print_info "发送TERM信号给进程 $pid"
            kill -TERM "$pid"
            
            # 等待进程结束
            local count=0
            while kill -0 "$pid" 2>/dev/null && [[ $count -lt 10 ]]; do
                sleep 1
                ((count++))
            done
            
            if kill -0 "$pid" 2>/dev/null; then
                print_warning "进程未响应TERM信号，发送KILL信号"
                kill -9 "$pid"
            fi
            
            print_success "服务已停止"
        else
            print_warning "进程 $pid 不存在"
        fi
        
        rm -f "$PID_FILE"
    else
        print_warning "PID文件不存在"
        
        # 尝试通过端口查找进程
        local pids=$(lsof -ti:$FLASK_PORT 2>/dev/null)
        if [[ -n "$pids" ]]; then
            print_info "通过端口找到进程: $pids"
            for pid in $pids; do
                kill -TERM "$pid" 2>/dev/null
            done
            print_success "进程已终止"
        fi
    fi
}

# 重启服务
restart_service() {
    print_info "重启服务..."
    stop_service
    sleep 2
    start_service
}

# 查看服务状态
status_service() {
    print_info "检查服务状态..."
    
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        
        if kill -0 "$pid" 2>/dev/null; then
            print_success "服务运行中，PID: $pid"
            
            # 检查端口
            if lsof -i:$FLASK_PORT | grep -q "$pid"; then
                print_success "端口 $FLASK_PORT 正常监听"
            else
                print_warning "端口 $FLASK_PORT 未监听"
            fi
            
            # 健康检查
            if curl -s "http://localhost:$FLASK_PORT/health" > /dev/null; then
                print_success "健康检查通过"
            else
                print_warning "健康检查失败"
            fi
        else
            print_error "服务未运行（PID文件存在但进程不存在）"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "服务未运行（PID文件不存在）"
    fi
}

# 查看日志
show_logs() {
    local log_type=${1:-"error"}
    local lines=${2:-50}
    
    case "$log_type" in
        "access")
            if [[ -f "$LOG_DIR/access.log" ]]; then
                print_info "显示访问日志（最后${lines}行）:"
                tail -n "$lines" "$LOG_DIR/access.log"
            else
                print_warning "访问日志文件不存在"
            fi
            ;;
        "error")
            if [[ -f "$LOG_DIR/error.log" ]]; then
                print_info "显示错误日志（最后${lines}行）:"
                tail -n "$lines" "$LOG_DIR/error.log"
            else
                print_warning "错误日志文件不存在"
            fi
            ;;
        *)
            print_error "未知的日志类型: $log_type"
            echo "可用类型: access, error"
            ;;
    esac
}

# 安装依赖
install_dependencies() {
    print_info "安装生产环境依赖..."

    # 检查conda环境
    check_conda

    # 安装基础依赖
    print_info "安装项目依赖..."
    if [[ -f "requirements.txt" ]]; then
        pip install -r requirements.txt
    else
        print_warning "requirements.txt 文件不存在"
    fi

    # 安装生产环境专用依赖
    local prod_packages=("gunicorn" "supervisor")

    for package in "${prod_packages[@]}"; do
        print_info "安装 $package..."
        pip install "$package"
    done

    print_success "依赖安装完成"
}

# 显示帮助信息
show_help() {
    echo "生产环境Flask服务管理脚本"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    查看服务状态"
    echo "  logs      查看日志 [access|error] [行数]"
    echo "  install   安装生产环境依赖"
    echo "  config    显示配置信息"
    echo "  help      显示帮助信息"
    echo ""
    echo "环境变量:"
    echo "  CONDA_ENV    conda环境名称 (默认: venv312)"
    echo "  FLASK_ENV    Flask环境 (默认: production)"
    echo "  FLASK_HOST   监听地址 (默认: 0.0.0.0)"
    echo "  FLASK_PORT   监听端口 (默认: 5000)"
    echo "  WORKERS      Worker进程数 (默认: 4)"
    echo "  TIMEOUT      请求超时时间 (默认: 30)"
    echo "  LOG_LEVEL    日志级别 (默认: info)"
    echo "  LOG_DIR      日志目录 (默认: ./logs)"
    echo "  PID_FILE     PID文件路径 (默认: /tmp/flask_service.pid)"
    echo ""
    echo "示例:"
    echo "  $0 install                  # 安装生产环境依赖"
    echo "  $0 start                    # 启动服务"
    echo "  $0 stop                     # 停止服务"
    echo "  $0 restart                  # 重启服务"
    echo "  $0 status                   # 查看状态"
    echo "  $0 logs error 100           # 查看错误日志最后100行"
    echo "  WORKERS=8 $0 start          # 使用8个worker启动"
    echo "  FLASK_PORT=8080 $0 start    # 在8080端口启动"
}

# 主函数
main() {
    case "${1:-help}" in
        "start")
            show_config
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        "status")
            status_service
            ;;
        "logs")
            show_logs "${2:-error}" "${3:-50}"
            ;;
        "install")
            install_dependencies
            ;;
        "config")
            show_config
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
