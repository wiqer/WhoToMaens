# MaoOCR API 参考文档

## 📋 概述

本文档详细描述了MaoOCR项目的所有API接口，包括OCR识别、文档处理、监控管理、外部API集成等功能。MaoOCR提供了RESTful API和WebSocket接口，支持多种文档格式的处理和智能OCR识别。

## 🚀 快速开始

### 基础信息
- **服务地址**: `http://localhost:8000`
- **API文档**: `http://localhost:8000/docs`
- **健康检查**: `http://localhost:8000/health`
- **版本**: 1.0.0

### 认证方式
目前API采用无认证方式，生产环境建议配置API密钥认证。

### 响应格式
所有API响应都采用统一的JSON格式：
```json
{
  "success": true,
  "data": {
    // 具体数据
  },
  "error": null
}
```

## 🔧 核心API

### 1. 基础服务API

#### 根路径
```http
GET /
```

**响应示例**:
```json
{
  "message": "MaoOCR API服务",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs"
}
```

#### 健康检查
```http
GET /health
```

**响应示例**:
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "services": {
    "maoocr": true,
    "resource_monitor": true,
    "vllm_manager": true
  },
  "resources": {
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "gpu_usage": 23.1
  }
}
```

#### 服务状态
```http
GET /api/status
```

**响应示例**:
```json
{
  "status": "running",
  "uptime": 3600,
  "version": "1.0.0",
  "services": {
    "ocr": "active",
    "document_processing": "active",
    "monitoring": "active"
  }
}
```

### 2. OCR识别API

#### 基础文本识别
```http
POST /api/ocr/recognize
Content-Type: multipart/form-data
```

**参数**:
- `image` (file): 要识别的图片文件

**响应示例**:
```json
{
  "success": true,
  "data": {
    "text": "识别的文本内容",
    "confidence": 0.95,
    "processing_time": 1.23,
    "language": "zh-CN"
  }
}
```

#### 带需求的文本识别
```http
POST /api/ocr/recognize-with-requirements
Content-Type: multipart/form-data
```

**参数**:
- `image` (file): 要识别的图片文件
- `requirements` (string): 识别需求描述

**响应示例**:
```json
{
  "success": true,
  "data": {
    "text": "识别的文本内容",
    "confidence": 0.95,
    "processing_time": 1.23,
    "language": "zh-CN",
    "requirements_met": true,
    "enhancements": ["格式优化", "语义纠错"]
  }
}
```

#### 批量识别
```http
POST /api/ocr/batch-recognize
Content-Type: multipart/form-data
```

**参数**:
- `images` (files): 多个图片文件
- `requirements` (string): 识别需求描述

**响应示例**:
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_12345",
    "total_images": 5,
    "processed_images": 5,
    "results": [
      {
        "index": 0,
        "text": "第一张图片的文本",
        "confidence": 0.92
      },
      {
        "index": 1,
        "text": "第二张图片的文本",
        "confidence": 0.88
      }
    ]
  }
}
```

#### 异步批量识别
```http
POST /api/ocr/batch-recognize-async
Content-Type: multipart/form-data
```

**参数**:
- `images` (files): 多个图片文件
- `requirements` (string): 识别需求描述

**响应示例**:
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_12345",
    "status": "processing",
    "total_images": 5,
    "estimated_time": 25.5
  }
}
```

#### 获取批量处理状态
```http
GET /api/ocr/batch-status/{batch_id}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_12345",
    "status": "completed",
    "progress": 100,
    "processed_images": 5,
    "total_images": 5,
    "estimated_remaining_time": 0
  }
}
```

#### 获取批量处理结果
```http
GET /api/ocr/batch-results/{batch_id}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "batch_id": "batch_12345",
    "status": "completed",
    "results": [
      {
        "index": 0,
        "text": "第一张图片的文本",
        "confidence": 0.92,
        "processing_time": 1.2
      }
    ]
  }
}
```

#### 获取可用模型
```http
GET /api/ocr/models
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "models": [
      {
        "name": "cnocr",
        "version": "2.2.2",
        "languages": ["zh-CN", "en"],
        "accuracy": 0.95
      },
      {
        "name": "monkey_ocr",
        "version": "1.0.0",
        "languages": ["zh-CN"],
        "accuracy": 0.93
      }
    ]
  }
}
```

#### 获取性能统计
```http
GET /api/ocr/performance
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_requests": 1250,
    "successful_requests": 1200,
    "failed_requests": 50,
    "average_response_time": 1.23,
    "requests_per_minute": 15.6,
    "accuracy_rate": 0.96
  }
}
```

#### PP-OCRv5 + OpenVINO 专用识别
```http
POST /api/ocr/pp-ocrv5-recognize
Content-Type: multipart/form-data
```

**参数**:
- `image` (file): 要识别的图片文件
- `device` (string, optional): 推理设备 (CPU/GPU/MYRIAD)，默认CPU
- `batch_size` (integer, optional): 批处理大小，默认8
- `enable_async` (boolean, optional): 是否启用异步推理，默认true

**响应示例**:
```json
{
  "success": true,
  "data": {
    "text": "识别的文本内容",
    "confidence": 0.95,
    "processing_time": 0.45,
    "language": "zh-CN",
    "engine": "pp_ocrv5_openvino",
    "device": "CPU",
    "inference_time": 0.23,
    "model_load_time": 0.12
  }
}
```

#### PP-OCRv5 批量识别
```http
POST /api/ocr/pp-ocrv5-batch-recognize
Content-Type: multipart/form-data
```

**参数**:
- `images` (files): 多个图片文件
- `device` (string, optional): 推理设备，默认CPU
- `max_batch_size` (integer, optional): 最大批处理大小，默认8
- `enable_dynamic_batch` (boolean, optional): 启用动态批处理，默认true

**响应示例**:
```json
{
  "success": true,
  "data": {
    "batch_id": "pp_ocrv5_batch_12345",
    "total_images": 10,
    "processed_images": 10,
    "average_inference_time": 0.28,
    "device_utilization": 85.5,
    "results": [
      {
        "index": 0,
        "text": "第一张图片的文本",
        "confidence": 0.94,
        "inference_time": 0.25
      }
    ]
  }
}
```

#### 获取PP-OCRv5引擎状态
```http
GET /api/ocr/pp-ocrv5-status
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "engine_status": "active",
    "model_loaded": true,
    "device": "CPU",
    "num_streams": 4,
    "cache_hit_rate": 78.5,
    "device_usage": 65.2,
    "stream_utilization": 82.1,
    "model_info": {
      "name": "PP-OCRv5",
      "version": "5.0",
      "optimization": "OpenVINO",
      "quantization": "FP16"
    }
  }
}
```

#### 获取OpenVINO设备信息
```http
GET /api/ocr/openvino-devices
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "available_devices": [
      {
        "name": "CPU",
        "type": "CPU",
        "capabilities": ["FP32", "FP16", "INT8"],
        "memory": "16GB",
        "utilization": 45.2
      },
      {
        "name": "GPU.0",
        "type": "GPU",
        "capabilities": ["FP32", "FP16"],
        "memory": "8GB",
        "utilization": 23.1
      }
    ],
    "current_device": "CPU",
    "recommended_device": "CPU"
  }
}
```

#### 切换OpenVINO设备
```http
POST /api/ocr/openvino-switch-device
Content-Type: application/json
```

**请求体**:
```json
{
  "device": "GPU.0",
  "num_streams": 2,
  "enable_async": true
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "previous_device": "CPU",
    "current_device": "GPU.0",
    "switch_time": 2.34,
    "status": "switched"
  }
}
```

#### 获取引擎性能对比
```http
GET /api/ocr/engine-comparison
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "engines": [
      {
        "name": "pp_ocrv5_openvino",
        "average_speed": 0.28,
        "accuracy": 0.94,
        "memory_usage": 512,
        "device": "CPU",
        "status": "active"
      },
      {
        "name": "cnocr",
        "average_speed": 1.23,
        "accuracy": 0.92,
        "memory_usage": 1024,
        "device": "GPU",
        "status": "active"
      }
    ],
    "recommendation": "pp_ocrv5_openvino"
  }
}
```

### 3. 文档处理API

#### 文件上传
```http
POST /api/upload
Content-Type: multipart/form-data
```

**参数**:
- `file` (file): 要上传的文件

**响应示例**:
```json
{
  "id": "file_12345",
  "filename": "document.pdf",
  "url": "/api/files/file_12345",
  "size": 1024000
}
```

#### 分片上传初始化
```http
POST /api/upload/init
Content-Type: application/json
```

**请求体**:
```json
{
  "fileId": "file_12345",
  "filename": "large_document.pdf",
  "fileSize": 52428800,
  "totalChunks": 10,
  "chunkSize": 5242880
}
```

**响应示例**:
```json
{
  "fileId": "file_12345",
  "status": "initialized"
}
```

#### 分片上传
```http
POST /api/upload/chunk
Content-Type: multipart/form-data
```

**参数**:
- `file_id` (string): 文件ID
- `chunk_index` (integer): 分片索引
- `chunk` (file): 分片文件

**响应示例**:
```json
{
  "chunkIndex": 0,
  "status": "uploaded"
}
```

#### 完成分片上传
```http
POST /api/upload/complete
Content-Type: application/json
```

**请求体**:
```json
{
  "fileId": "file_12345"
}
```

**响应示例**:
```json
{
  "id": "file_12345",
  "filename": "large_document.pdf",
  "url": "/api/files/file_12345",
  "size": 52428800
}
```

#### 获取文件
```http
GET /api/files/{file_id}
```

**响应**: 文件内容

#### 处理文档
```http
POST /api/process-document
Content-Type: application/json
```

**请求体**:
```json
{
  "fileId": "file_12345",
  "fileName": "document.pdf",
  "fileType": "pdf",
  "settings": {
    "output_format": "markdown",
    "include_images": true,
    "preserve_layout": true
  }
}
```

**响应示例**:
```json
{
  "id": "result_12345",
  "originalFile": "document.pdf",
  "outputFile": "document.md",
  "contentLength": 2048,
  "settings": {
    "output_format": "markdown",
    "include_images": true,
    "preserve_layout": true
  }
}
```

#### 下载处理结果
```http
GET /api/download/{result_id}
```

**响应**: 处理后的文件内容

### 4. 监控系统API

#### 获取监控面板数据
```http
GET /api/monitoring/dashboard?time_range=60
```

**参数**:
- `time_range` (integer): 时间范围（分钟），默认60

**响应示例**:
```json
{
  "success": true,
  "data": {
    "system_metrics": {
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "gpu_usage": 23.1,
      "disk_usage": 78.5
    },
    "performance_metrics": {
      "requests_per_minute": 15.6,
      "average_response_time": 1.23,
      "error_rate": 0.02
    },
    "cache_metrics": {
      "hit_rate": 0.85,
      "cache_size": 1024000
    }
  }
}
```

#### 获取实时指标
```http
GET /api/monitoring/realtime
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "timestamp": 1703123456.789,
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "gpu_usage": 23.1,
    "active_requests": 5,
    "queue_size": 2
  }
}
```

#### 导出监控数据
```http
GET /api/monitoring/export?format=json
```

**参数**:
- `format` (string): 导出格式，支持json

**响应**: 监控数据文件

### 5. 日志管理API

#### 获取日志
```http
GET /api/logs?level=ERROR&limit=100&hours=24
```

**参数**:
- `level` (string): 日志级别（DEBUG, INFO, WARNING, ERROR, CRITICAL）
- `logger_name` (string): 日志器名称
- `limit` (integer): 返回条数限制，默认100
- `hours` (integer): 时间范围（小时），默认24

**响应示例**:
```json
{
  "success": true,
  "data": {
    "logs": [
      {
        "timestamp": "2024-01-01T12:00:00",
        "level": "ERROR",
        "logger": "maoocr.ocr",
        "message": "OCR识别失败",
        "details": "图片格式不支持"
      }
    ],
    "total": 50
  }
}
```

#### 获取日志统计
```http
GET /api/logs/statistics?hours=24
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_logs": 1250,
    "by_level": {
      "DEBUG": 200,
      "INFO": 800,
      "WARNING": 150,
      "ERROR": 80,
      "CRITICAL": 20
    },
    "by_logger": {
      "maoocr.ocr": 500,
      "maoocr.document": 400,
      "maoocr.monitoring": 350
    }
  }
}
```

#### 获取错误分析
```http
GET /api/logs/errors?hours=24
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "error_patterns": [
      {
        "pattern": "OCR recognition failed",
        "count": 25,
        "percentage": 31.25
      },
      {
        "pattern": "File not found",
        "count": 15,
        "percentage": 18.75
      }
    ],
    "error_trend": [
      {
        "hour": "12:00",
        "count": 5
      },
      {
        "hour": "13:00",
        "count": 8
      }
    ]
  }
}
```

#### 搜索日志
```http
GET /api/logs/search?query=OCR&case_sensitive=false
```

**参数**:
- `query` (string): 搜索关键词
- `case_sensitive` (boolean): 是否区分大小写，默认false

**响应示例**:
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "timestamp": "2024-01-01T12:00:00",
        "level": "INFO",
        "logger": "maoocr.ocr",
        "message": "OCR识别成功",
        "highlight": "OCR识别成功"
      }
    ],
    "total": 15
  }
}
```

#### 导出日志
```http
GET /api/logs/export?format=json&hours=24
```

**参数**:
- `format` (string): 导出格式，支持json
- `hours` (integer): 时间范围（小时），默认24

**响应**: 日志数据文件

### 6. 告警系统API

#### 获取活跃告警
```http
GET /api/alerts
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "active_alerts": [
      {
        "rule_name": "high_cpu_usage",
        "level": "WARNING",
        "message": "CPU使用率过高",
        "timestamp": "2024-01-01T12:00:00",
        "value": 85.2,
        "threshold": 80.0
      }
    ],
    "total": 3
  }
}
```

#### 获取告警历史
```http
GET /api/alerts/history?hours=24
```

**参数**:
- `hours` (integer): 时间范围（小时），默认24

**响应示例**:
```json
{
  "success": true,
  "data": {
    "alert_history": [
      {
        "rule_name": "high_cpu_usage",
        "level": "WARNING",
        "message": "CPU使用率过高",
        "timestamp": "2024-01-01T12:00:00",
        "resolved_at": "2024-01-01T12:05:00",
        "duration": 300
      }
    ],
    "total": 10
  }
}
```

#### 获取告警统计
```http
GET /api/alerts/statistics?hours=24
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_alerts": 25,
    "by_level": {
      "INFO": 5,
      "WARNING": 15,
      "ERROR": 3,
      "CRITICAL": 2
    },
    "by_rule": {
      "high_cpu_usage": 10,
      "high_memory_usage": 8,
      "high_error_rate": 7
    },
    "average_resolution_time": 180
  }
}
```

#### 确认告警
```http
POST /api/alerts/{rule_name}/acknowledge?user=admin
```

**参数**:
- `rule_name` (string): 告警规则名称
- `user` (string): 确认用户

**响应示例**:
```json
{
  "success": true,
  "data": {
    "rule_name": "high_cpu_usage",
    "acknowledged_by": "admin",
    "acknowledged_at": "2024-01-01T12:00:00"
  }
}
```

#### 解决告警
```http
POST /api/alerts/{rule_name}/resolve
```

**参数**:
- `rule_name` (string): 告警规则名称

**响应示例**:
```json
{
  "success": true,
  "data": {
    "rule_name": "high_cpu_usage",
    "resolved_at": "2024-01-01T12:05:00"
  }
}
```

### 7. 健康检查API

#### 获取健康状态
```http
GET /api/health
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "overall_status": "HEALTHY",
    "checks": {
      "system_resources": {
        "status": "HEALTHY",
        "message": "系统资源正常",
        "last_check": "2024-01-01T12:00:00"
      },
      "cache_system": {
        "status": "HEALTHY",
        "message": "缓存系统正常",
        "last_check": "2024-01-01T12:00:00"
      },
      "model_services": {
        "status": "HEALTHY",
        "message": "模型服务正常",
        "last_check": "2024-01-01T12:00:00"
      }
    }
  }
}
```

#### 获取特定检查结果
```http
GET /api/health/{check_name}
```

**参数**:
- `check_name` (string): 检查项名称

**响应示例**:
```json
{
  "success": true,
  "data": {
    "check_name": "system_resources",
    "status": "HEALTHY",
    "message": "系统资源正常",
    "details": {
      "cpu_usage": 45.2,
      "memory_usage": 67.8,
      "disk_usage": 78.5
    },
    "last_check": "2024-01-01T12:00:00"
  }
}
```

#### 立即运行检查
```http
POST /api/health/{check_name}/run
```

**参数**:
- `check_name` (string): 检查项名称

**响应示例**:
```json
{
  "success": true,
  "data": {
    "check_name": "system_resources",
    "status": "HEALTHY",
    "message": "系统资源正常",
    "execution_time": 0.5
  }
}
```

## 🔌 WebSocket API

### WebSocket连接
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/ocr');
```

### 消息格式

#### OCR识别请求
```json
{
  "type": "ocr_request",
  "data": {
    "image": "base64_encoded_image",
    "requirements": "识别需求描述"
  }
}
```

#### 批量OCR请求
```json
{
  "type": "batch_ocr_request",
  "data": {
    "images": ["base64_image_1", "base64_image_2"],
    "requirements": "识别需求描述"
  }
}
```

#### 响应消息
```json
{
  "type": "ocr_response",
  "data": {
    "text": "识别的文本",
    "confidence": 0.95,
    "processing_time": 1.23
  }
}
```

#### 进度更新
```json
{
  "type": "progress_update",
  "data": {
    "batch_id": "batch_12345",
    "progress": 60,
    "processed": 3,
    "total": 5
  }
}
```

## 🔗 外部API集成

### API管理器配置

#### 获取API统计
```http
GET /api/external/stats
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_requests": 1250,
    "api_stats": {
      "openai_api": {
        "total_requests": 500,
        "successful_requests": 480,
        "failed_requests": 20,
        "avg_response_time": 1.2,
        "success_rate": 0.96
      },
      "anthropic_api": {
        "total_requests": 750,
        "successful_requests": 720,
        "failed_requests": 30,
        "avg_response_time": 1.5,
        "success_rate": 0.96
      }
    }
  }
}
```

#### 列出API配置
```http
GET /api/external/apis
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "apis": [
      {
        "name": "openai_api",
        "type": "openai",
        "base_url": "https://api.openai.com/v1",
        "model": "gpt-3.5-turbo",
        "enabled": true,
        "priority": 1,
        "rate_limit": 60
      },
      {
        "name": "anthropic_api",
        "type": "anthropic",
        "base_url": "https://api.anthropic.com",
        "model": "claude-3-sonnet",
        "enabled": true,
        "priority": 2,
        "rate_limit": 50
      }
    ]
  }
}
```

## 📊 错误码说明

### HTTP状态码
- `200`: 请求成功
- `400`: 请求参数错误
- `401`: 未授权
- `403`: 禁止访问
- `404`: 资源不存在
- `500`: 服务器内部错误

### 业务错误码
```json
{
  "success": false,
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "不支持的文件类型",
    "details": "仅支持PDF、EPUB、DOCX、MD格式"
  }
}
```

常见错误码：
- `INVALID_FILE_TYPE`: 不支持的文件类型
- `FILE_TOO_LARGE`: 文件过大
- `OCR_FAILED`: OCR识别失败
- `PROCESSING_TIMEOUT`: 处理超时
- `INSUFFICIENT_RESOURCES`: 资源不足
- `API_RATE_LIMIT`: API调用频率限制

## 🚀 使用示例

### Python客户端示例

```python
import requests
import json

# 基础OCR识别
def recognize_text(image_path):
    url = "http://localhost:8000/api/ocr/recognize"
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(url, files=files)
    return response.json()

# 文档处理
def process_document(file_path):
    # 1. 上传文件
    upload_url = "http://localhost:8000/api/upload"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        upload_response = requests.post(upload_url, files=files)
    file_info = upload_response.json()
    
    # 2. 处理文档
    process_url = "http://localhost:8000/api/process-document"
    process_data = {
        "fileId": file_info['id'],
        "fileName": file_info['filename'],
        "fileType": "pdf",
        "settings": {
            "output_format": "markdown",
            "include_images": True
        }
    }
    process_response = requests.post(process_url, json=process_data)
    return process_response.json()

# 获取监控数据
def get_monitoring_data():
    url = "http://localhost:8000/api/monitoring/dashboard"
    response = requests.get(url)
    return response.json()
```

### JavaScript客户端示例

```javascript
// 基础OCR识别
async function recognizeText(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch('http://localhost:8000/api/ocr/recognize', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}

// WebSocket连接
function connectWebSocket() {
    const ws = new WebSocket('ws://localhost:8000/ws/ocr');
    
    ws.onopen = function() {
        console.log('WebSocket连接已建立');
    };
    
    ws.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('收到消息:', data);
    };
    
    ws.onclose = function() {
        console.log('WebSocket连接已关闭');
    };
    
    return ws;
}

// 发送OCR请求
function sendOCRRequest(ws, imageBase64) {
    const request = {
        type: 'ocr_request',
        data: {
            image: imageBase64,
            requirements: '识别文本内容'
        }
    };
    
    ws.send(JSON.stringify(request));
}
```

### cURL示例

```bash
# 健康检查
curl -X GET http://localhost:8000/health

# OCR识别
curl -X POST http://localhost:8000/api/ocr/recognize \
  -F "image=@/path/to/image.jpg"

# 文档处理
curl -X POST http://localhost:8000/api/upload \
  -F "file=@/path/to/document.pdf"

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

# 获取监控数据
curl -X GET "http://localhost:8000/api/monitoring/dashboard?time_range=60"

# 获取日志
curl -X GET "http://localhost:8000/api/logs?level=ERROR&limit=100"
```

## 🔧 配置说明

### 环境变量
```bash
# 服务配置
MAOOCR_HOST=0.0.0.0
MAOOCR_PORT=8000
MAOOCR_DEBUG=false

# 文件上传配置
MAOOCR_UPLOAD_FOLDER=uploads
MAOOCR_MAX_FILE_SIZE=524288000

# 监控配置
MAOOCR_MONITORING_ENABLED=true
MAOOCR_LOG_LEVEL=INFO

# 外部API配置
MAOOCR_EXTERNAL_API_CONFIG=configs/external_apis.yaml
```

### 配置文件
主要配置文件位于 `configs/` 目录：
- `maoocr_config.yaml`: 主配置
- `external_apis.yaml`: 外部API配置
- `monitoring_config.yaml`: 监控配置
- `performance_config.yaml`: 性能配置

## 📚 相关文档

- [技术架构文档](./technical-architecture.md)
- [配置说明文档](./configuration.md)
- [监控系统文档](./MONITORING_SYSTEM.md)
- [性能优化文档](./PERFORMANCE_OPTIMIZATION.md)
- [WebSocket协议文档](./websocket_protocol.md)
- [前后端集成文档](./frontend_backend_integration.md)

---

*文档版本: 1.0.0*
*最后更新时间: 2024年12月*