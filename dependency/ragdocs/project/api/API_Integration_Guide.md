# BugAgaric API 集成指南

## 📋 概述

本文档详细说明了UltraRAG项目中前后端API的对接情况，包括已实现的接口、待实现的接口以及集成建议。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                                │
├─────────────────────────────────────────────────────────────┤
│  Streamlit UI (端口: 8843)  │  React前端 (端口: 3000)        │
│  • 数据构建                 │  • 用户界面                    │
│  • 模型训练                 │  • 文档管理                    │
│  • 效果评测                 │  • 搜索功能                    │
│  • 推理体验                 │  • 对话系统                    │
│                             │  • 提示词工具                  │
│                             │  • 设置管理                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        API网关层                             │
├─────────────────────────────────────────────────────────────┤
│  Go API服务 (端口: 8080)    │  Python微服务                  │
│  • 认证服务                 │  • LLM服务 (端口: 8000)        │
│  • 文档管理                 │  • Embedding服务 (端口: 8001)  │
│  • 搜索服务                 │  • Reranker服务 (端口: 8002)   │
│  • 对话服务                 │  • 缓存服务 (端口: 8003)       │
│  • 提示词服务               │                                │
│  • 用户设置服务             │                                │
└─────────────────────────────────────────────────────────────┘
```

## 📊 API实现状态对照表

### 🔐 认证相关API

| API接口 | 方法 | 路径 | 前端页面 | 实现状态 | 集成状态 |
|---------|------|------|----------|----------|----------|
| 用户登录 | POST | `/auth/login` | Login.jsx | ✅ 已实现 | ✅ 已集成 |
| 用户注册 | POST | `/auth/register` | Register.jsx | ✅ 已实现 | ✅ 已集成 |
| 用户登出 | POST | `/auth/logout` | 全局 | ✅ 已实现 | ✅ 已集成 |

**实现详情**:
- **后端**: Go服务中的`handlers/auth.go`
- **认证方式**: JWT Token
- **前端集成**: 已实现token存储和自动刷新

### 📄 文档管理API

| API接口 | 方法 | 路径 | 前端页面 | 实现状态 | 集成状态 |
|---------|------|------|----------|----------|----------|
| 上传文档 | POST | `/documents/upload` | Documents.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取文档列表 | GET | `/documents` | Documents.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取文档详情 | GET | `/documents/{id}` | Documents.jsx | ✅ 已实现 | ✅ 已集成 |
| 删除文档 | DELETE | `/documents/{id}` | Documents.jsx | ✅ 已实现 | ✅ 已集成 |

**实现详情**:
- **后端**: Go服务中的`handlers/document.go`
- **文件存储**: MinIO对象存储
- **数据库**: PostgreSQL
- **前端集成**: 已实现文件上传进度和错误处理

### 🔍 搜索相关API

| API接口 | 方法 | 路径 | 前端页面 | 实现状态 | 集成状态 |
|---------|------|------|----------|----------|----------|
| 搜索文档 | POST | `/search` | Search.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取搜索历史 | GET | `/search/history` | Search.jsx | ✅ 已实现 | ✅ 已集成 |
| 搜索建议 | GET | `/search/suggestions` | Search.jsx | ✅ 已实现 | ✅ 已集成 |

**实现详情**:
- **后端**: Go服务中的`handlers/search.go`
- **向量搜索**: Milvus向量数据库
- **缓存**: Redis缓存热门搜索
- **前端集成**: 已实现搜索建议和结果高亮

### 💬 对话相关API

| API接口 | 方法 | 路径 | 前端页面 | 实现状态 | 集成状态 |
|---------|------|------|----------|----------|----------|
| 创建会话 | POST | `/chat/sessions` | Chat.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取会话列表 | GET | `/chat/sessions` | Chat.jsx | ✅ 已实现 | ✅ 已集成 |
| 删除会话 | DELETE | `/chat/sessions` | Chat.jsx | ✅ 已实现 | ✅ 已集成 |
| 发送消息 | POST | `/chat/messages` | Chat.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取对话历史 | GET | `/chat/history` | Chat.jsx | ✅ 已实现 | ✅ 已集成 |

**实现详情**:
- **后端**: Go服务中的`handlers/chat.go`
- **LLM服务**: Python微服务 (端口: 8000)
- **流式响应**: 支持Server-Sent Events
- **前端集成**: 已实现流式消息显示和会话管理

### 📊 统计与缓存API

| API接口 | 方法 | 路径 | 前端页面 | 实现状态 | 集成状态 |
|---------|------|------|----------|----------|----------|
| 获取统计信息 | GET | `/api/v1/stats` | Stats.jsx | ✅ 已实现 | ✅ 已集成 |
| 缓存预热 | POST | `/api/v1/cache/warmup` | Stats.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取预热统计 | GET | `/api/v1/stats/warmup` | Stats.jsx | ✅ 已实现 | ✅ 已集成 |

**实现详情**:
- **后端**: Go服务中的`handlers/stats.go`
- **缓存服务**: 独立的缓存微服务
- **监控**: 实时统计和性能监控
- **前端集成**: 已实现实时数据更新

### 🎯 提示词生成/优化API

| API接口 | 方法 | 路径 | 前端页面 | 实现状态 | 集成状态 |
|---------|------|------|----------|----------|----------|
| 生成提示词 | POST | `/prompts/generate` | Prompts.jsx | ✅ 已实现 | ✅ 已集成 |
| 优化提示词 | POST | `/prompts/optimize` | Prompts.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取提示词历史 | GET | `/prompts/history` | Prompts.jsx | ✅ 已实现 | ✅ 已集成 |
| 保存提示词模板 | POST | `/prompts/templates` | Prompts.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取提示词模板 | GET | `/prompts/templates` | Prompts.jsx | ✅ 已实现 | ✅ 已集成 |
| 删除提示词模板 | DELETE | `/prompts/templates/{id}` | Prompts.jsx | ✅ 已实现 | ✅ 已集成 |
| 分析提示词 | POST | `/prompts/analyze` | Prompts.jsx | ✅ 已实现 | ✅ 已集成 |

**实现详情**:
- **后端**: Go服务中的`handlers/prompts.go`
- **AI模型**: 集成LLM进行提示词生成和优化
- **模板管理**: 支持自定义模板保存和管理
- **前端集成**: 已实现完整的提示词工具界面

### ⚙️ 用户设置API

| API接口 | 方法 | 路径 | 前端页面 | 实现状态 | 集成状态 |
|---------|------|------|----------|----------|----------|
| 获取用户设置 | GET | `/user/settings` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 更新用户设置 | PUT | `/user/settings` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取用户信息 | GET | `/user/profile` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 更新用户信息 | PUT | `/user/profile` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 修改密码 | POST | `/user/change-password` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取通知设置 | GET | `/user/notifications` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 更新通知设置 | PUT | `/user/notifications` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取API密钥 | GET | `/user/api-keys` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 生成API密钥 | POST | `/user/api-keys` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 删除API密钥 | DELETE | `/user/api-keys/{id}` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 获取使用统计 | GET | `/user/usage` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 导出用户数据 | GET | `/user/export` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |
| 删除用户账户 | POST | `/user/delete-account` | Settings.jsx | ✅ 已实现 | ✅ 已集成 |

**实现详情**:
- **后端**: Go服务中的`handlers/user.go`
- **数据存储**: PostgreSQL用户数据
- **安全机制**: 密码加密、API密钥管理
- **前端集成**: 已实现完整的设置管理界面

### 🤖 模型服务API

| API接口 | 方法 | 路径 | 前端页面 | 实现状态 | 集成状态 |
|---------|------|------|----------|----------|----------|
| LLM聊天 | POST | `/chat` | Chat.jsx | ✅ 已实现 | 🟡 部分集成 |
| 生成嵌入 | POST | `/embed` | 后台服务 | ✅ 已实现 | 🟡 部分集成 |
| 重排序 | POST | `/rerank` | 后台服务 | ✅ 已实现 | 🟡 部分集成 |

**实现详情**:
- **LLM服务**: `bugagaric/server/run_server_hf_llm.py`
- **Embedding服务**: `bugagaric/server/run_embedding.py`
- **Reranker服务**: `bugagaric/server/run_server_reranker.py`
- **前端集成**: Streamlit UI已部分集成，React前端待集成

## 🔧 集成实现指南

### 1. 前端API客户端配置

```javascript
// src/utils/api.js
import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:8080/api',
  timeout: 30000,
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器 - 处理错误
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，跳转到登录页
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;
```

### 2. 认证服务集成

```javascript
// src/services/auth.js
import api from '../utils/api';

export const authService = {
  // 用户登录
  async login(username, password) {
    const response = await api.post('/auth/login', { username, password });
    const { token } = response.data;
    localStorage.setItem('token', token);
    return response.data;
  },

  // 用户注册
  async register(username, password, email) {
    const response = await api.post('/auth/register', { username, password, email });
    return response.data;
  },

  // 用户登出
  async logout() {
    try {
      await api.post('/auth/logout');
    } finally {
      localStorage.removeItem('token');
    }
  },

  // 检查登录状态
  isAuthenticated() {
    return !!localStorage.getItem('token');
  }
};
```

### 3. 文档管理服务集成

```javascript
// src/services/documents.js
import api from '../utils/api';

export const documentService = {
  // 上传文档
  async uploadDocument(file, metadata) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));
    
    const response = await api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        const percentCompleted = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        // 更新上传进度
        console.log(`上传进度: ${percentCompleted}%`);
      }
    });
    return response.data;
  },

  // 获取文档列表
  async getDocuments(params = {}) {
    const response = await api.get('/documents', { params });
    return response.data;
  },

  // 获取文档详情
  async getDocument(id) {
    const response = await api.get(`/documents/${id}`);
    return response.data;
  },

  // 删除文档
  async deleteDocument(id) {
    const response = await api.delete(`/documents/${id}`);
    return response.data;
  }
};
```

### 4. 搜索服务集成

```javascript
// src/services/search.js
import api from '../utils/api';

export const searchService = {
  // 搜索文档
  async searchDocuments(query, options = {}) {
    const response = await api.post('/search', {
      query,
      page: options.page || 1,
      limit: options.limit || 10,
      tags: options.tags || [],
      start_date: options.startDate,
      end_date: options.endDate
    });
    return response.data;
  },

  // 获取搜索历史
  async getSearchHistory(limit = 10) {
    const response = await api.get('/search/history', { params: { limit } });
    return response.data;
  },

  // 获取搜索建议
  async getSearchSuggestions(query, limit = 5) {
    const response = await api.get('/search/suggestions', { 
      params: { q: query, limit } 
    });
    return response.data;
  }
};
```

### 5. 对话服务集成

```javascript
// src/services/chat.js
import api from '../utils/api';

export const chatService = {
  // 创建会话
  async createSession(title) {
    const response = await api.post('/chat/sessions', { title });
    return response.data;
  },

  // 获取会话列表
  async getSessions() {
    const response = await api.get('/chat/sessions');
    return response.data;
  },

  // 删除会话
  async deleteSession(sessionId) {
    const response = await api.delete('/chat/sessions', { 
      params: { id: sessionId } 
    });
    return response.data;
  },

  // 发送消息
  async sendMessage(sessionId, content, stream = false) {
    if (stream) {
      // 流式响应
      const response = await fetch(`${api.defaults.baseURL}/chat/messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ session_id: sessionId, content, stream: true })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      
      return {
        async *[Symbol.asyncIterator]() {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') return;
                try {
                  yield JSON.parse(data);
                } catch (e) {
                  // 忽略解析错误
                }
              }
            }
          }
        }
      };
    } else {
      // 普通响应
      const response = await api.post('/chat/messages', {
        session_id: sessionId,
        content,
        stream: false
      });
      return response.data;
    }
  },

  // 获取对话历史
  async getHistory(sessionId) {
    const response = await api.get('/chat/history', { 
      params: { id: sessionId } 
    });
    return response.data;
  }
};
```

### 6. 提示词服务集成

```javascript
// src/services/prompts.js
import api from '../utils/api';

export const promptsService = {
  // 生成提示词
  async generatePrompt(context, parameters = {}) {
    const response = await api.post('/prompts/generate', {
      context,
      parameters
    });
    return response.data;
  },

  // 优化提示词
  async optimizePrompt(promptContent, optimizationStrategy, options = {}) {
    const response = await api.post('/prompts/optimize', {
      prompt_content: promptContent,
      optimization_strategy: optimizationStrategy,
      target_length: options.targetLength || 'medium',
      style_preferences: options.stylePreferences || {}
    });
    return response.data;
  },

  // 获取提示词历史
  async getPromptHistory(page = 1, limit = 10) {
    const response = await api.get('/prompts/history', {
      params: { page, limit }
    });
    return response.data;
  },

  // 保存提示词模板
  async savePromptTemplate(template) {
    const response = await api.post('/prompts/templates', template);
    return response.data;
  },

  // 获取提示词模板列表
  async getPromptTemplates() {
    const response = await api.get('/prompts/templates');
    return response.data;
  },

  // 删除提示词模板
  async deletePromptTemplate(templateId) {
    const response = await api.delete(`/prompts/templates/${templateId}`);
    return response.data;
  },

  // 分析提示词
  async analyzePrompt(promptContent) {
    const response = await api.post('/prompts/analyze', {
      prompt_content: promptContent
    });
    return response.data;
  }
};
```

### 7. 设置服务集成

```javascript
// src/services/settings.js
import api from '../utils/api';

export const settingsService = {
  // 获取用户设置
  async getUserSettings() {
    const response = await api.get('/user/settings');
    return response.data;
  },

  // 更新用户设置
  async updateUserSettings(settings) {
    const response = await api.put('/user/settings', settings);
    return response.data;
  },

  // 获取用户个人信息
  async getUserProfile() {
    const response = await api.get('/user/profile');
    return response.data;
  },

  // 更新用户个人信息
  async updateUserProfile(profile) {
    const response = await api.put('/user/profile', profile);
    return response.data;
  },

  // 修改密码
  async changePassword(oldPassword, newPassword) {
    const response = await api.post('/user/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    });
    return response.data;
  },

  // 获取通知设置
  async getNotificationSettings() {
    const response = await api.get('/user/notifications');
    return response.data;
  },

  // 更新通知设置
  async updateNotificationSettings(settings) {
    const response = await api.put('/user/notifications', settings);
    return response.data;
  },

  // 获取API密钥
  async getApiKeys() {
    const response = await api.get('/user/api-keys');
    return response.data;
  },

  // 生成新的API密钥
  async generateApiKey(name, permissions = []) {
    const response = await api.post('/user/api-keys', {
      name,
      permissions
    });
    return response.data;
  },

  // 删除API密钥
  async deleteApiKey(keyId) {
    const response = await api.delete(`/user/api-keys/${keyId}`);
    return response.data;
  },

  // 获取使用统计
  async getUsageStats() {
    const response = await api.get('/user/usage');
    return response.data;
  },

  // 导出用户数据
  async exportUserData() {
    const response = await api.get('/user/export', {
      responseType: 'blob'
    });
    return response.data;
  },

  // 删除用户账户
  async deleteAccount(password) {
    const response = await api.post('/user/delete-account', {
      password
    });
    return response.data;
  }
};
```

## 🚀 集成优先级建议

### 高优先级 (核心功能) ✅ 已完成
1. **认证系统** - 实现登录注册和token管理
2. **文档管理** - 实现文档上传、列表、详情、删除
3. **搜索功能** - 实现文档搜索和搜索历史
4. **对话系统** - 实现会话管理和消息发送

### 中优先级 (增强功能) ✅ 已完成
5. **统计信息** - 实现系统统计和监控
6. **缓存管理** - 实现缓存预热和统计
7. **提示词工具** - 实现提示词生成、优化、模板管理
8. **用户设置** - 实现个人信息、系统设置、API密钥管理

### 低优先级 (优化功能) 🔄 进行中
9. **性能优化** - 实现懒加载和缓存策略
10. **用户体验** - 实现错误处理和加载状态
11. **高级功能** - 实现批量操作和高级搜索
12. **模型搜索** - 实现HuggingFace模型搜索

## 🔍 测试建议

### 1. API测试
```bash
# 使用curl测试API
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'

# 使用Postman或Insomnia进行API测试
```

### 2. 前端集成测试
```javascript
// 在React组件中测试API集成
import { useEffect, useState } from 'react';
import { documentService } from '../services/documents';

function DocumentList() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const data = await documentService.getDocuments();
        setDocuments(data.results);
      } catch (error) {
        console.error('加载文档失败:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDocuments();
  }, []);

  // 渲染文档列表
}
```

### 3. 提示词功能测试
```javascript
// 测试提示词生成
import { promptsService } from '../services/prompts';

async function testPromptGeneration() {
  try {
    const result = await promptsService.generatePrompt(
      { domain: '技术文档', task_type: '问答' },
      { style: '专业', tone: '正式' }
    );
    console.log('生成的提示词:', result.content);
  } catch (error) {
    console.error('生成提示词失败:', error);
  }
}
```

### 4. 设置功能测试
```javascript
// 测试用户设置
import { settingsService } from '../services/settings';

async function testUserSettings() {
  try {
    const settings = await settingsService.getUserSettings();
    console.log('用户设置:', settings);
    
    await settingsService.updateUserSettings({ theme: 'dark' });
    console.log('设置更新成功');
  } catch (error) {
    console.error('设置操作失败:', error);
  }
}
```

## 📝 注意事项

1. **错误处理**: 所有API调用都应该包含适当的错误处理
2. **加载状态**: 为用户提供清晰的加载反馈
3. **数据验证**: 前端和后端都要进行数据验证
4. **安全性**: 确保敏感数据的安全传输和存储
5. **性能**: 合理使用缓存和分页加载
6. **用户体验**: 提供友好的错误提示和操作反馈

## 🔗 相关文档

- [API接口文档](./README.md)
- [前端开发指南](../frontend/README.md)
- [后端开发指南](../backend/README.md)
- [部署指南](../deployment/installation.md) 