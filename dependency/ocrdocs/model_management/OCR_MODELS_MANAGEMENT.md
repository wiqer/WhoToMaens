# OCR模型管理功能

## 概述

OCR模型管理功能为MaoOCR系统提供了外部OCR模型的接入能力，支持多种API风格，包括标准OCR API、OpenAI风格、Anthropic风格和自定义API。用户可以通过Web界面轻松添加、管理、测试和唤醒外部OCR模型。

## 功能特性

### 🎯 核心功能
- **模型发现**: 自动发现外部OCR服务中的可用模型
- **多API风格支持**: 支持标准、OpenAI、Anthropic、自定义等多种API风格
- **模型管理**: 添加、编辑、删除、启用/禁用OCR模型
- **连接测试**: 测试OCR模型的连通性和响应性能
- **自动唤醒**: 支持自动唤醒离线状态的OCR模型
- **优先级管理**: 设置模型优先级，实现智能负载均衡

### 🔧 技术特性
- **异步处理**: 支持异步OCR请求处理
- **错误重试**: 自动重试机制，提高系统稳定性
- **速率限制**: 支持API调用频率限制
- **健康检查**: 定期检查模型服务状态
- **性能监控**: 实时监控模型响应时间和成功率

## API风格支持

### 1. 标准OCR API
适用于传统的OCR服务，使用标准的RESTful API格式。

**请求格式:**
```json
{
  "text": "base64编码的图像数据",
  "model": "model-name",
  "language": "zh-cn"
}
```

**响应格式:**
```json
{
  "text": "识别出的文字内容",
  "confidence": 0.95,
  "regions": [...]
}
```

### 2. OpenAI风格
兼容OpenAI GPT-4 Vision等模型的API格式。

**请求格式:**
```json
{
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "请识别这张图片中的文字"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,..."
          }
        }
      ]
    }
  ],
  "max_tokens": 1000
}
```

### 3. Anthropic风格
兼容Anthropic Claude Vision等模型的API格式。

**请求格式:**
```json
{
  "model": "claude-3-vision-20240229",
  "max_tokens": 1000,
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "base64编码的图像数据"
          }
        },
        {
          "type": "text",
          "text": "请识别这张图片中的文字"
        }
      ]
    }
  ]
}
```

### 4. 自定义API
支持完全自定义的API格式，用户可以根据需要配置请求和响应格式。

## Web界面使用

### 访问OCR模型管理页面
1. 启动MaoOCR Web应用
2. 在侧边栏中点击"OCR模型管理"
3. 或直接访问 `/ocr-models` 路径

### 主要操作

#### 1. 发现模型
1. 点击"发现模型"按钮
2. 输入外部OCR服务的基础URL
3. 选择API风格
4. 点击"发现模型"开始扫描
5. 查看发现的模型列表并选择要添加的模型

#### 2. 添加模型
1. 点击"添加模型"按钮
2. 填写模型配置信息：
   - **模型名称**: 用于标识模型的唯一名称
   - **API风格**: 选择对应的API风格
   - **基础URL**: OCR服务的基础地址
   - **模型ID**: 具体的模型标识符
   - **API密钥**: 如果需要认证的密钥
   - **超时时间**: 请求超时时间（秒）
   - **最大重试次数**: 失败重试次数
   - **速率限制**: 每分钟最大请求数
   - **优先级**: 模型优先级（数字越小优先级越高）
   - **启用模型**: 是否启用该模型
   - **自动唤醒**: 是否支持自动唤醒功能

#### 3. 测试模型
1. 在模型列表中找到要测试的模型
2. 点击"测试连接"按钮
3. 系统会发送测试请求验证模型连通性
4. 查看测试结果和响应时间

#### 4. 唤醒模型
1. 在模型列表中找到要唤醒的模型
2. 点击"唤醒模型"按钮
3. 系统会尝试唤醒离线状态的模型
4. 查看唤醒结果和模型状态

#### 5. 编辑模型
1. 在模型列表中找到要编辑的模型
2. 点击"编辑"按钮
3. 修改模型配置参数
4. 保存更改

#### 6. 删除模型
1. 在模型列表中找到要删除的模型
2. 点击"删除"按钮
3. 确认删除操作

## 后端API接口

### 1. 获取外部OCR模型列表
```http
GET /api/ocr/models/external
```

**响应:**
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "name": "model-name",
        "base_url": "https://api.example.com",
        "model": "model-id",
        "status": "active",
        "priority": 1,
        "api_style": "standard",
        "auto_wake": true,
        "last_used": "2024-01-01T12:00:00Z"
      }
    ]
  }
}
```

### 2. 发现OCR模型
```http
POST /api/ocr/models/external/discover
```

**请求体:**
```json
{
  "base_url": "https://api.example.com",
  "api_style": "standard"
}
```

**响应:**
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "id": "model-id",
        "name": "Model Name",
        "type": "ocr",
        "description": "Model description"
      }
    ]
  }
}
```

### 3. 添加外部OCR模型
```http
POST /api/ocr/models/external/add
```

**请求体:**
```json
{
  "name": "model-name",
  "base_url": "https://api.example.com",
  "model": "model-id",
  "api_style": "standard",
  "api_key": "optional-api-key",
  "timeout": 30,
  "max_retries": 3,
  "rate_limit": 60,
  "priority": 1,
  "enabled": true,
  "auto_wake": false
}
```

### 4. 测试外部OCR模型
```http
POST /api/ocr/models/external/test
```

**请求体:**
```json
{
  "name": "model-name",
  "base_url": "https://api.example.com",
  "model": "model-id",
  "api_style": "standard"
}
```

### 5. 唤醒外部OCR模型
```http
POST /api/ocr/models/external/wake
```

**请求体:**
```json
{
  "name": "model-name",
  "base_url": "https://api.example.com"
}
```

## 配置示例

### 标准OCR API配置
```yaml
apis:
  standard-ocr:
    type: ocr_api
    base_url: "https://ocr.example.com"
    model: "standard-v1"
    api_style: "standard"
    timeout: 30
    max_retries: 3
    rate_limit: 60
    priority: 1
    enabled: true
    auto_wake: true
```

### OpenAI风格配置
```yaml
apis:
  gpt4-vision:
    type: ocr_api
    base_url: "https://api.openai.com"
    model: "gpt-4-vision-preview"
    api_style: "openai"
    api_key: "sk-..."
    timeout: 60
    max_retries: 3
    rate_limit: 10
    priority: 2
    enabled: true
    auto_wake: false
```

### Anthropic风格配置
```yaml
apis:
  claude-vision:
    type: ocr_api
    base_url: "https://api.anthropic.com"
    model: "claude-3-vision-20240229"
    api_style: "anthropic"
    api_key: "sk-ant-..."
    timeout: 60
    max_retries: 3
    rate_limit: 5
    priority: 3
    enabled: true
    auto_wake: false
```

### 自定义API配置
```yaml
apis:
  custom-ocr:
    type: ocr_api
    base_url: "https://ocr.company.com"
    model: "custom-engine"
    api_style: "custom"
    timeout: 45
    max_retries: 2
    rate_limit: 100
    priority: 1
    enabled: true
    auto_wake: true
    headers:
      X-API-Version: "v2"
      X-Client-ID: "maoocr"
    extra_params:
      language: "zh-cn"
      confidence_threshold: 0.8
```

## 使用场景

### 1. 多模型负载均衡
通过配置多个OCR模型并设置不同的优先级，可以实现智能负载均衡：
- 高优先级模型用于重要任务
- 低优先级模型用于备份和降级处理

### 2. 模型服务发现
在企业环境中，可以自动发现和注册新的OCR服务：
- 支持动态服务发现
- 自动健康检查
- 服务状态监控

### 3. 混合云部署
支持同时使用本地和云端OCR服务：
- 本地模型用于敏感数据处理
- 云端模型用于大规模处理
- 自动故障转移

### 4. 成本优化
通过合理配置模型优先级和速率限制，可以优化OCR服务成本：
- 优先使用成本较低的模型
- 限制高成本模型的调用频率
- 根据业务需求动态调整

## 故障排除

### 常见问题

#### 1. 模型连接失败
**症状**: 测试连接时显示连接失败
**解决方案**:
- 检查基础URL是否正确
- 确认网络连接正常
- 验证API密钥是否有效
- 检查防火墙设置

#### 2. 模型发现失败
**症状**: 无法发现外部OCR模型
**解决方案**:
- 确认API风格选择正确
- 检查服务端点是否可访问
- 验证服务是否支持模型发现接口
- 查看服务日志获取详细错误信息

#### 3. 模型唤醒失败
**症状**: 自动唤醒功能不工作
**解决方案**:
- 确认模型支持唤醒功能
- 检查唤醒端点是否正确
- 验证唤醒权限是否足够
- 查看服务状态和日志

#### 4. 性能问题
**症状**: 模型响应时间过长或成功率低
**解决方案**:
- 调整超时时间设置
- 增加重试次数
- 检查网络延迟
- 优化模型配置参数

### 调试技巧

1. **查看日志**: 检查系统日志获取详细错误信息
2. **网络诊断**: 使用ping、telnet等工具测试网络连通性
3. **API测试**: 使用curl或Postman直接测试API接口
4. **性能监控**: 查看模型响应时间和成功率统计

## 最佳实践

### 1. 模型配置
- 为每个模型设置合适的超时时间和重试次数
- 根据模型性能设置合理的速率限制
- 配置适当的优先级实现负载均衡

### 2. 安全考虑
- 使用HTTPS协议保护API通信
- 妥善保管API密钥，避免泄露
- 定期轮换API密钥
- 监控异常访问行为

### 3. 监控和维护
- 定期检查模型健康状态
- 监控模型性能和成功率
- 及时更新模型配置
- 备份重要配置信息

### 4. 扩展性
- 设计可扩展的模型架构
- 支持动态添加和移除模型
- 实现自动服务发现
- 准备故障转移方案

## 总结

OCR模型管理功能为MaoOCR系统提供了强大的外部模型接入能力，支持多种API风格和丰富的管理功能。通过Web界面，用户可以轻松管理外部OCR模型，实现智能负载均衡和故障转移，提高系统的可靠性和性能。

该功能特别适用于需要集成多个OCR服务的场景，如企业级文档处理、多语言识别、混合云部署等。通过合理的配置和管理，可以显著提升OCR系统的整体性能和用户体验。