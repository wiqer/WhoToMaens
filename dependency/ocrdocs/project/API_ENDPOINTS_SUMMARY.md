# MaoOCR API 端点汇总表

## 📋 概述

本文档提供了MaoOCR项目中所有API端点的快速参考，按功能分类组织，方便开发者快速查找和使用。

## 🔧 基础服务API

| 端点 | 方法 | 描述 | 参数 | 响应 |
|------|------|------|------|------|
| `/` | GET | 根路径 | 无 | 服务信息 |
| `/health` | GET | 健康检查 | 无 | 健康状态 |
| `/api/status` | GET | 服务状态 | 无 | 运行状态 |

## 🔍 OCR识别API

| 端点 | 方法 | 描述 | 参数 | 响应 |
|------|------|------|------|------|
| `/api/ocr/recognize` | POST | 基础文本识别 | `image` (file) | 识别结果 |
| `/api/ocr/recognize-with-requirements` | POST | 带需求的文本识别 | `image` (file), `requirements` (string) | 识别结果 |
| `/api/ocr/batch-recognize` | POST | 批量识别 | `images` (files), `requirements` (string) | 批量结果 |
| `/api/ocr/batch-recognize-async` | POST | 异步批量识别 | `images` (files), `requirements` (string) | 任务ID |
| `/api/ocr/batch-status/{batch_id}` | GET | 获取批量处理状态 | `batch_id` (path) | 处理状态 |
| `/api/ocr/batch-results/{batch_id}` | GET | 获取批量处理结果 | `batch_id` (path) | 处理结果 |
| `/api/ocr/models` | GET | 获取可用模型 | 无 | 模型列表 |
| `/api/ocr/performance` | GET | 获取性能统计 | 无 | 性能数据 |
| `/api/ocr/pp-ocrv5-recognize` | POST | PP-OCRv5专用识别 | `image` (file), `device`, `batch_size`, `enable_async` | 识别结果 |
| `/api/ocr/pp-ocrv5-batch-recognize` | POST | PP-OCRv5批量识别 | `images` (files), `device`, `max_batch_size`, `enable_dynamic_batch` | 批量结果 |
| `/api/ocr/pp-ocrv5-status` | GET | 获取PP-OCRv5引擎状态 | 无 | 引擎状态 |
| `/api/ocr/openvino-devices` | GET | 获取OpenVINO设备信息 | 无 | 设备列表 |
| `/api/ocr/openvino-switch-device` | POST | 切换OpenVINO设备 | JSON body | 切换结果 |
| `/api/ocr/engine-comparison` | GET | 获取引擎性能对比 | 无 | 性能对比 |

## 📄 文档处理API

| 端点 | 方法 | 描述 | 参数 | 响应 |
|------|------|------|------|------|
| `/api/upload` | POST | 文件上传 | `file` (file) | 文件信息 |
| `/api/upload/init` | POST | 分片上传初始化 | JSON body | 初始化结果 |
| `/api/upload/chunk` | POST | 分片上传 | `file_id`, `chunk_index`, `chunk` | 上传状态 |
| `/api/upload/complete` | POST | 完成分片上传 | `fileId` (JSON) | 文件信息 |
| `/api/files/{file_id}` | GET | 获取文件 | `file_id` (path) | 文件内容 |
| `/api/process-document` | POST | 处理文档 | JSON body | 处理结果 |
| `/api/download/{result_id}` | GET | 下载处理结果 | `result_id` (path) | 文件内容 |

## 📊 监控系统API

| 端点 | 方法 | 描述 | 参数 | 响应 |
|------|------|------|------|------|
| `/api/monitoring/dashboard` | GET | 获取监控面板数据 | `time_range` (query) | 监控数据 |
| `/api/monitoring/realtime` | GET | 获取实时指标 | 无 | 实时数据 |
| `/api/monitoring/export` | GET | 导出监控数据 | `format` (query) | 数据文件 |

## 📝 日志管理API

| 端点 | 方法 | 描述 | 参数 | 响应 |
|------|------|------|------|------|
| `/api/logs` | GET | 获取日志 | `level`, `logger_name`, `limit`, `hours` | 日志列表 |
| `/api/logs/statistics` | GET | 获取日志统计 | `hours` (query) | 统计信息 |
| `/api/logs/errors` | GET | 获取错误分析 | `hours` (query) | 错误分析 |
| `/api/logs/search` | GET | 搜索日志 | `query`, `case_sensitive` | 搜索结果 |
| `/api/logs/export` | GET | 导出日志 | `format`, `hours` | 日志文件 |

## 🚨 告警系统API

| 端点 | 方法 | 描述 | 参数 | 响应 |
|------|------|------|------|------|
| `/api/alerts` | GET | 获取活跃告警 | 无 | 告警列表 |
| `/api/alerts/history` | GET | 获取告警历史 | `hours` (query) | 历史记录 |
| `/api/alerts/statistics` | GET | 获取告警统计 | `hours` (query) | 统计信息 |
| `/api/alerts/{rule_name}/acknowledge` | POST | 确认告警 | `rule_name` (path), `user` (query) | 确认结果 |
| `/api/alerts/{rule_name}/resolve` | POST | 解决告警 | `rule_name` (path) | 解决结果 |

## 💚 健康检查API

| 端点 | 方法 | 描述 | 参数 | 响应 |
|------|------|------|------|------|
| `/api/health` | GET | 获取健康状态 | 无 | 健康状态 |
| `/api/health/{check_name}` | GET | 获取特定检查结果 | `check_name` (path) | 检查结果 |
| `/api/health/{check_name}/run` | POST | 立即运行检查 | `check_name` (path) | 执行结果 |

## 🔌 WebSocket API

| 端点 | 方法 | 描述 | 参数 | 响应 |
|------|------|------|------|------|
| `/ws/ocr` | WebSocket | OCR WebSocket接口 | 连接参数 | 实时消息 |

## 🔗 外部API集成

| 端点 | 方法 | 描述 | 参数 | 响应 |
|------|------|------|------|------|
| `/api/external/stats` | GET | 获取API统计 | 无 | 统计信息 |
| `/api/external/apis` | GET | 列出API配置 | 无 | API列表 |

## 📋 请求参数说明

### 通用查询参数
- `limit`: 返回条数限制（默认100）
- `hours`: 时间范围（小时，默认24）
- `time_range`: 时间范围（分钟，默认60）

### 文件上传参数
- `file`: 文件对象
- `file_id`: 文件唯一标识
- `chunk_index`: 分片索引
- `chunk`: 分片文件

### 文档处理参数
```json
{
  "fileId": "文件ID",
  "fileName": "文件名",
  "fileType": "文件类型",
  "settings": {
    "output_format": "输出格式",
    "include_images": "是否包含图片",
    "preserve_layout": "是否保持布局"
  }
}
```

### OCR识别参数
- `image`: 图片文件
- `requirements`: 识别需求描述
- `images`: 多个图片文件

## 📊 响应格式

### 成功响应
```json
{
  "success": true,
  "data": {
    // 具体数据
  },
  "error": null
}
```

### 错误响应
```json
{
  "success": false,
  "error": {
    "code": "错误码",
    "message": "错误消息",
    "details": "详细信息"
  }
}
```

## 🔧 使用示例

### 基础OCR识别
```bash
curl -X POST http://localhost:8000/api/ocr/recognize \
  -F "image=@/path/to/image.jpg"
```

### 文档处理
```bash
# 1. 上传文件
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/document.pdf"

# 2. 处理文档
curl -X POST http://localhost:8000/api/process-document \
  -H "Content-Type: application/json" \
  -d '{
    "fileId": "file_12345",
    "fileName": "document.pdf",
    "fileType": "pdf",
    "settings": {
      "output_format": "markdown"
    }
  }'
```

### 获取监控数据
```bash
curl -X GET "http://localhost:8000/api/monitoring/dashboard?time_range=60"
```

### WebSocket连接
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ocr');
ws.onmessage = function(event) {
    console.log('收到消息:', JSON.parse(event.data));
};
```

## 📚 相关文档

- [完整API参考文档](API_REFERENCE.md) - 详细的API文档和使用示例
- [技术架构文档](technical-architecture.md) - 系统架构设计
- [配置说明文档](configuration.md) - 配置文件说明
- [WebSocket协议文档](websocket_protocol.md) - WebSocket详细协议

---

*文档版本: 1.0.0*
*最后更新时间: 2024年12月*