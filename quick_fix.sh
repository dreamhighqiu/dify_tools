#!/bin/bash
# 快速修复生产环境依赖问题

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

# 检查conda环境
check_conda_env() {
    local env_name=${1:-"venv312"}
    
    print_info "检查conda环境: $env_name"
    
    if [[ "$CONDA_DEFAULT_ENV" == "$env_name" ]]; then
        print_success "conda环境已激活: $CONDA_DEFAULT_ENV"
        return 0
    else
        print_error "请先激活conda环境: conda activate $env_name"
        return 1
    fi
}

# 安装生产环境依赖
install_production_deps() {
    print_info "安装生产环境依赖..."
    
    # 检查并安装gunicorn
    if ! python -c "import gunicorn" 2>/dev/null; then
        print_info "安装gunicorn..."
        pip install gunicorn
        print_success "gunicorn安装完成"
    else
        print_success "gunicorn已安装"
    fi
    
    # 检查并安装其他可能需要的包
    local optional_packages=("supervisor" "psutil")
    
    for package in "${optional_packages[@]}"; do
        if ! python -c "import $package" 2>/dev/null; then
            print_info "安装可选包: $package"
            pip install "$package" || print_warning "$package 安装失败，但不影响基本功能"
        fi
    done
    
    print_success "生产环境依赖安装完成"
}

# 验证安装
verify_installation() {
    print_info "验证安装..."
    
    # 检查Python版本
    python_version=$(python --version)
    print_success "Python版本: $python_version"
    
    # 检查关键包
    local key_packages=("flask" "gunicorn")
    
    for package in "${key_packages[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            version=$(python -c "import $package; print(getattr($package, '__version__', 'unknown'))")
            print_success "$package 版本: $version"
        else
            print_error "$package 未安装"
            return 1
        fi
    done
    
    print_success "验证通过"
}

# 主函数
main() {
    echo "🔧 快速修复生产环境依赖"
    echo "=========================="
    
    # 检查conda环境
    if ! check_conda_env "venv312"; then
        exit 1
    fi
    
    # 安装依赖
    install_production_deps
    
    # 验证安装
    verify_installation
    
    echo ""
    print_success "修复完成！现在可以运行:"
    echo "  ./start_production.sh start"
    echo ""
}

main "$@"
