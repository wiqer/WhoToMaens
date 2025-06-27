# MaoOCR WebSocket通信协议

## 📋 概述

本文档详细说明MaoOCR系统中WebSocket通信的协议规范，包括消息格式、事件类型、错误处理等。

## 🔗 连接信息

### 连接地址
```
ws://localhost:8000/ws/ocr
```

### 连接参数
- **协议**: WebSocket
- **编码**: UTF-8
- **心跳间隔**: 30秒
- **重连策略**: 指数退避

## 📨 消息格式

### 基础消息结构
所有WebSocket消息都遵循以下JSON格式：

```json
{
  "type": "消息类型",
  "data": {},
  "timestamp": 1704067200.0,
  "id": "消息ID（可选）"
}
```

### 字段说明
- **type**: 消息类型，字符串
- **data**: 消息数据，对象
- **timestamp**: 时间戳，Unix时间戳（秒）
- **id**: 消息ID，用于请求-响应匹配（可选）

## 🔄 消息类型

### 1. OCR识别请求

#### 客户端 → 服务器
```json
{
  "type": "ocr_request",
  "data": {
    "image": "base64_encoded_image",
    "requirements": {
      "document_type": "auto",
      "language": "auto",
      "accuracy_requirement": "high",
      "speed_requirement": "medium",
      "real_time": false,
      "batch_processing": false
    }
  },
  "timestamp": 1704067200.0,
  "id": "req_001"
}
```

#### 字段说明
- **image**: Base64编码的图片数据
- **requirements**: OCR识别需求参数
  - **document_type**: 文档类型（auto/document/receipt/id_card/business_card）
  - **language**: 语言（auto/chinese/english/mixed）
  - **accuracy_requirement**: 精度要求（high/medium/low）
  - **speed_requirement**: 速度要求（fast/medium/slow）
  - **real_time**: 是否实时处理
  - **batch_processing**: 是否批量处理

### 2. 识别开始

#### 服务器 → 客户端
```json
{
  "type": "ocr_start",
  "data": {
    "request_id": "req_001",
    "estimated_time": 5.0
  },
  "timestamp": 1704067200.0
}
```

#### 字段说明
- **request_id**: 对应的请求ID
- **estimated_time**: 预估处理时间（秒）

### 3. 识别进度

#### 服务器 → 客户端
```json
{
  "type": "ocr_progress",
  "data": {
    "request_id": "req_001",
    "progress": 50,
    "stage": "recognition",
    "message": "正在识别文本..."
  },
  "timestamp": 1704067200.0
}
```

#### 字段说明
- **request_id**: 对应的请求ID
- **progress**: 进度百分比（0-100）
- **stage**: 当前阶段（preprocessing/detection/recognition/postprocessing）
- **message**: 进度描述

### 4. 识别完成

#### 服务器 → 客户端
```json
{
  "type": "ocr_complete",
  "data": {
    "request_id": "req_001",
    "result": {
      "text": "识别出的文本内容",
      "confidence": 0.95,
      "processing_time": 1.23,
      "selected_models": ["cnocr", "monkey_ocr"],
      "strategy": "fusion",
      "language": "chinese",
      "document_type": "mixed_language",
      "regions": [
        {
          "bbox": [10, 20, 100, 50],
          "text": "区域文本",
          "confidence": 0.9
        }
      ]
    }
  },
  "timestamp": 1704067200.0
}
```

#### 字段说明
- **request_id**: 对应的请求ID
- **result**: 识别结果
  - **text**: 完整识别文本
  - **confidence**: 整体置信度
  - **processing_time**: 处理时间（秒）
  - **selected_models**: 使用的模型列表
  - **strategy**: 使用的策略
  - **language**: 检测到的语言
  - **document_type**: 检测到的文档类型
  - **regions**: 文本区域信息

### 5. 识别错误

#### 服务器 → 客户端
```json
{
  "type": "ocr_error",
  "data": {
    "request_id": "req_001",
    "error_code": "IMAGE_TOO_LARGE",
    "error_message": "图片尺寸过大",
    "details": "图片尺寸超过最大限制 10MB"
  },
  "timestamp": 1704067200.0
}
```

#### 字段说明
- **request_id**: 对应的请求ID
- **error_code**: 错误代码
- **error_message**: 错误消息
- **details**: 错误详情

### 6. 心跳检测

#### 客户端 → 服务器
```json
{
  "type": "ping",
  "data": {},
  "timestamp": 1704067200.0
}
```

#### 服务器 → 客户端
```json
{
  "type": "pong",
  "data": {
    "server_time": 1704067200.0,
    "uptime": 3600.0
  },
  "timestamp": 1704067200.0
}
```

### 7. 连接状态

#### 服务器 → 客户端
```json
{
  "type": "connection_status",
  "data": {
    "status": "connected",
    "client_id": "client_001",
    "server_info": {
      "version": "1.0.0",
      "uptime": 3600.0,
      "active_connections": 5
    }
  },
  "timestamp": 1704067200.0
}
```

## 🚨 错误处理

### 错误代码列表

| 错误代码 | 描述 | 解决方案 |
|----------|------|----------|
| `INVALID_IMAGE` | 无效的图片格式 | 检查图片格式是否支持 |
| `IMAGE_TOO_LARGE` | 图片尺寸过大 | 压缩图片或使用较小的图片 |
| `IMAGE_TOO_SMALL` | 图片尺寸过小 | 使用分辨率更高的图片 |
| `NO_TEXT_DETECTED` | 未检测到文本 | 检查图片是否包含清晰文本 |
| `MODEL_LOAD_ERROR` | 模型加载失败 | 检查模型文件是否完整 |
| `PROCESSING_TIMEOUT` | 处理超时 | 稍后重试或使用较小的图片 |
| `SERVER_ERROR` | 服务器内部错误 | 联系技术支持 |
| `RATE_LIMIT_EXCEEDED` | 请求频率过高 | 降低请求频率 |

### 错误响应格式
```json
{
  "type": "error",
  "data": {
    "error_code": "ERROR_CODE",
    "error_message": "错误描述",
    "details": "详细错误信息",
    "suggestions": ["建议1", "建议2"]
  },
  "timestamp": 1704067200.0
}
```

## 🔄 连接管理

### 连接建立
1. 客户端发起WebSocket连接
2. 服务器验证连接并返回连接状态
3. 客户端发送认证信息（如需要）
4. 服务器确认认证并开始心跳检测

### 心跳机制
- **心跳间隔**: 30秒
- **超时时间**: 90秒
- **重试次数**: 3次
- **重连策略**: 指数退避（1s, 2s, 4s, 8s...）

### 断线重连
```javascript
// 客户端重连示例
class WebSocketClient {
  constructor(url) {
    this.url = url;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
  }

  connect() {
    this.ws = new WebSocket(this.url);
    this.ws.onopen = () => {
      console.log('WebSocket连接已建立');
      this.reconnectAttempts = 0;
      this.startHeartbeat();
    };

    this.ws.onclose = () => {
      console.log('WebSocket连接已断开');
      this.reconnect();
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket错误:', error);
    };
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      setTimeout(() => {
        console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, delay);
    }
  }

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({
          type: 'ping',
          data: {},
          timestamp: Date.now() / 1000
        }));
      }
    }, 30000);
  }
}
```

## 📱 客户端实现示例

### Flutter WebSocket客户端
```dart
import 'dart:convert';
import 'dart:io';
import 'package:web_socket_channel/web_socket_channel.dart';

class MaoOCRWebSocket {
  WebSocketChannel? _channel;
  String _url = 'ws://localhost:8000/ws/ocr';
  bool _isConnected = false;
  int _reconnectAttempts = 0;
  static const int maxReconnectAttempts = 5;

  Future<void> connect() async {
    try {
      _channel = WebSocketChannel.connect(Uri.parse(_url));
      _isConnected = true;
      _reconnectAttempts = 0;
      
      _channel!.stream.listen(
        (message) => _handleMessage(message),
        onError: (error) => _handleError(error),
        onDone: () => _handleDisconnect(),
      );
      
      // 开始心跳
      _startHeartbeat();
      
    } catch (e) {
      _handleError(e);
    }
  }

  Future<void> sendOCRRequest(String imageBase64, Map<String, dynamic> requirements) async {
    if (!_isConnected) {
      throw Exception('WebSocket未连接');
    }

    final message = {
      'type': 'ocr_request',
      'data': {
        'image': imageBase64,
        'requirements': requirements,
      },
      'timestamp': DateTime.now().millisecondsSinceEpoch / 1000,
      'id': 'req_${DateTime.now().millisecondsSinceEpoch}',
    };

    _channel!.sink.add(jsonEncode(message));
  }

  void _handleMessage(dynamic message) {
    try {
      final data = jsonDecode(message);
      final type = data['type'];
      
      switch (type) {
        case 'ocr_start':
          _onOCRStart(data['data']);
          break;
        case 'ocr_progress':
          _onOCRProgress(data['data']);
          break;
        case 'ocr_complete':
          _onOCRComplete(data['data']);
          break;
        case 'ocr_error':
          _onOCRError(data['data']);
          break;
        case 'pong':
          _onPong(data['data']);
          break;
        default:
          print('未知消息类型: $type');
      }
    } catch (e) {
      print('消息处理错误: $e');
    }
  }

  void _startHeartbeat() {
    Timer.periodic(Duration(seconds: 30), (timer) {
      if (_isConnected) {
        final pingMessage = {
          'type': 'ping',
          'data': {},
          'timestamp': DateTime.now().millisecondsSinceEpoch / 1000,
        };
        _channel!.sink.add(jsonEncode(pingMessage));
      } else {
        timer.cancel();
      }
    });
  }

  void _handleError(dynamic error) {
    print('WebSocket错误: $error');
    _isConnected = false;
    _reconnect();
  }

  void _handleDisconnect() {
    print('WebSocket连接断开');
    _isConnected = false;
    _reconnect();
  }

  void _reconnect() {
    if (_reconnectAttempts < maxReconnectAttempts) {
      _reconnectAttempts++;
      final delay = Duration(seconds: pow(2, _reconnectAttempts - 1).toInt());
      
      Timer(delay, () {
        print('尝试重连 (${_reconnectAttempts}/$maxReconnectAttempts)');
        connect();
      });
    }
  }

  // 回调函数
  void Function(Map<String, dynamic>)? onOCRStart;
  void Function(Map<String, dynamic>)? onOCRProgress;
  void Function(Map<String, dynamic>)? onOCRComplete;
  void Function(Map<String, dynamic>)? onOCRError;
  void Function(Map<String, dynamic>)? onPong;

  void _onOCRStart(Map<String, dynamic> data) {
    onOCRStart?.call(data);
  }

  void _onOCRProgress(Map<String, dynamic> data) {
    onOCRProgress?.call(data);
  }

  void _onOCRComplete(Map<String, dynamic> data) {
    onOCRComplete?.call(data);
  }

  void _onOCRError(Map<String, dynamic> data) {
    onOCRError?.call(data);
  }

  void _onPong(Map<String, dynamic> data) {
    onPong?.call(data);
  }

  void disconnect() {
    _isConnected = false;
    _channel?.sink.close();
  }
}
```

### React WebSocket客户端
```javascript
class MaoOCRWebSocket {
  constructor(url = 'ws://localhost:8000/ws/ocr') {
    this.url = url;
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.heartbeatInterval = null;
    this.messageHandlers = new Map();
  }

  connect() {
    try {
      this.ws = new WebSocket(this.url);
      
      this.ws.onopen = () => {
        console.log('WebSocket连接已建立');
        this.isConnected = true;
        this.reconnectAttempts = 0;
        this.startHeartbeat();
      };

      this.ws.onmessage = (event) => {
        this.handleMessage(event.data);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket错误:', error);
        this.handleError(error);
      };

      this.ws.onclose = () => {
        console.log('WebSocket连接已断开');
        this.handleDisconnect();
      };

    } catch (error) {
      this.handleError(error);
    }
  }

  sendOCRRequest(imageBase64, requirements = {}) {
    if (!this.isConnected) {
      throw new Error('WebSocket未连接');
    }

    const message = {
      type: 'ocr_request',
      data: {
        image: imageBase64,
        requirements: requirements,
      },
      timestamp: Date.now() / 1000,
      id: `req_${Date.now()}`,
    };

    this.ws.send(JSON.stringify(message));
  }

  handleMessage(data) {
    try {
      const message = JSON.parse(data);
      const { type, data: messageData } = message;

      // 调用对应的处理器
      const handler = this.messageHandlers.get(type);
      if (handler) {
        handler(messageData);
      } else {
        console.warn('未知消息类型:', type);
      }

    } catch (error) {
      console.error('消息处理错误:', error);
    }
  }

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected) {
        const pingMessage = {
          type: 'ping',
          data: {},
          timestamp: Date.now() / 1000,
        };
        this.ws.send(JSON.stringify(pingMessage));
      }
    }, 30000);
  }

  handleError(error) {
    console.error('WebSocket错误:', error);
    this.isConnected = false;
    this.reconnect();
  }

  handleDisconnect() {
    console.log('WebSocket连接断开');
    this.isConnected = false;
    this.reconnect();
  }

  reconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.pow(2, this.reconnectAttempts - 1) * 1000;
      
      setTimeout(() => {
        console.log(`尝试重连 (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.connect();
      }, delay);
    }
  }

  // 注册消息处理器
  on(event, handler) {
    this.messageHandlers.set(event, handler);
  }

  // 移除消息处理器
  off(event) {
    this.messageHandlers.delete(event);
  }

  disconnect() {
    this.isConnected = false;
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }
    if (this.ws) {
      this.ws.close();
    }
  }
}

// 使用示例
const wsClient = new MaoOCRWebSocket();

wsClient.on('ocr_start', (data) => {
  console.log('OCR开始:', data);
  // 更新UI显示开始状态
});

wsClient.on('ocr_progress', (data) => {
  console.log('OCR进度:', data);
  // 更新进度条
});

wsClient.on('ocr_complete', (data) => {
  console.log('OCR完成:', data);
  // 显示识别结果
});

wsClient.on('ocr_error', (data) => {
  console.error('OCR错误:', data);
  // 显示错误信息
});

// 连接WebSocket
wsClient.connect();

// 发送OCR请求
const imageBase64 = 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...';
const requirements = {
  document_type: 'auto',
  language: 'auto',
  accuracy_requirement: 'high',
};

wsClient.sendOCRRequest(imageBase64, requirements);
```

## 🔒 安全考虑

### 1. 认证机制
- 支持JWT Token认证
- 支持API Key认证
- 支持OAuth2认证

### 2. 数据加密
- 支持WSS（WebSocket Secure）
- 支持消息加密
- 支持图片数据加密

### 3. 访问控制
- 连接频率限制
- 消息大小限制
- 并发连接数限制

## 📊 性能优化

### 1. 消息压缩
- 支持GZIP压缩
- 支持图片压缩
- 支持文本压缩

### 2. 连接池
- 连接复用
- 负载均衡
- 自动扩缩容

### 3. 缓存机制
- 结果缓存
- 模型缓存
- 连接缓存

## 📚 相关文档

- [API接口文档](./api_documentation.md)
- [前后端集成进度](./frontend_backend_integration.md)
- [部署指南](./deployment/multi_platform_deployment.md)

---

**最后更新**: 2024年1月
**文档版本**: v1.0
**维护人员**: MaoOCR开发团队