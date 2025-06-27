# BugAgaric API接口文档

## 📋 基础信息
- **Base URL**: `/api`
- **版本**: 1.0
- **认证方式**: JWT Token
- **响应格式**: JSON
- **字符编码**: UTF-8

## 🏗️ 系统架构

UltraRAG采用微服务架构，包含以下服务：

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

### 服务端口配置
- **Go API服务**: 8080
- **LLM服务**: 8000
- **Embedding服务**: 8001
- **Reranker服务**: 8002
- **缓存服务**: 8003
- **Streamlit UI**: 8843
- **React前端**: 3000

## 🔐 认证机制

### JWT Token格式
```
Authorization: Bearer <your-jwt-token>
```

### Token结构
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "user_123",
    "username": "testuser",
    "role": "user",
    "exp": 1640995200,
    "iat": 1640908800
  }
}
```

---

## 🚀 核心接口

### 1. 认证接口

#### 用户登录
```http
POST /auth/login
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

**响应示例**:
```json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": 1640995200,
  "user": {
    "id": "user_123",
    "username": "testuser",
    "email": "test@example.com",
    "role": "user"
  }
}
```

**错误响应**:
```json
{
  "error": {
    "code": 401,
    "message": "用户名或密码错误"
  }
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

**响应示例**:
```json
{
  "message": "用户注册成功",
  "user_id": "user_123",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### 用户登出
```http
POST /auth/logout
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "message": "登出成功"
}
```

### 2. 文档管理接口

#### 上传文档
```http
POST /documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file: [文件]
metadata: {
  "title": "文档标题",
  "description": "文档描述",
  "tags": ["标签1", "标签2"],
  "category": "技术文档"
}
```

**支持的文件格式**:
- PDF (.pdf)
- Word (.docx, .doc)
- Text (.txt)
- Markdown (.md)
- Excel (.xlsx, .xls)
- PowerPoint (.pptx, .ppt)

**文件大小限制**: 50MB

**响应示例**:
```json
{
  "document_id": "doc_123",
  "message": "文档上传成功",
  "file_info": {
    "filename": "document.pdf",
    "size": 1024000,
    "type": "application/pdf"
  },
  "processing_status": "completed"
}
```

#### 获取文档列表
```http
GET /documents?page=1&limit=10&tag=技术文档&category=技术文档&search=关键词
Authorization: Bearer <token>
```

**查询参数**:
- `page`: 页码 (默认: 1)
- `limit`: 每页数量 (默认: 10, 最大: 100)
- `tag`: 标签过滤
- `category`: 分类过滤
- `search`: 关键词搜索
- `sort`: 排序方式 (created_at, updated_at, title)
- `order`: 排序顺序 (asc, desc)

**响应示例**:
```json
{
  "total": 100,
  "page": 1,
  "limit": 10,
  "total_pages": 10,
  "results": [
    {
      "id": "doc_123",
      "title": "文档标题",
      "description": "文档描述",
      "content": "文档内容摘要",
      "tags": ["技术文档"],
      "category": "技术文档",
      "file_info": {
        "filename": "document.pdf",
        "size": 1024000,
        "type": "application/pdf"
      },
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z",
      "user_id": "user_123"
    }
  ]
}
```

#### 获取文档详情
```http
GET /documents/{id}
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "id": "doc_123",
  "title": "文档标题",
  "description": "文档描述",
  "content": "完整文档内容",
  "tags": ["技术文档"],
  "category": "技术文档",
  "file_info": {
    "filename": "document.pdf",
    "size": 1024000,
    "type": "application/pdf",
    "url": "https://storage.example.com/documents/doc_123.pdf"
  },
  "metadata": {
    "pages": 10,
    "language": "zh-CN",
    "keywords": ["关键词1", "关键词2"]
  },
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "user_id": "user_123"
}
```

#### 删除文档
```http
DELETE /documents/{id}
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "message": "文档删除成功"
}
```

### 3. 搜索接口

#### 搜索文档
```http
POST /search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "搜索关键词",
  "tags": ["技术文档"],
  "category": "技术文档",
  "start_date": "2024-01-01",
  "end_date": "2024-12-31",
  "page": 1,
  "limit": 10,
  "sort": "relevance",
  "filters": {
    "file_type": ["pdf", "docx"],
    "size_min": 1000,
    "size_max": 10000000
  }
}
```

**响应示例**:
```json
{
  "total": 50,
  "page": 1,
  "limit": 10,
  "query": "搜索关键词",
  "results": [
    {
      "id": "doc_123",
      "title": "相关文档标题",
      "content": "匹配的内容片段...",
      "score": 0.95,
      "tags": ["技术文档"],
      "category": "技术文档",
      "highlights": [
        {
          "field": "content",
          "snippet": "包含<em>搜索关键词</em>的文本片段"
        }
      ],
      "file_info": {
        "filename": "document.pdf",
        "size": 1024000,
        "type": "application/pdf"
      }
    }
  ],
  "suggestions": ["相关搜索词1", "相关搜索词2"]
}
```

#### 获取搜索历史
```http
GET /search/history?limit=10
Authorization: Bearer <token>
```

**响应示例**:
```json
[
  {
    "id": "search_123",
    "query": "搜索关键词",
    "results_count": 50,
    "timestamp": "2024-01-01T00:00:00Z"
  }
]
```

#### 获取搜索建议
```http
GET /search/suggestions?q=关键词&limit=5
Authorization: Bearer <token>
```

**响应示例**:
```json
[
  "建议搜索词1",
  "建议搜索词2",
  "建议搜索词3"
]
```

### 4. 对话接口

#### 创建对话会话
```http
POST /chat/sessions
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "会话标题",
  "description": "会话描述",
  "settings": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

**响应示例**:
```json
{
  "session_id": "session_123",
  "title": "会话标题",
  "description": "会话描述",
  "created_at": "2024-01-01T00:00:00Z",
  "settings": {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 1000
  }
}
```

#### 获取会话列表
```http
GET /chat/sessions?page=1&limit=10
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "total": 20,
  "page": 1,
  "limit": 10,
  "results": [
    {
      "session_id": "session_123",
      "title": "会话标题",
      "description": "会话描述",
      "message_count": 10,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### 删除对话会话
```http
DELETE /chat/sessions?id=session_123
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "message": "会话删除成功"
}
```

#### 发送消息
```http
POST /chat/messages
Authorization: Bearer <token>
Content-Type: application/json

{
  "session_id": "session_123",
  "content": "用户消息内容",
  "stream": false,
  "context": {
    "documents": ["doc_123", "doc_456"],
    "search_query": "相关搜索"
  }
}
```

**普通响应示例**:
```json
{
  "message_id": "msg_123",
  "session_id": "session_123",
  "role": "assistant",
  "content": "AI回复内容",
  "timestamp": "2024-01-01T00:00:00Z",
  "context": {
    "documents": ["doc_123"],
    "citations": [
      {
        "document_id": "doc_123",
        "title": "相关文档",
        "snippet": "引用的内容片段"
      }
    ]
  }
}
```

**流式响应** (stream=true):
```
data: {"role": "assistant", "content": "你好"}

data: {"role": "assistant", "content": "！我是AI助手"}

data: {"role": "assistant", "content": "，有什么可以帮助你的吗？"}

data: {"context": {"documents": ["doc_123"], "citations": [...]}}

data: [DONE]
```

#### 获取对话历史
```http
GET /chat/history?id=session_123&page=1&limit=20
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "session_id": "session_123",
  "total": 20,
  "page": 1,
  "limit": 20,
  "messages": [
    {
      "id": "msg_123",
      "role": "user",
      "content": "用户消息",
      "timestamp": "2024-01-01T00:00:00Z"
    },
    {
      "id": "msg_124",
      "role": "assistant",
      "content": "AI回复",
      "timestamp": "2024-01-01T00:00:01Z",
      "context": {
        "documents": ["doc_123"],
        "citations": [...]
      }
    }
  ]
}
```

### 5. 缓存与统计接口

#### 缓存预热
```http
POST /api/v1/cache/warmup
Authorization: Bearer <token>
Content-Type: application/json

{
  "cache_items": [
    {"key": "item1", "value": "value1", "ttl": 3600}
  ],
  "search_suggestions": ["建议1", "建议2"],
  "hot_search_terms": ["热门词1", "热门词2"]
}
```

**响应示例**:
```json
{
  "status": "success",
  "message": "缓存预热完成",
  "warmed_items": 10,
  "warmed_suggestions": 5,
  "warmed_terms": 3
}
```

#### 获取统计信息
```http
GET /api/v1/stats
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "cache": {
    "hits": 1000,
    "misses": 50,
    "hit_rate": 0.95,
    "size": 1000,
    "memory_usage": "50MB"
  },
  "documents": {
    "total": 500,
    "by_type": {
      "pdf": 200,
      "docx": 150,
      "txt": 100,
      "other": 50
    },
    "total_size": "2.5GB"
  },
  "users": {
    "total": 100,
    "active_today": 25,
    "active_week": 50
  },
  "search": {
    "total_searches": 1000,
    "avg_results": 15,
    "popular_queries": ["查询1", "查询2", "查询3"]
  },
  "chat": {
    "total_sessions": 200,
    "total_messages": 5000,
    "avg_session_length": 25
  }
}
```

#### 获取预热统计
```http
GET /api/v1/stats/warmup
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "warmup_hits": 500,
  "warmup_misses": 20,
  "total_warmup_time": 30,
  "warmup_efficiency": 0.96
}
```

### 6. 提示词生成与优化接口

#### 生成提示词
```http
POST /prompts/generate
Authorization: Bearer <token>
Content-Type: application/json

{
  "context": {
    "domain": "技术文档",
    "task_type": "问答",
    "requirements": ["准确性", "简洁性"]
  },
  "parameters": {
    "style": "专业",
    "tone": "正式",
    "length": "中等"
  }
}
```

**响应示例**:
```json
{
  "prompt_id": "prompt_123",
  "content": "生成的提示词内容...",
  "metadata": {
    "domain": "技术文档",
    "task_type": "问答",
    "style": "专业"
  },
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 优化提示词
```http
POST /prompts/optimize
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt_content": "原始提示词",
  "optimization_strategy": "enhance_clarity",
  "target_length": "short",
  "style_preferences": {
    "formality": "formal",
    "complexity": "simple"
  }
}
```

**响应示例**:
```json
{
  "original_prompt": "原始提示词",
  "optimized_prompt": "优化后的提示词",
  "improvements": [
    "提高了清晰度",
    "减少了冗余",
    "增强了可读性"
  ],
  "optimization_score": 0.85
}
```

#### 获取提示词历史
```http
GET /prompts/history?page=1&limit=10
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "total": 50,
  "page": 1,
  "limit": 10,
  "results": [
    {
      "id": "prompt_123",
      "type": "generate",
      "content": "生成的提示词内容",
      "context": {
        "domain": "技术文档",
        "task_type": "问答"
      },
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### 保存提示词模板
```http
POST /prompts/templates
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "模板名称",
  "content": "提示词内容",
  "category": "custom",
  "tags": ["标签1", "标签2"]
}
```

**响应示例**:
```json
{
  "template_id": "template_123",
  "name": "模板名称",
  "content": "提示词内容",
  "category": "custom",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 获取提示词模板列表
```http
GET /prompts/templates
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "total": 20,
  "results": [
    {
      "id": "template_123",
      "name": "模板名称",
      "content": "提示词内容",
      "category": "custom",
      "tags": ["标签1", "标签2"],
      "created_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### 删除提示词模板
```http
DELETE /prompts/templates/{template_id}
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "message": "模板删除成功"
}
```

#### 分析提示词
```http
POST /prompts/analyze
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt_content": "要分析的提示词内容"
}
```

**响应示例**:
```json
{
  "clarity": 0.85,
  "completeness": 0.92,
  "executability": 0.78,
  "token_estimate": 150,
  "suggestions": [
    "建议添加更多具体细节",
    "可以考虑简化某些表达"
  ],
  "analysis_score": 0.85
}
```

### 7. 用户设置接口

#### 获取用户设置
```http
GET /user/settings
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "language": "zh-CN",
  "theme": "light",
  "timezone": "Asia/Shanghai",
  "date_format": "YYYY-MM-DD",
  "auto_save": true,
  "show_tutorial": false
}
```

#### 更新用户设置
```http
PUT /user/settings
Authorization: Bearer <token>
Content-Type: application/json

{
  "language": "zh-CN",
  "theme": "dark",
  "timezone": "Asia/Shanghai",
  "date_format": "YYYY-MM-DD",
  "auto_save": true,
  "show_tutorial": false
}
```

**响应示例**:
```json
{
  "message": "设置更新成功"
}
```

#### 获取用户个人信息
```http
GET /user/profile
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "id": "user_123",
  "username": "testuser",
  "nickname": "测试用户",
  "email": "test@example.com",
  "bio": "个人简介",
  "avatar": "https://example.com/avatar.jpg",
  "created_at": "2024-01-01T00:00:00Z",
  "last_login": "2024-01-01T12:00:00Z"
}
```

#### 更新用户个人信息
```http
PUT /user/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "nickname": "新昵称",
  "email": "newemail@example.com",
  "bio": "新的个人简介",
  "avatar": "https://example.com/new-avatar.jpg"
}
```

**响应示例**:
```json
{
  "message": "个人信息更新成功"
}
```

#### 修改密码
```http
POST /user/change-password
Authorization: Bearer <token>
Content-Type: application/json

{
  "old_password": "旧密码",
  "new_password": "新密码"
}
```

**响应示例**:
```json
{
  "message": "密码修改成功"
}
```

#### 获取通知设置
```http
GET /user/notifications
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "email_notifications": true,
  "push_notifications": false,
  "document_upload": true,
  "search_complete": true,
  "chat_message": true,
  "system_updates": false
}
```

#### 更新通知设置
```http
PUT /user/notifications
Authorization: Bearer <token>
Content-Type: application/json

{
  "email_notifications": true,
  "push_notifications": false,
  "document_upload": true,
  "search_complete": true,
  "chat_message": true,
  "system_updates": false
}
```

**响应示例**:
```json
{
  "message": "通知设置更新成功"
}
```

#### 获取API密钥列表
```http
GET /user/api-keys
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "total": 5,
  "results": [
    {
      "id": "key_123",
      "name": "开发环境密钥",
      "key_prefix": "ult_",
      "permissions": ["read", "write"],
      "status": "active",
      "created_at": "2024-01-01T00:00:00Z",
      "last_used": "2024-01-01T12:00:00Z"
    }
  ]
}
```

#### 生成新的API密钥
```http
POST /user/api-keys
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "新密钥名称",
  "permissions": ["read", "write", "delete"]
}
```

**响应示例**:
```json
{
  "id": "key_124",
  "name": "新密钥名称",
  "key": "ult_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "permissions": ["read", "write", "delete"],
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### 删除API密钥
```http
DELETE /user/api-keys/{key_id}
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "message": "API密钥删除成功"
}
```

#### 获取使用统计
```http
GET /user/usage
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "documents": {
    "total": 50,
    "total_size": "2.5GB"
  },
  "chat": {
    "total_sessions": 20,
    "total_messages": 500
  },
  "search": {
    "total_searches": 100
  },
  "api_calls": 1000,
  "storage": {
    "used": "2.5GB",
    "total": "10GB",
    "usage_percent": 25
  },
  "api_quota": {
    "used": 1000,
    "total": 10000,
    "usage_percent": 10
  }
}
```

#### 导出用户数据
```http
GET /user/export
Authorization: Bearer <token>
```

**响应**: 文件下载 (JSON格式)

#### 删除用户账户
```http
POST /user/delete-account
Authorization: Bearer <token>
Content-Type: application/json

{
  "password": "确认密码"
}
```

**响应示例**:
```json
{
  "message": "账户删除成功"
}
```

### 8. 模型搜索接口

#### 搜索HuggingFace模型
```http
GET /api/hf_models?search=bert&pipeline_tag=text-classification&limit=10&page=1
Authorization: Bearer <token>
```

**查询参数**:
- `search`: 搜索关键词
- `pipeline_tag`: 模型类型 (text-classification, text-generation, etc.)
- `limit`: 返回数量 (默认: 10)
- `page`: 页码 (默认: 1)

**响应示例**:
```json
[
  {
    "modelId": "bert-base-chinese",
    "description": "BERT中文预训练模型",
    "downloads": 1000000,
    "pipeline_tag": "text-classification",
    "tags": ["bert", "chinese", "nlp"],
    "author": "huggingface",
    "last_modified": "2024-01-01T00:00:00Z"
  }
]
```

---

## 📊 数据模型

### Document模型
```json
{
  "id": "string",
  "title": "string",
  "description": "string",
  "content": "string",
  "tags": ["string"],
  "category": "string",
  "file_info": {
    "filename": "string",
    "size": "number",
    "type": "string",
    "url": "string"
  },
  "metadata": {
    "pages": "number",
    "language": "string",
    "keywords": ["string"]
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
  "timestamp": "string",
  "context": {
    "documents": ["string"],
    "citations": [
      {
        "document_id": "string",
        "title": "string",
        "snippet": "string"
      }
    ]
  }
}
```

### User模型
```json
{
  "id": "string",
  "username": "string",
  "email": "string",
  "role": "user|admin",
  "created_at": "string",
  "last_login": "string"
}
```

### PromptTemplate模型
```json
{
  "id": "string",
  "name": "string",
  "content": "string",
  "category": "string",
  "tags": ["string"],
  "user_id": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

### ApiKey模型
```json
{
  "id": "string",
  "name": "string",
  "key_prefix": "string",
  "permissions": ["string"],
  "status": "active|inactive",
  "user_id": "string",
  "created_at": "string",
  "last_used": "string"
}
```

---

## 🔧 错误处理

### 错误响应格式
```json
{
  "error": {
    "code": 400,
    "message": "错误描述",
    "details": "详细错误信息",
    "timestamp": "2024-01-01T00:00:00Z",
    "request_id": "req_123"
  }
}
```

### 常见错误码
| 错误码 | 描述 | 解决方案 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查请求参数格式和必填字段 |
| 401 | 未授权 | 提供有效的JWT令牌 |
| 403 | 禁止访问 | 检查用户权限和资源访问权限 |
| 404 | 资源不存在 | 检查资源ID是否正确 |
| 409 | 资源冲突 | 检查资源是否已存在 |
| 413 | 文件过大 | 减小文件大小或使用分块上传 |
| 415 | 不支持的文件类型 | 使用支持的文件格式 |
| 422 | 请求格式正确但语义错误 | 检查业务逻辑约束 |
| 429 | 请求过于频繁 | 降低请求频率或联系管理员 |
| 500 | 服务器内部错误 | 联系系统管理员 |
| 502 | 网关错误 | 检查微服务状态 |
| 503 | 服务不可用 | 等待服务恢复或联系管理员 |

---

## 🚀 使用示例

### JavaScript/TypeScript示例
```javascript
// 配置API客户端
const API_BASE_URL = 'http://localhost:8080/api';

// 登录获取令牌
async function login(username, password) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });
  
  if (!response.ok) {
    throw new Error('登录失败');
  }
  
  const data = await response.json();
  localStorage.setItem('token', data.token);
  return data;
}

// 上传文档
async function uploadDocument(file, metadata) {
  const token = localStorage.getItem('token');
  const formData = new FormData();
  formData.append('file', file);
  formData.append('metadata', JSON.stringify(metadata));
  
  const response = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },
    body: formData
  });
  
  return response.json();
}

// 搜索文档
async function searchDocuments(query, options = {}) {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ query, ...options })
  });
  
  return response.json();
}

// 生成提示词
async function generatePrompt(context, parameters) {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/prompts/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ context, parameters })
  });
  
  return response.json();
}

// 更新用户设置
async function updateUserSettings(settings) {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/user/settings`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(settings)
  });
  
  return response.json();
}

// 发送聊天消息
async function sendMessage(sessionId, content, stream = false) {
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE_URL}/chat/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ session_id: sessionId, content, stream })
  });
  
  if (stream) {
    return response.body.getReader();
  } else {
    return response.json();
  }
}
```

### Python示例
```python
import requests
import json

class UltraRAGClient:
    def __init__(self, base_url='http://localhost:8080/api'):
        self.base_url = base_url
        self.token = None
    
    def login(self, username, password):
        response = requests.post(f'{self.base_url}/auth/login', json={
            'username': username,
            'password': password
        })
        response.raise_for_status()
        data = response.json()
        self.token = data['token']
        return data
    
    def upload_document(self, file_path, metadata):
        if not self.token:
            raise ValueError('请先登录')
        
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'metadata': json.dumps(metadata)}
            headers = {'Authorization': f'Bearer {self.token}'}
            
            response = requests.post(
                f'{self.base_url}/documents/upload',
                files=files,
                data=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    def search_documents(self, query, **options):
        if not self.token:
            raise ValueError('请先登录')
        
        response = requests.post(
            f'{self.base_url}/search',
            json={'query': query, **options},
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response.raise_for_status()
        return response.json()
    
    def generate_prompt(self, context, parameters):
        if not self.token:
            raise ValueError('请先登录')
        
        response = requests.post(
            f'{self.base_url}/prompts/generate',
            json={'context': context, 'parameters': parameters},
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response.raise_for_status()
        return response.json()
    
    def update_user_settings(self, settings):
        if not self.token:
            raise ValueError('请先登录')
        
        response = requests.put(
            f'{self.base_url}/user/settings',
            json=settings,
            headers={'Authorization': f'Bearer {self.token}'}
        )
        response.raise_for_status()
        return response.json()
    
    def send_message(self, session_id, content, stream=False):
        if not self.token:
            raise ValueError('请先登录')
        
        response = requests.post(
            f'{self.base_url}/chat/messages',
            json={'session_id': session_id, 'content': content, 'stream': stream},
            headers={'Authorization': f'Bearer {self.token}'},
            stream=stream
        )
        response.raise_for_status()
        
        if stream:
            return response.iter_lines()
        else:
            return response.json()

# 使用示例
client = UltraRAGClient()
client.login('testuser', 'testpass123')

# 上传文档
result = client.upload_document('document.pdf', {
    'title': '测试文档',
    'tags': ['技术文档']
})
print(f'文档上传成功: {result["document_id"]}')

# 搜索文档
results = client.search_documents('测试关键词')
print(f'找到 {results["total"]} 个结果')

# 生成提示词
prompt = client.generate_prompt(
    context={'domain': '技术文档', 'task_type': '问答'},
    parameters={'style': '专业', 'tone': '正式'}
)
print(f'生成的提示词: {prompt["content"]}')

# 更新设置
client.update_user_settings({'theme': 'dark', 'language': 'zh-CN'})
print('设置更新成功')

# 发送消息
response = client.send_message('session_123', '你好，请介绍一下UltraRAG')
print(f'AI回复: {response["content"]}')
```

---

## 📈 性能优化建议

### 1. 请求优化
- 使用连接池复用HTTP连接
- 启用gzip压缩
- 合理设置超时时间
- 使用批量操作减少请求次数

### 2. 缓存策略
- 缓存认证token
- 缓存搜索结果
- 缓存文档元数据
- 使用ETag进行条件请求

### 3. 文件上传优化
- 使用分块上传大文件
- 压缩文件减少传输时间
- 并行上传多个文件
- 显示上传进度

### 4. 搜索优化
- 使用搜索建议
- 实现搜索历史
- 支持高级搜索语法
- 结果分页和懒加载

---

## 🔒 安全注意事项

### 1. 认证安全
- 使用HTTPS传输
- 定期更新JWT密钥
- 设置合理的token过期时间
- 实现token刷新机制

### 2. 文件安全
- 验证文件类型和大小
- 扫描恶意文件
- 限制文件访问权限
- 定期清理临时文件

### 3. 数据安全
- 加密敏感数据
- 实施访问控制
- 记录操作日志
- 定期备份数据

### 4. API安全
- 实施速率限制
- 验证输入参数
- 防止SQL注入
- 使用CORS保护

---

## 📞 技术支持

### 文档资源
- [API集成指南](./API_Integration_Guide.md)
- [API测试指南](./API_Testing_Guide.md)
- [错误码说明](#错误处理)
- [性能优化指南](../performance/optimization.md)

### 联系方式
- **项目主页**: https://github.com/OpenBMB/BugAgaric
- **问题反馈**: https://github.com/OpenBMB/BugAgaric/issues
- **讨论社区**: https://github.com/OpenBMB/BugAgaric/discussions

### 更新日志
- **v1.0.0**: 初始版本，包含基础API功能
- **v1.1.0**: 添加流式对话和高级搜索功能
- **v1.2.0**: 优化性能和安全性
- **v1.3.0**: 添加提示词生成/优化和用户设置功能 