#!/bin/bash
# 环境检测和修复脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

# 检测当前环境
detect_environment() {
    print_info "🔍 检测当前Python环境"
    echo "=================================="
    
    # 检查conda
    if command -v conda &> /dev/null; then
        print_success "✅ conda已安装: $(conda --version)"
        
        if [[ "$CONDA_DEFAULT_ENV" != "" ]]; then
            print_success "✅ 当前conda环境: $CONDA_DEFAULT_ENV"
        else
            print_warning "⚠️ conda未激活任何环境"
        fi
        
        print_info "📋 可用conda环境:"
        conda env list | grep -v "^#" | while read line; do
            if [[ -n "$line" ]]; then
                echo "   $line"
            fi
        done
    else
        print_warning "⚠️ conda未安装或不在PATH中"
    fi
    
    echo ""
    
    # 检查Python venv
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "✅ 当前Python虚拟环境: $(basename $VIRTUAL_ENV)"
    else
        print_warning "⚠️ 未激活Python虚拟环境"
    fi
    
    # 检查本地venv目录
    if [[ -d ".venv" ]]; then
        print_success "✅ 发现本地.venv目录"
    else
        print_warning "⚠️ 未发现本地.venv目录"
    fi
    
    if [[ -d "venv" ]]; then
        print_success "✅ 发现本地venv目录"
    else
        print_warning "⚠️ 未发现本地venv目录"
    fi
    
    echo ""
    
    # 检查Python版本
    if command -v python &> /dev/null; then
        print_success "✅ Python: $(python --version) ($(which python))"
    else
        print_error "❌ python命令不可用"
    fi
    
    if command -v python3 &> /dev/null; then
        print_success "✅ Python3: $(python3 --version) ($(which python3))"
    else
        print_error "❌ python3命令不可用"
    fi
    
    echo ""
}

# 检查依赖
check_dependencies() {
    print_info "📦 检查Python依赖"
    echo "=================================="
    
    local required_packages=("flask" "gunicorn" "pymysql" "openai" "httpx")
    local missing_packages=()
    
    for package in "${required_packages[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            local version=$(python -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null || echo "unknown")
            print_success "✅ $package: $version"
        else
            print_error "❌ $package: 未安装"
            missing_packages+=("$package")
        fi
    done
    
    if [[ ${#missing_packages[@]} -gt 0 ]]; then
        echo ""
        print_warning "缺少以下依赖: ${missing_packages[*]}"
        print_info "可以运行以下命令安装:"
        echo "  pip install ${missing_packages[*]}"
        echo "  或者: pip install -r requirements.txt"
    fi
    
    echo ""
}

# 测试应用导入
test_app_import() {
    print_info "🧪 测试应用导入"
    echo "=================================="
    
    if python -c "from run import app; print('Flask应用导入成功')" 2>/dev/null; then
        print_success "✅ Flask应用导入成功"
    else
        print_error "❌ Flask应用导入失败"
        print_info "尝试获取详细错误信息:"
        python -c "from run import app" 2>&1 | head -10 || true
    fi
    
    echo ""
}

# 修复conda环境
fix_conda_env() {
    local env_name=${1:-"venv312"}
    
    print_info "🔧 修复conda环境: $env_name"
    echo "=================================="
    
    if ! command -v conda &> /dev/null; then
        print_error "conda未安装，无法修复"
        return 1
    fi
    
    # 初始化conda
    if [[ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
        source "$HOME/miniconda3/etc/profile.d/conda.sh"
    elif [[ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]]; then
        source "$HOME/anaconda3/etc/profile.d/conda.sh"
    else
        eval "$(conda shell.bash hook)" 2>/dev/null || true
    fi
    
    # 检查环境是否存在
    if ! conda env list | grep -q "^$env_name "; then
        print_warning "环境 $env_name 不存在，创建新环境..."
        conda create -n "$env_name" python=3.12 -y
        print_success "环境创建成功"
    fi
    
    # 激活环境
    conda activate "$env_name"
    
    if [[ "$CONDA_DEFAULT_ENV" == "$env_name" ]]; then
        print_success "环境激活成功: $CONDA_DEFAULT_ENV"
        
        # 安装依赖
        print_info "安装依赖..."
        pip install -r requirements.txt
        pip install gunicorn
        
        print_success "conda环境修复完成"
    else
        print_error "环境激活失败"
        return 1
    fi
}

# 修复Python venv
fix_python_venv() {
    local venv_path=${1:-".venv"}
    
    print_info "🔧 修复Python虚拟环境: $venv_path"
    echo "=================================="
    
    if ! command -v python3 &> /dev/null; then
        print_error "python3未安装，无法修复"
        return 1
    fi
    
    # 创建或重建虚拟环境
    if [[ -d "$venv_path" ]]; then
        print_warning "虚拟环境已存在，重新创建..."
        rm -rf "$venv_path"
    fi
    
    python3 -m venv "$venv_path"
    print_success "虚拟环境创建成功"
    
    # 激活环境
    source "$venv_path/bin/activate"
    
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        print_success "虚拟环境激活成功: $(basename $VIRTUAL_ENV)"
        
        # 升级pip
        pip install --upgrade pip
        
        # 安装依赖
        print_info "安装依赖..."
        pip install -r requirements.txt
        pip install gunicorn
        
        print_success "Python虚拟环境修复完成"
    else
        print_error "虚拟环境激活失败"
        return 1
    fi
}

# 显示修复建议
show_recommendations() {
    print_info "💡 修复建议"
    echo "=================================="
    
    echo "根据检测结果，建议采取以下行动:"
    echo ""
    
    if command -v conda &> /dev/null; then
        echo "🐍 Conda环境修复:"
        echo "  $0 fix-conda [环境名]     # 修复conda环境 (默认: venv312)"
        echo "  conda activate venv312    # 手动激活conda环境"
        echo ""
    fi
    
    echo "🐍 Python venv修复:"
    echo "  $0 fix-venv [路径]        # 修复Python虚拟环境 (默认: .venv)"
    echo "  source .venv/bin/activate # 手动激活Python虚拟环境"
    echo ""
    
    echo "📦 依赖安装:"
    echo "  pip install -r requirements.txt"
    echo "  pip install gunicorn"
    echo ""
    
    echo "🚀 启动服务:"
    echo "  ./start.sh start          # 自动检测环境并启动"
    echo "  USE_CONDA=true ./start.sh start   # 强制使用conda"
    echo "  USE_CONDA=false ./start.sh start  # 强制使用Python venv"
}

# 显示帮助
show_help() {
    echo "环境检测和修复脚本"
    echo ""
    echo "用法: $0 [命令] [参数]"
    echo ""
    echo "命令:"
    echo "  detect        检测当前环境状态"
    echo "  check         检查依赖和应用"
    echo "  fix-conda     修复conda环境 [环境名]"
    echo "  fix-venv      修复Python虚拟环境 [路径]"
    echo "  recommend     显示修复建议"
    echo "  help          显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 detect                 # 检测环境"
    echo "  $0 fix-conda venv312      # 修复conda环境"
    echo "  $0 fix-venv .venv         # 修复Python虚拟环境"
}

# 主函数
main() {
    case "${1:-detect}" in
        "detect")
            detect_environment
            ;;
        "check")
            check_dependencies
            test_app_import
            ;;
        "fix-conda")
            fix_conda_env "${2:-venv312}"
            ;;
        "fix-venv")
            fix_python_venv "${2:-.venv}"
            ;;
        "recommend")
            show_recommendations
            ;;
        "all")
            detect_environment
            check_dependencies
            test_app_import
            show_recommendations
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

main "$@"
