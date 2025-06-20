#!/bin/bash
# 修复应用导入问题的脚本

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

# 检查并修复Python路径问题
fix_python_path() {
    print_info "检查Python路径问题..."
    
    # 确保当前目录在Python路径中
    if ! python -c "import sys; print('.' in sys.path or '' in sys.path)" | grep -q True; then
        print_warning "当前目录不在Python路径中，添加到PYTHONPATH"
        export PYTHONPATH=".:$PYTHONPATH"
        print_success "PYTHONPATH已更新"
    fi
    
    # 检查工作目录
    if [[ ! -f "run.py" ]]; then
        print_error "当前目录中没有run.py文件"
        print_info "请确保在项目根目录中运行脚本"
        return 1
    fi
    
    print_success "Python路径检查通过"
}

# 检查并安装缺失的依赖
fix_dependencies() {
    print_info "检查并修复依赖问题..."
    
    # 检查requirements.txt
    if [[ ! -f "requirements.txt" ]]; then
        print_error "requirements.txt文件不存在"
        return 1
    fi
    
    # 检查关键依赖
    local missing_deps=()
    local required_deps=("flask" "flask_cors" "python_dotenv" "pymysql" "openai" "httpx")
    
    for dep in "${required_deps[@]}"; do
        if ! python -c "import $dep" 2>/dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_warning "发现缺失的依赖: ${missing_deps[*]}"
        print_info "正在安装缺失的依赖..."
        
        # 尝试安装缺失的依赖
        for dep in "${missing_deps[@]}"; do
            print_info "安装 $dep..."
            pip install "$dep" || print_warning "$dep 安装失败"
        done
        
        # 重新安装所有依赖
        print_info "重新安装所有依赖..."
        pip install -r requirements.txt
    else
        print_success "所有依赖都已安装"
    fi
}

# 检查并修复环境变量问题
fix_environment_vars() {
    print_info "检查环境变量配置..."
    
    # 检查.env文件
    if [[ ! -f ".env" ]]; then
        if [[ -f ".env.example" ]]; then
            print_warning ".env文件不存在，从.env.example复制"
            cp .env.example .env
            print_success ".env文件已创建"
        else
            print_error ".env.example文件也不存在"
            return 1
        fi
    fi
    
    # 加载环境变量
    if command -v python &> /dev/null; then
        python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('环境变量加载成功')
" 2>/dev/null || print_warning "环境变量加载失败"
    fi
    
    print_success "环境变量检查完成"
}

# 检查并修复文件权限问题
fix_file_permissions() {
    print_info "检查文件权限..."
    
    # 检查关键文件的可读性
    local key_files=("run.py" "app/__init__.py" "app/config.py" ".env")
    
    for file in "${key_files[@]}"; do
        if [[ -f "$file" ]]; then
            if [[ ! -r "$file" ]]; then
                print_warning "$file 不可读，修复权限"
                chmod +r "$file"
            fi
        fi
    done
    
    print_success "文件权限检查完成"
}

# 检查并修复模块导入问题
fix_module_imports() {
    print_info "检查模块导入问题..."
    
    # 检查app目录结构
    local required_dirs=("app" "app/api" "app/utils" "app/services")
    
    for dir in "${required_dirs[@]}"; do
        if [[ ! -d "$dir" ]]; then
            print_error "目录 $dir 不存在"
            return 1
        fi
        
        # 确保__init__.py文件存在
        if [[ ! -f "$dir/__init__.py" ]]; then
            print_warning "$dir/__init__.py 不存在，创建空文件"
            touch "$dir/__init__.py"
        fi
    done
    
    print_success "模块结构检查完成"
}

# 测试应用导入
test_app_import() {
    print_info "测试应用导入..."
    
    # 逐步测试导入
    local test_imports=(
        "import flask"
        "import app"
        "from app import create_app"
        "from run import app"
    )
    
    for import_test in "${test_imports[@]}"; do
        if python -c "$import_test; print('✅ $import_test')" 2>/dev/null; then
            print_success "$import_test"
        else
            print_error "$import_test 失败"
            print_info "详细错误信息:"
            python -c "$import_test" 2>&1 | head -5
            return 1
        fi
    done
    
    print_success "应用导入测试通过"
}

# 创建临时测试脚本
create_test_script() {
    print_info "创建测试脚本..."
    
    cat > test_import.py << 'EOF'
#!/usr/bin/env python3
import sys
import os

print(f"Python版本: {sys.version}")
print(f"工作目录: {os.getcwd()}")
print(f"Python路径: {sys.path[:3]}")

try:
    print("测试基础导入...")
    import flask
    print("✅ Flask导入成功")
    
    import app
    print("✅ app模块导入成功")
    
    from app import create_app
    print("✅ create_app导入成功")
    
    from run import app
    print("✅ app实例导入成功")
    
    print(f"✅ 应用名称: {app.name}")
    print("🎉 所有导入测试通过！")
    
except Exception as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF
    
    chmod +x test_import.py
    print_success "测试脚本已创建: test_import.py"
}

# 显示修复建议
show_fix_suggestions() {
    print_info "修复建议:"
    echo "1. 确保在项目根目录: cd /path/to/dify_tools"
    echo "2. 激活正确的Python环境: conda activate venv312"
    echo "3. 安装依赖: pip install -r requirements.txt"
    echo "4. 检查.env文件: cp .env.example .env"
    echo "5. 测试导入: python test_import.py"
    echo "6. 运行诊断: python diagnose_import.py"
}

# 主修复流程
main() {
    print_info "🔧 开始修复应用导入问题"
    echo "=================================="
    
    # 1. 修复Python路径
    if ! fix_python_path; then
        print_error "Python路径修复失败"
        exit 1
    fi
    
    # 2. 修复文件权限
    fix_file_permissions
    
    # 3. 修复模块结构
    if ! fix_module_imports; then
        print_error "模块结构修复失败"
        exit 1
    fi
    
    # 4. 修复环境变量
    if ! fix_environment_vars; then
        print_error "环境变量修复失败"
        exit 1
    fi
    
    # 5. 修复依赖
    fix_dependencies
    
    # 6. 创建测试脚本
    create_test_script
    
    # 7. 测试应用导入
    if test_app_import; then
        print_success "🎉 应用导入问题已修复！"
        print_info "现在可以运行: ./start.sh start"
    else
        print_error "应用导入仍然失败"
        print_info "请运行详细诊断: python diagnose_import.py"
        show_fix_suggestions
        exit 1
    fi
}

# 显示帮助
show_help() {
    echo "应用导入问题修复脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  fix       修复所有导入问题（默认）"
    echo "  test      只测试导入"
    echo "  deps      只修复依赖"
    echo "  env       只修复环境变量"
    echo "  help      显示帮助"
    echo ""
    echo "示例:"
    echo "  $0                # 修复所有问题"
    echo "  $0 test           # 只测试导入"
    echo "  $0 deps           # 只修复依赖"
}

# 执行主函数
case "${1:-fix}" in
    "fix")
        main
        ;;
    "test")
        test_app_import
        ;;
    "deps")
        fix_dependencies
        ;;
    "env")
        fix_environment_vars
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
