# 图像生成Flask服务

这是一个基于Flask的图像生成服务，使用千帆API进行图像处理。

## 功能特性

- 基于参考图像生成新图像
- RESTful API接口
- 支持自定义提示词
- 完整的错误处理和日志记录
- 健康检查接口
- 环境变量配置管理

## 项目结构

```
.
├── app.py              # 主应用入口文件
├── imagetoimage.py     # 原始实现文件
├── requirements.txt    # Python依赖包
├── config.env          # 环境变量配置模板
├── start.sh           # Linux/Mac启动脚本
├── start.bat          # Windows启动脚本
├── test_api.py        # API测试脚本
└── README.md          # 项目说明文档
```

## 快速开始

### 方法一：使用启动脚本（推荐）

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```cmd
start.bat
```

### 方法二：手动安装

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
```bash
cp config.env .env
# 编辑 .env 文件，配置你的API密钥
```

4. 启动服务：
```bash
python app.py
```

## 配置说明

在 `.env` 文件中配置以下参数：

```env
# Flask应用配置
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
SECRET_KEY=your-secret-key-here

# 千帆API配置
QIANFAN_API_KEY=your_qianfan_api_key_here
QIANFAN_BASE_URL=https://qianfan.baidubce.com/v2
```

## API接口

### 健康检查
- **GET** `/health`
- 返回服务状态信息

### 图像生成
- **POST** `/get_img_info`

**请求体：**
```json
{
    "url": "参考图像的URL",
    "prompt": "图像生成提示词"
}
```

**成功响应：**
```json
{
    "success": true,
    "result": "生成图像的URL"
}
```

**错误响应：**
```json
{
    "success": false,
    "result": "错误信息"
}
```

## 测试

运行API测试：
```bash
python test_api.py
```

## 主要改进

相比原始版本，新版本包含以下改进：

1. **更好的项目结构**：分离了配置、应用逻辑和启动脚本
2. **环境变量管理**：使用 `.env` 文件管理敏感配置
3. **错误处理**：完善的异常处理和错误响应
4. **日志记录**：详细的日志记录便于调试
5. **健康检查**：添加了服务健康检查接口
6. **启动脚本**：自动化环境设置和启动流程
7. **测试脚本**：API接口测试工具
8. **文档完善**：详细的README和使用说明

## 依赖说明

- **Flask**: Web框架
- **openai**: OpenAI客户端库，用于调用千帆API
- **requests**: HTTP请求库
- **python-dotenv**: 环境变量管理
- **pytest**: 测试框架（可选）

## 注意事项

- 请确保API密钥的安全性
- 建议在生产环境中使用环境变量管理敏感信息
- 注意API调用频率限制
- 生产环境建议使用WSGI服务器（如Gunicorn）

## 故障排除

1. **端口被占用**：修改 `FLASK_PORT` 环境变量
2. **API调用失败**：检查API密钥和网络连接
3. **依赖安装失败**：确保Python版本兼容（建议3.8+） 