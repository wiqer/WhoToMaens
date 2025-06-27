# BugAgaric API 接口文档

## 📋 概述

BugAgaric 提供了一套完整的API接口，支持文档管理、搜索、对话、模型服务等功能。系统采用微服务架构，包含Go服务和Python服务两大部分。

## 🏗️ 架构概览

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端界面       │    │   Go API服务     │    │  Python微服务    │
│                 │    │                 │    │                 │
│ • Streamlit UI  │◄──►│ • 认证服务       │◄──►│ • LLM服务       │
│ • React前端     │    │ • 文档管理       │    │ • Embedding服务  │
│ • 用户界面      │    │ • 搜索服务       │    │ • Reranker服务   │
│                 │    │ • 对话服务       │    │ • 缓存服务      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔐 认证机制

所有API请求都需要JWT认证，在请求头中包含：
```
Authorization: Bearer <your-jwt-token>
```

## 📚 API分类

### 1. Go服务API (主服务)
- **基础URL**: `/api`
- **端口**: 8080
- **功能**: 认证、文档管理、搜索、对话、缓存

### 2. Python微服务API
- **LLM服务**: `/chat` (端口: 8000)
- **Embedding服务**: `/embed` (端口: 8001)  
- **Reranker服务**: `/rerank` (端口: 8002)

### 3. 缓存服务API
- **基础URL**: `/cache`
- **端口**: 8003
- **功能**: 缓存管理、统计信息

---

## 🚀 Go服务API详细文档

### 认证接口

#### 用户登录
```http
POST /auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**响应**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": 1640995200
}
```

#### 用户注册
```http
POST /auth/register
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "email": "string"
}
```

**响应**:
```json
{
  "message": "用户注册成功",
  "user_id": "user_123"
}
```

### 文档管理接口

#### 上传文档
```http
POST /documents/upload
Content-Type: multipart/form-data

file: [文件]
metadata: {
  "title": "文档标题",
  "description": "文档描述",
  "tags": ["标签1", "标签2"]
}
```

**响应**:
```json
{
  "document_id": "doc_123",
  "message": "文档上传成功"
}
```

#### 获取文档列表
```http
GET /documents?page=1&limit=10&tag=技术文档
```

**响应**:
```json
{
  "total": 100,
  "page": 1,
  "limit": 10,
  "results": [
    {
      "id": "doc_123",
      "title": "文档标题",
      "content": "文档内容摘要",
      "tags": ["技术文档"],
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### 获取文档详情
```http
GET /documents/{id}
```

#### 删除文档
```http
DELETE /documents/{id}
```

### 搜索接口

#### 搜索文档
```http
POST /search
Content-Type: application/json

{
  "query": "搜索关键词",
  "tags": ["技术文档"],
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "page": 1,
  "limit": 10
}
```

**响应**:
```json
{
  "total": 50,
  "page": 1,
  "limit": 10,
  "results": [
    {
      "id": "doc_123",
      "title": "相关文档标题",
      "content": "匹配的内容片段",
      "score": 0.95,
      "tags": ["技术文档"]
    }
  ]
}
```

#### 获取搜索历史
```http
GET /search/history?limit=10
```

**响应**:
```json
[
  {
    "id": "search_123",
    "query": "搜索关键词",
    "timestamp": "2024-01-01T00:00:00Z"
  }
]
```

### 对话接口

#### 创建对话会话
```http
POST /chat/sessions
Content-Type: application/json

{
  "title": "会话标题"
}
```

**响应**:
```json
{
  "session_id": "session_123",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 获取会话列表
```http
GET /chat/sessions
```

**响应**:
```json
[
  {
    "session_id": "session_123",
    "title": "会话标题",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### 发送消息
```http
POST /chat/messages
Content-Type: application/json

{
  "session_id": "session_123",
  "content": "用户消息内容",
  "stream": false
}
```

**响应**:
```json
{
  "message_id": "msg_123",
  "response": "AI回复内容",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

#### 获取对话历史
```http
GET /chat/history?id=session_123
```

**响应**:
```json
[
  {
    "role": "user",
    "content": "用户消息",
    "timestamp": "2024-01-01T00:00:00Z"
  },
  {
    "role": "assistant", 
    "content": "AI回复",
    "timestamp": "2024-01-01T00:00:01Z"
  }
]
```

### 缓存与统计接口

#### 缓存预热
```http
POST /api/v1/cache/warmup
Content-Type: application/json

{
  "cache_items": [
    {"key": "item1", "value": "value1"}
  ],
  "search_suggestions": ["建议1", "建议2"],
  "hot_search_terms": ["热门词1", "热门词2"]
}
```

#### 获取统计信息
```http
GET /api/v1/stats
```

**响应**:
```json
{
  "cache_hits": 1000,
  "cache_misses": 50,
  "total_documents": 500,
  "total_users": 100
}
```

---

## 🐍 Python微服务API详细文档

### LLM服务 (端口: 8000)

#### 聊天接口
```http
POST /chat
Content-Type: multipart/form-data

data: {
  "messages": [
    {"role": "user", "content": "你好"}
  ],
  "stream": false
}
```

**响应**:
```json
{
  "role": "assistant",
  "content": "你好！我是AI助手，有什么可以帮助你的吗？"
}
```

**流式响应** (stream=true):
```
data: {"role": "assistant", "content": "你好"}

data: {"role": "assistant", "content": "！我是AI助手"}

data: {"role": "assistant", "content": "，有什么可以帮助你的吗？"}

data: [DONE]
```

### Embedding服务 (端口: 8001)

#### 生成嵌入向量
```http
POST /embed
Content-Type: application/json

{
  "texts": ["文本1", "文本2", "文本3"]
}
```

**响应**:
```json
[
  [0.1, 0.2, 0.3, ...],
  [0.4, 0.5, 0.6, ...],
  [0.7, 0.8, 0.9, ...]
]
```

### Reranker服务 (端口: 8002)

#### 重排序
```http
POST /rerank
Content-Type: application/json

{
  "query": "查询文本",
  "texts": ["候选文本1", "候选文本2", "候选文本3"]
}
```

**响应**:
```json
[
  {"text": "候选文本2", "score": 0.95},
  {"text": "候选文本1", "score": 0.85},
  {"text": "候选文本3", "score": 0.75}
]
```

---

## 💾 缓存服务API详细文档

### 缓存操作

#### 设置缓存
```http
POST /cache/{key}
Content-Type: application/json

{
  "value": "缓存值",
  "ttl": 3600
}
```

#### 获取缓存
```http
GET /cache/{key}
```

#### 删除缓存
```http
DELETE /cache/{key}
```

### 缓存统计

#### 获取缓存统计
```http
GET /cache/stats
```

**响应**:
```json
{
  "hits": 1000,
  "misses": 50,
  "hit_rate": 0.95,
  "size": 1000,
  "memory_usage": "50MB"
}
```

#### 获取最常访问项
```http
GET /cache/frequent?limit=10
```

---

## 🔧 错误处理

### 错误响应格式
```json
{
  "error": {
    "code": 400,
    "message": "错误描述"
  }
}
```

### 常见错误码
| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数格式 |
| 401 | 未授权 | 提供有效的JWT令牌 |
| 403 | 禁止访问 | 检查用户权限 |
| 404 | 资源不存在 | 检查资源ID是否正确 |
| 413 | 文件过大 | 减小文件大小 |
| 415 | 不支持的文件类型 | 使用支持的文件格式 |
| 500 | 服务器内部错误 | 联系系统管理员 |

---

## 📊 数据模型

### Document模型
```json
{
  "id": "string",
  "title": "string", 
  "content": "string",
  "tags": ["string"],
  "metadata": {
    "file_size": "number",
    "file_type": "string",
    "upload_time": "string"
  },
  "created_at": "string",
  "updated_at": "string",
  "user_id": "string"
}
```

### ChatMessage模型
```json
{
  "id": "string",
  "session_id": "string",
  "role": "user|assistant",
  "content": "string",
  "timestamp": "string"
}
```

---

## 🚀 使用示例

### JavaScript/TypeScript示例
```javascript
// 登录获取令牌
const loginResponse = await fetch('/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'user', password: 'pass' })
});
const { token } = await loginResponse.json();

// 上传文档
const formData = new FormData();
formData.append('file', file);
formData.append('metadata', JSON.stringify({
  title: '文档标题',
  tags: ['技术文档']
}));

const uploadResponse = await fetch('/documents/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: formData
});

// 搜索文档
const searchResponse = await fetch('/search', {
  method: 'POST',
  headers: { 
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    query: '搜索关键词',
    page: 1,
    limit: 10
  })
});
```

### Python示例
```python
import requests

# 登录
response = requests.post('http://localhost:8080/auth/login', json={
    'username': 'user',
    'password': 'pass'
})
token = response.json()['token']

headers = {'Authorization': f'Bearer {token}'}

# 上传文档
with open('document.pdf', 'rb') as f:
    files = {'file': f}
    data = {'metadata': '{"title": "文档标题"}'}
    response = requests.post('http://localhost:8080/documents/upload', 
                           files=files, data=data, headers=headers)

# 搜索文档
response = requests.post('http://localhost:8080/search', 
                        json={'query': '搜索关键词'}, 
                        headers=headers)
```

---

## 📈 性能优化建议

1. **使用缓存**: 合理利用缓存服务减少重复计算
2. **批量操作**: 对于大量数据，使用批量接口
3. **流式响应**: 对于长文本生成，使用流式接口
4. **连接复用**: 保持HTTP连接复用
5. **压缩传输**: 启用gzip压缩

---

## 🔒 安全注意事项

1. **令牌安全**: 妥善保管JWT令牌，定期更新
2. **文件上传**: 限制文件大小和类型
3. **输入验证**: 对所有用户输入进行验证
4. **权限控制**: 实施适当的访问控制
5. **HTTPS**: 生产环境使用HTTPS

---

## 📞 技术支持

如有问题，请参考：
- [项目文档](../README.md)
- [部署指南](../deployment/installation.md)
- [常见问题](../user_guide/FAQ.md) 