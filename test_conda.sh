#!/bin/bash
# Conda环境测试脚本

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 测试conda环境
test_conda_env() {
    local env_name=${1:-"venv312"}
    
    print_info "测试conda环境: $env_name"
    
    # 检查conda是否可用
    if ! command -v conda &> /dev/null; then
        print_error "conda命令不可用"
        return 1
    fi
    
    # 初始化conda
    eval "$(conda shell.bash hook)"
    
    # 检查环境是否存在
    if conda env list | grep -q "^$env_name "; then
        print_success "环境 $env_name 存在"
        
        # 尝试激活环境
        conda activate "$env_name"
        
        if [[ "$CONDA_DEFAULT_ENV" == "$env_name" ]]; then
            print_success "环境激活成功: $CONDA_DEFAULT_ENV"
            
            # 检查Python版本
            python_version=$(python --version)
            print_success "Python版本: $python_version"
            
            # 检查pip
            if command -v pip &> /dev/null; then
                pip_version=$(pip --version)
                print_success "pip版本: $pip_version"
            else
                print_error "pip不可用"
            fi
            
            return 0
        else
            print_error "环境激活失败"
            return 1
        fi
    else
        print_error "环境 $env_name 不存在"
        print_info "可用环境:"
        conda env list
        return 1
    fi
}

# 主函数
main() {
    echo "🐍 Conda环境测试"
    echo "=================="
    
    local env_name=${1:-"venv312"}
    
    if test_conda_env "$env_name"; then
        print_success "Conda环境测试通过"
        exit 0
    else
        print_error "Conda环境测试失败"
        exit 1
    fi
}

main "$@"
