# BugAgaric API 测试与调试指南

## 📋 概述

本文档提供了UltraRAG项目中API接口的测试和调试方法，包括测试工具、测试用例和常见问题解决方案。

## 🛠️ 测试工具推荐

### 1. 命令行工具
- **curl**: 基础HTTP请求测试
- **httpie**: 更友好的命令行HTTP客户端
- **wget**: 文件下载和基础请求

### 2. GUI工具
- **Postman**: 功能强大的API测试工具
- **Insomnia**: 轻量级API客户端
- **Thunder Client**: VS Code插件

### 3. 编程语言工具
- **Python**: requests库
- **JavaScript**: fetch API, axios
- **Go**: net/http包

## 🚀 环境准备

### 1. 启动服务
```bash
# 启动Go API服务
cd go-services/api
go run main.go

# 启动Python微服务
python bugagaric/server/run_server_hf_llm.py -host localhost -port 8000 -model_path models/llm -device cuda
python bugagaric/server/run_embedding.py -host localhost -port 8001 -model_path models/embedding -device cuda
python bugagaric/server/run_server_reranker.py -host localhost -port 8002 -model_path models/reranker -device cuda

# 启动缓存服务
cd go-services/cache-service
go run cmd/cache-service/main.go
```

### 2. 检查服务状态
```bash
# 检查端口占用
netstat -tulpn | grep :8080
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001
netstat -tulpn | grep :8002
netstat -tulpn | grep :8003

# 检查服务健康状态
curl http://localhost:8080/api/health
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health
curl http://localhost:8003/health
```

## 📝 API测试用例

### 🔐 认证API测试

#### 1. 用户注册
```bash
# curl测试
curl -X POST http://localhost:8080/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123",
    "email": "test@example.com"
  }'

# httpie测试
http POST localhost:8080/api/auth/register \
  username=testuser \
  password=testpass123 \
  email=test@example.com

# Python测试
import requests

response = requests.post('http://localhost:8080/api/auth/register', json={
    'username': 'testuser',
    'password': 'testpass123',
    'email': 'test@example.com'
})
print(response.status_code)
print(response.json())
```

#### 2. 用户登录
```bash
# curl测试
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass123"
  }'

# 保存token
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}' | jq -r '.token')
echo "Token: $TOKEN"
```

### 📄 文档管理API测试

#### 1. 上传文档
```bash
# 创建测试文件
echo "这是一个测试文档内容" > test_document.txt

# curl测试
curl -X POST http://localhost:8080/api/documents/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_document.txt" \
  -F 'metadata={"title": "测试文档", "description": "这是一个测试文档", "tags": ["测试", "文档"]}'

# Python测试
import requests

with open('test_document.txt', 'rb') as f:
    files = {'file': f}
    data = {
        'metadata': '{"title": "测试文档", "description": "这是一个测试文档", "tags": ["测试", "文档"]}'
    }
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.post(
        'http://localhost:8080/api/documents/upload',
        files=files,
        data=data,
        headers=headers
    )
    print(response.status_code)
    print(response.json())
```

#### 2. 获取文档列表
```bash
# curl测试
curl -X GET "http://localhost:8080/api/documents?page=1&limit=10" \
  -H "Authorization: Bearer $TOKEN"

# 带标签过滤
curl -X GET "http://localhost:8080/api/documents?page=1&limit=10&tag=测试" \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. 获取文档详情
```bash
# 假设文档ID为 doc_123
curl -X GET "http://localhost:8080/api/documents/doc_123" \
  -H "Authorization: Bearer $TOKEN"
```

#### 4. 删除文档
```bash
# 删除文档
curl -X DELETE "http://localhost:8080/api/documents/doc_123" \
  -H "Authorization: Bearer $TOKEN"
```

### 🔍 搜索API测试

#### 1. 搜索文档
```bash
# curl测试
curl -X POST http://localhost:8080/api/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "测试文档",
    "page": 1,
    "limit": 10,
    "tags": ["测试"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31"
  }'

# Python测试
import requests

response = requests.post(
    'http://localhost:8080/api/search',
    json={
        'query': '测试文档',
        'page': 1,
        'limit': 10,
        'tags': ['测试'],
        'start_date': '2024-01-01',
        'end_date': '2024-12-31'
    },
    headers={'Authorization': f'Bearer {token}'}
)
print(response.json())
```

#### 2. 获取搜索历史
```bash
curl -X GET "http://localhost:8080/api/search/history?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

### 💬 对话API测试

#### 1. 创建对话会话
```bash
curl -X POST http://localhost:8080/api/chat/sessions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title": "测试会话"}'
```

#### 2. 获取会话列表
```bash
curl -X GET http://localhost:8080/api/chat/sessions \
  -H "Authorization: Bearer $TOKEN"
```

#### 3. 发送消息
```bash
# 普通消息
curl -X POST http://localhost:8080/api/chat/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "session_id": "session_123",
    "content": "你好，请介绍一下UltraRAG",
    "stream": false
  }'

# 流式消息
curl -X POST http://localhost:8080/api/chat/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "session_id": "session_123",
    "content": "你好，请介绍一下UltraRAG",
    "stream": true
  }' \
  --no-buffer
```

### 🤖 Python微服务API测试

#### 1. LLM服务测试
```bash
# 聊天接口
curl -X POST http://localhost:8000/chat \
  -H "Authorization: Bearer $TOKEN" \
  -F 'data={"messages": [{"role": "user", "content": "你好"}], "stream": false}'

# Python测试
import requests

response = requests.post(
    'http://localhost:8000/chat',
    files={'data': ('data.json', '{"messages": [{"role": "user", "content": "你好"}], "stream": false}')},
    headers={'Authorization': f'Bearer {token}'}
)
print(response.json())
```

#### 2. Embedding服务测试
```bash
curl -X POST http://localhost:8001/embed \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"texts": ["这是一个测试文本", "这是另一个测试文本"]}'
```

#### 3. Reranker服务测试
```bash
curl -X POST http://localhost:8002/rerank \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "查询文本",
    "texts": ["候选文本1", "候选文本2", "候选文本3"]
  }'
```

### 💾 缓存服务API测试

#### 1. 设置缓存
```bash
curl -X POST http://localhost:8003/cache/test_key \
  -H "Content-Type: application/json" \
  -d '{"value": "test_value", "ttl": 3600}'
```

#### 2. 获取缓存
```bash
curl -X GET http://localhost:8003/cache/test_key
```

#### 3. 获取缓存统计
```bash
curl -X GET http://localhost:8003/cache/stats
```

## 🔍 调试技巧

### 1. 启用详细日志
```bash
# Go服务调试
export DEBUG=true
export LOG_LEVEL=debug
go run main.go

# Python服务调试
export PYTHONPATH=.
python -u bugagaric/server/run_server_hf_llm.py -host localhost -port 8000 -model_path models/llm -device cuda
```

### 2. 使用代理工具
```bash
# 使用mitmproxy监控请求
mitmproxy -p 8081

# 设置代理
export HTTP_PROXY=http://localhost:8081
export HTTPS_PROXY=http://localhost:8081
```

### 3. 网络调试
```bash
# 检查网络连接
telnet localhost 8080
telnet localhost 8000
telnet localhost 8001
telnet localhost 8002
telnet localhost 8003

# 检查端口状态
lsof -i :8080
lsof -i :8000
lsof -i :8001
lsof -i :8002
lsof -i :8003
```

## 🐛 常见问题与解决方案

### 1. 认证问题
**问题**: 401 Unauthorized
```bash
# 检查token格式
echo $TOKEN | cut -d. -f2 | base64 -d | jq .

# 重新获取token
TOKEN=$(curl -s -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "testpass123"}' | jq -r '.token')
```

**解决方案**:
- 确保token格式正确 (Bearer <token>)
- 检查token是否过期
- 验证用户凭据

### 2. 文件上传问题
**问题**: 413 Payload Too Large
```bash
# 检查文件大小
ls -lh test_document.txt

# 压缩文件
gzip test_document.txt
```

**解决方案**:
- 减小文件大小
- 检查服务器配置的最大文件大小
- 使用分块上传

### 3. 连接超时问题
**问题**: Connection timeout
```bash
# 检查服务状态
ps aux | grep python
ps aux | grep go

# 重启服务
pkill -f "run_server_hf_llm.py"
python bugagaric/server/run_server_hf_llm.py -host localhost -port 8000 -model_path models/llm -device cuda &
```

**解决方案**:
- 检查服务是否正常运行
- 验证端口配置
- 检查防火墙设置

### 4. 内存不足问题
**问题**: Out of memory
```bash
# 检查内存使用
free -h
ps aux --sort=-%mem | head -10

# 清理内存
sudo sync && sudo sysctl -w vm.drop_caches=3
```

**解决方案**:
- 增加系统内存
- 优化模型加载
- 使用更小的模型

### 5. GPU相关问题
**问题**: CUDA out of memory
```bash
# 检查GPU状态
nvidia-smi

# 清理GPU内存
sudo fuser -v /dev/nvidia*
```

**解决方案**:
- 减少batch size
- 使用CPU模式
- 清理GPU内存

## 📊 性能测试

### 1. 压力测试
```bash
# 使用ab进行压力测试
ab -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/documents

# 使用wrk进行压力测试
wrk -t12 -c400 -d30s -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/documents
```

### 2. 响应时间测试
```bash
# 测试响应时间
time curl -X GET "http://localhost:8080/api/documents" \
  -H "Authorization: Bearer $TOKEN"

# 批量测试
for i in {1..10}; do
  echo "Test $i:"
  time curl -s -X GET "http://localhost:8080/api/documents" \
    -H "Authorization: Bearer $TOKEN" > /dev/null
done
```

### 3. 内存使用测试
```bash
# 监控内存使用
watch -n 1 'ps aux | grep -E "(python|go)" | grep -v grep'

# 监控系统资源
htop
```

## 📝 测试报告模板

### API测试报告
```markdown
# API测试报告

## 测试环境
- 服务版本: v1.0.0
- 测试时间: 2024-01-01
- 测试工具: curl/Postman

## 测试结果

### 认证API
- [x] 用户注册 - 200 OK
- [x] 用户登录 - 200 OK
- [x] 用户登出 - 200 OK

### 文档管理API
- [x] 上传文档 - 200 OK
- [x] 获取文档列表 - 200 OK
- [x] 获取文档详情 - 200 OK
- [x] 删除文档 - 200 OK

### 搜索API
- [x] 搜索文档 - 200 OK
- [x] 获取搜索历史 - 200 OK

### 对话API
- [x] 创建会话 - 200 OK
- [x] 获取会话列表 - 200 OK
- [x] 发送消息 - 200 OK
- [x] 获取对话历史 - 200 OK

## 性能指标
- 平均响应时间: 150ms
- 最大响应时间: 500ms
- 成功率: 100%

## 问题记录
1. 无

## 建议
1. 优化大文件上传性能
2. 增加缓存机制
```

## 🔗 相关资源

- [API接口文档](./README.md)
- [API集成指南](./API_Integration_Guide.md)
- [错误码说明](./README.md#错误处理)
- [性能优化指南](../performance/optimization.md) 