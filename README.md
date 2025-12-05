# Pandoc Converter Service

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.123-green.svg)](https://fastapi.tiangolo.com/)
[![Pandoc](https://img.shields.io/badge/Pandoc-3.8.3-orange.svg)](https://pandoc.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

基于 FastAPI 和 Pandoc 的文档转换 HTTP 服务，支持多种文档格式之间的转换（HTML、Markdown、DOCX、PDF 等）。

## 📋 目录

- [功能特性](#功能特性)
- [技术栈](#技术栈)
- [快速开始](#快速开始)
- [API 接口](#api-接口)
- [使用示例](#使用示例)
- [测试](#测试)
- [项目结构](#项目结构)
- [部署](#部署)
- [故障排查](#故障排查)
- [贡献](#贡献)
- [许可证](#许可证)

## 功能特性

- **多格式支持**: 支持 Pandoc 支持的所有输入和输出格式
- **多种接口**: 提供 JSON-RPC、RESTful JSON 和文件上传三种接口方式
- **完整参数支持**: 支持 Pandoc 的所有常用参数（standalone、template、variables、filters、metadata 等）
- **容器化部署**: 基于 Docker 和 Docker Compose 的容器化部署方案
- **健康检查**: 提供健康检查接口，便于监控和运维

## 技术栈

- **基础镜像**: `pandoc/latex:3.8.3-ubuntu`
- **Python 版本**: 3.13
- **Web 框架**: FastAPI
- **文档转换**: Pandoc (通过 subprocess 调用)
- **容器化**: Docker + Docker Compose

## 快速开始

### 使用 Docker Compose

```bash
# 构建并启动服务
docker-compose up --build

# 后台运行
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务启动后，可以通过以下地址访问：

- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health
- 服务信息: http://localhost:8000/

### 使用 Docker

```bash
# 构建镜像
docker build -t pandoc-converter-service .

# 运行容器
docker run -d -p 8000:8000 --name pandoc-converter pandoc-converter-service
```

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API 接口

### 1. 健康检查

```http
GET /health
```

返回服务健康状态和 Pandoc 版本信息。

### 2. 获取支持的格式

```http
GET /formats
```

返回 Pandoc 支持的所有输入和输出格式列表。

### 3. JSON-RPC 接口

兼容 Pandoc Server Mode 的 JSON-RPC 接口。

```http
POST /rpc
Content-Type: application/json
```

请求示例：

```json
{
  "jsonrpc": "2.0",
  "method": "convert",
  "params": {
    "from": "html",
    "to": "docx",
    "content": "base64_encoded_content",
    "standalone": true
  },
  "id": "request-1"
}
```

响应示例：

```json
{
  "jsonrpc": "2.0",
  "result": {
    "from": "html",
    "to": "docx",
    "content": "base64_encoded_output"
  },
  "id": "request-1"
}
```

### 4. RESTful 文件上传接口

```http
POST /convert
Content-Type: multipart/form-data
```

表单字段：

- `file`: 上传的文件
- `from`: 输入格式（如 `html`, `markdown`）
- `to`: 输出格式（如 `docx`, `pdf`）
- `standalone`: 是否生成独立文档（可选，布尔值）
- `template`: 模板文件路径（可选）
- `variables`: JSON 格式的变量（可选）
- `filters`: 逗号分隔的过滤器列表（可选）
- `metadata`: JSON 格式的元数据（可选）
- `extra_args`: JSON 格式的额外参数数组（可选）

### 5. RESTful JSON 接口

```http
POST /convert/json
Content-Type: application/json
```

请求示例：

```json
{
  "from": "markdown",
  "to": "pdf",
  "content": "base64_encoded_content",
  "standalone": true,
  "variables": {
    "title": "My Document"
  }
}
```

响应示例：

```json
{
  "success": true,
  "from": "markdown",
  "to": "pdf",
  "content": "base64_encoded_output",
  "filename": "output.pdf",
  "message": "Conversion successful"
}
```

## 使用示例

### HTML 转 DOCX

**文件上传方式（推荐）**：

```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@sample.html" \
  -F "from=html" \
  -F "to=docx" \
  -F "standalone=true" \
  --output output.docx
```

**JSON-RPC 方式**：

```bash
curl -X POST "http://localhost:8000/rpc" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "convert",
    "params": {
      "from": "html",
      "to": "docx",
      "content": "'$(base64 -i sample.html)'",
      "standalone": true
    },
    "id": "1"
  }'
```

### Markdown 转 PDF

**文件上传方式**：

```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@sample.md" \
  -F "from=markdown" \
  -F "to=pdf" \
  -F "standalone=true" \
  --output output.pdf
```

**JSON 接口方式**：

```bash
CONTENT=$(base64 -i sample.md)
curl -X POST "http://localhost:8000/convert/json" \
  -H "Content-Type: application/json" \
  -d "{
    \"from\": \"markdown\",
    \"to\": \"pdf\",
    \"content\": \"$CONTENT\",
    \"standalone\": true
  }" | python3 -c "
import sys, json, base64
result = json.load(sys.stdin)
if result.get('success'):
    content = base64.b64decode(result['content'])
    with open('output.pdf', 'wb') as f:
        f.write(content)
    print('PDF saved!')
"
```

更多 curl 示例请参考 [tests/curl_examples.md](tests/curl_examples.md)

## 测试

项目包含两个测试脚本：

1. **HTML 转 DOCX 测试**: `tests/test_html_to_docx.py`
2. **Markdown 转 PDF 测试**: `tests/test_markdown_to_pdf.py`

运行测试前，确保服务已启动：

```bash
# 安装测试依赖
pip install requests

# 运行 HTML 转 DOCX 测试
python tests/test_html_to_docx.py

# 运行 Markdown 转 PDF 测试
python tests/test_markdown_to_pdf.py
```

测试脚本会测试所有三种接口方式（文件上传、JSON、JSON-RPC），并将转换结果保存到 `tests/test_files/` 目录。

## 支持的格式

Pandoc 支持多种输入和输出格式，包括但不限于：

**输入格式**: markdown, html, docx, epub, latex, tex, rtf, odt, txt, plain 等

**输出格式**: docx, pdf, html, epub, latex, tex, rtf, odt, markdown, plain 等

可以通过 `/formats` 接口查看完整的格式列表。

## 配置参数

### Pandoc 参数说明

- `standalone`: 生成独立文档（包含完整的文档结构）
- `template`: 使用自定义模板文件
- `variables`: 模板变量（键值对）
- `filters`: Pandoc 过滤器列表
- `metadata`: 文档元数据
- `extra_args`: 额外的 Pandoc 命令行参数

### 环境变量

- `PYTHONUNBUFFERED`: 设置为 `1` 以禁用 Python 输出缓冲

## 项目结构

```
pandoc-converter-service/
├── app/                      # 应用代码
│   ├── __init__.py
│   ├── main.py              # FastAPI 应用入口
│   ├── models.py            # Pydantic 数据模型
│   ├── service.py           # Pandoc 转换服务逻辑
│   └── utils.py             # 工具函数
├── tests/                    # 测试文件
│   ├── test_html_to_docx.py # HTML 转 DOCX 测试
│   ├── test_markdown_to_pdf.py # Markdown 转 PDF 测试
│   ├── curl_tests.sh        # Curl 测试脚本
│   ├── curl_examples.md     # Curl 使用示例
│   └── test_files/          # 测试文件
│       ├── sample.html       # HTML 测试文件
│       └── sample.md         # Markdown 测试文件
├── requirements.txt          # Python 依赖
├── Dockerfile               # Docker 构建文件
├── docker-compose.yaml      # Docker Compose 配置
├── run_tests.sh            # 测试运行脚本
└── README.md               # 项目文档
```

## 部署

### Docker Compose 部署（推荐）

```bash
# 启动服务
docker-compose up -d --build

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### Kubernetes 部署

可以基于 Dockerfile 构建镜像并部署到 Kubernetes 集群。

### 生产环境建议

1. 使用反向代理（如 Nginx）处理 HTTPS
2. 配置适当的资源限制
3. 设置日志收集和监控
4. 使用健康检查进行自动重启

## 故障排查

### Pandoc 未找到

如果遇到 "Pandoc not found" 错误，请确保：

1. 使用正确的基础镜像 `pandoc/latex:3.8.3-ubuntu`
2. 容器内已正确安装 Pandoc

### 转换失败

如果转换失败，请检查：

1. 输入格式是否正确
2. 输出格式是否支持
3. 文件内容是否有效
4. 查看服务日志获取详细错误信息

### 端口冲突

如果端口 8000 已被占用，可以在 `docker-compose.yaml` 中修改端口映射：

```yaml
ports:
  - "8001:8000"  # 将主机端口改为 8001
```

## 开发

### 本地开发环境设置

```bash
# 克隆项目
git clone git@github.com:zzong12/pandoc-converter-service.git
cd pandoc-converter-service

# 安装依赖
pip install -r requirements.txt

# 运行服务（需要本地安装 Pandoc）
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 运行测试

```bash
# 确保服务已启动（使用 Docker）
docker-compose up -d

# 运行 Python 测试
python tests/test_html_to_docx.py
python tests/test_markdown_to_pdf.py

# 或运行测试脚本
./run_tests.sh

# 运行 curl 测试
./tests/curl_tests.sh
```

## 性能优化

- 使用 Docker 容器可以更好地隔离环境
- 对于高并发场景，可以考虑使用多个 worker 进程
- 大文件转换时注意超时设置

## 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 相关链接

- [Pandoc 官方文档](https://pandoc.org/MANUAL.html)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Docker 文档](https://docs.docker.com/)

## 作者

- **zzong12** - [GitHub](https://github.com/zzong12)

## 致谢

- 感谢 [Pandoc](https://pandoc.org/) 项目提供的强大文档转换工具
- 感谢 [FastAPI](https://fastapi.tiangolo.com/) 提供的优秀 Web 框架

