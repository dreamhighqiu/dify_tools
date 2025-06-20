#!/bin/bash
# 统一Flask服务启动脚本 - 生产环境专用
# 支持conda环境，自动端口清理，后台服务管理

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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
LOG_DIR=${LOG_DIR:-"./logs"}
PID_FILE=${PID_FILE:-"/tmp/flask_service.pid"}

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
    
    local required_packages=("flask" "gunicorn")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if ! python -c "import $package" 2>/dev/null; then
            missing_packages+=("$package")
        fi
    done
    
    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        print_error "缺少以下依赖包: ${missing_packages[*]}"
        print_info "请运行: pip install ${missing_packages[*]}"
        exit 1
    fi
    
    print_success "依赖检查通过"
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
check_and_kill_port() {
    local port=${1:-5000}
    
    print_info "检查端口 $port 使用情况..."
    
    local pids=$(lsof -ti:$port 2>/dev/null)
    
    if [[ -n "$pids" ]]; then
        print_warning "端口 $port 被以下进程占用: $pids"
        
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
        pids=$(lsof -ti:$port 2>/dev/null)
        if [[ -n "$pids" ]]; then
            print_warning "强制清理端口 $port 上的进程..."
            
            # 尝试优雅关闭
            for pid in $pids; do
                if kill -0 $pid 2>/dev/null; then
                    print_info "发送TERM信号给进程 $pid"
                    kill -TERM $pid 2>/dev/null || true
                fi
            done
            
            # 等待进程结束
            sleep 3
            
            # 检查是否还有进程
            local remaining_pids=$(lsof -ti:$port 2>/dev/null)
            if [[ -n "$remaining_pids" ]]; then
                print_warning "强制终止剩余进程..."
                for pid in $remaining_pids; do
                    if kill -0 $pid 2>/dev/null; then
                        print_info "发送KILL信号给进程 $pid"
                        kill -9 $pid 2>/dev/null || true
                    fi
                done
                
                # 最后检查
                sleep 1
                local final_pids=$(lsof -ti:$port 2>/dev/null)
                if [[ -n "$final_pids" ]]; then
                    print_error "无法清理端口 $port，请手动处理: kill -9 $final_pids"
                    exit 1
                fi
            fi
            
            print_success "端口 $port 已清理完成"
        fi
    else
        print_success "端口 $port 可用"
    fi
    
    return 0
}

# 启动服务
start_service() {
    print_header "启动生产服务"
    
    # 检查环境
    check_conda
    check_dependencies
    setup_logging
    check_and_kill_port $FLASK_PORT
    
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
        --preload \
        --worker-class sync \
        --max-requests 1000 \
        --max-requests-jitter 100 \
        run:app
    
    local gunicorn_exit_code=$?
    
    if [[ $gunicorn_exit_code -ne 0 ]]; then
        print_error "Gunicorn启动失败，退出码: $gunicorn_exit_code"
        print_info "检查错误日志: $LOG_DIR/error.log"
        if [[ -f "$LOG_DIR/error.log" ]]; then
            print_info "最近的错误日志:"
            tail -n 10 "$LOG_DIR/error.log"
        fi
        exit 1
    fi
    
    # 检查启动状态
    sleep 3
    if [[ -f "$PID_FILE" ]]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            print_success "服务启动成功，PID: $pid"
            print_info "访问地址: http://$FLASK_HOST:$FLASK_PORT"
            print_info "健康检查: http://$FLASK_HOST:$FLASK_PORT/health"
            
            # 健康检查
            sleep 2
            if curl -s "http://localhost:$FLASK_PORT/health" > /dev/null; then
                print_success "健康检查通过 ✅"
            else
                print_warning "健康检查失败，请检查服务状态"
            fi
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

# 显示帮助信息
show_help() {
    echo "Flask生产环境服务管理脚本"
    echo ""
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    查看服务状态"
    echo "  logs      查看日志 [access|error] [行数]"
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
    echo ""
    echo "示例:"
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
