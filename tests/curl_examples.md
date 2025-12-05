# Curl 测试命令示例

以下是一些用于测试 PDF 转换功能的 curl 命令示例。

## 基础测试

### 1. 健康检查
```bash
curl -X GET "http://localhost:8000/health"
```

### 2. 查看支持的格式
```bash
curl -X GET "http://localhost:8000/formats"
```

## Markdown 转 PDF

### 3. 文件上传方式（推荐）
```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@tests/test_files/sample.md" \
  -F "from=markdown" \
  -F "to=pdf" \
  -F "standalone=true" \
  --output output.pdf
```

### 4. JSON 接口方式
```bash
# 先编码文件内容
CONTENT=$(base64 -i tests/test_files/sample.md)

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
    print('PDF saved to output.pdf')
"
```

### 5. JSON-RPC 接口方式
```bash
# 先编码文件内容
CONTENT=$(base64 -i tests/test_files/sample.md)

curl -X POST "http://localhost:8000/rpc" \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"method\": \"convert\",
    \"params\": {
      \"from\": \"markdown\",
      \"to\": \"pdf\",
      \"content\": \"$CONTENT\",
      \"standalone\": true
    },
    \"id\": \"test-1\"
  }" | python3 -c "
import sys, json, base64
result = json.load(sys.stdin)
if 'result' in result and result.get('error') is None:
    content = base64.b64decode(result['result']['content'])
    with open('output.pdf', 'wb') as f:
        f.write(content)
    print('PDF saved to output.pdf')
"
```

## HTML 转 PDF

### 6. HTML 文件上传转 PDF
```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@tests/test_files/sample.html" \
  -F "from=html" \
  -F "to=pdf" \
  -F "standalone=true" \
  --output output.pdf
```

### 7. HTML 文本内容转 PDF（JSON）
```bash
# 创建简单的 HTML 内容
HTML_CONTENT="<html><body><h1>Test Document</h1><p>This is a test.</p></body></html>"
CONTENT=$(echo -n "$HTML_CONTENT" | base64)

curl -X POST "http://localhost:8000/convert/json" \
  -H "Content-Type: application/json" \
  -d "{
    \"from\": \"html\",
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
    print('PDF saved to output.pdf')
"
```

## 高级选项示例

### 8. 使用模板变量
```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@tests/test_files/sample.md" \
  -F "from=markdown" \
  -F "to=pdf" \
  -F "standalone=true" \
  -F "variables={\"title\":\"My Document\",\"author\":\"John Doe\"}" \
  --output output.pdf
```

### 9. 使用元数据
```bash
curl -X POST "http://localhost:8000/convert" \
  -F "file=@tests/test_files/sample.md" \
  -F "from=markdown" \
  -F "to=pdf" \
  -F "standalone=true" \
  -F "metadata={\"title\":\"Test Document\",\"author\":\"Test Author\"}" \
  --output output.pdf
```

## 快速测试脚本

运行完整的测试套件：
```bash
./tests/curl_tests.sh
```

## 注意事项

1. **文件路径**: 确保测试文件路径正确
2. **Base64 编码**: 在 JSON 接口中，文件内容需要 base64 编码
3. **输出文件**: 使用 `--output` 参数保存转换后的文件
4. **错误处理**: 检查 HTTP 状态码和响应内容

## 常见问题

### 问题：连接被拒绝
```bash
# 确保服务正在运行
docker-compose ps
# 或
curl http://localhost:8000/health
```

### 问题：文件未找到
```bash
# 检查文件是否存在
ls -la tests/test_files/sample.md
```

### 问题：转换失败
```bash
# 查看详细错误信息
curl -v -X POST "http://localhost:8000/convert" ...
```

