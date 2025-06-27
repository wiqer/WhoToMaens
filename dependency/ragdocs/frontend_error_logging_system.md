# 前端错误日志收集和上报系统

## 概述

本系统提供了一个完整的前端错误日志收集和上报解决方案，能够收集用户操作上下文、系统资源信息和错误信息，合并后上报到后端存储，方便问题检测和分析。

## 系统架构

### 前端组件
- **错误日志收集器** (`frontend/src/utils/errorLogger.js`)
- **用户操作监听器**
- **系统资源监控器**
- **性能指标收集器**

### 后端组件
- **日志接收API** (`bugagaric/modules/logging/api.py`)
- **日志处理器** (`bugagaric/modules/logging/frontend_log_handler.py`)
- **日志分析工具** (`scripts/frontend_log_analyzer.py`)

### 数据流程
```
前端错误/操作 → 日志收集器 → 定期上报 → 后端API → 日志处理器 → 本地文件存储 → 分析工具 → 问题报告
```

## 功能特性

### 🚀 前端日志收集
- **错误捕获**：JavaScript错误、React错误、Promise拒绝、API错误
- **用户操作跟踪**：点击、输入、表单提交、页面导航等
- **系统信息收集**：浏览器信息、屏幕分辨率、内存使用、性能指标
- **上下文信息**：当前URL、用户会话、操作时间等

### 📊 后端日志处理
- **异步处理**：队列机制，不阻塞主线程
- **批量写入**：提高写入效率
- **按日期组织**：自动按日期分类存储
- **数据验证**：确保数据格式正确

### 🔍 日志分析
- **错误模式识别**：自动识别重复错误和问题模式
- **性能问题分析**：页面加载时间、内存使用等
- **用户行为分析**：操作习惯、页面访问统计
- **智能建议**：基于分析结果生成改进建议

## 快速开始

### 1. 前端集成

#### 安装依赖
```bash
# 前端项目根目录
npm install
```

#### 引入日志收集器
```javascript
// 在 main.jsx 或 App.jsx 中引入
import { errorLogger, logError, logUserAction, logPerformance } from './utils/errorLogger';

// 自动开始收集日志
console.log('前端日志收集器已启动');
```

#### 手动记录日志
```javascript
// 记录用户操作
logUserAction('button_click', {
  buttonId: 'submit-btn',
  page: 'login'
});

// 记录性能指标
logPerformance('page_load_time', 1500, {
  page: 'dashboard'
});

// 记录自定义错误
logError({
  type: 'custom_error',
  message: '用户操作失败',
  details: { userId: 123, action: 'save' }
});
```

### 2. 后端集成

#### 注册API路由
```python
# 在Flask应用中注册蓝图
from bugagaric.modules.logging.api import frontend_logs_bp

app.register_blueprint(frontend_logs_bp)
```

#### 启动日志处理器
```python
# 日志处理器会自动启动
from bugagaric.modules.logging.frontend_log_handler import frontend_log_handler

# 检查服务状态
stats = frontend_log_handler.get_log_stats()
print(f"今日日志统计: {stats}")
```

### 3. 日志分析

#### 运行分析工具
```bash
# 分析今天的日志
python3 scripts/frontend_log_analyzer.py

# 分析指定日期的日志
python3 scripts/frontend_log_analyzer.py --date 2024-01-01

# 分析多天日志
python3 scripts/frontend_log_analyzer.py --date 2024-01-01 --days 7
```

## 数据格式

### 前端上报数据格式
```json
{
  "sessionId": "session_1234567890_abc123",
  "timestamp": "2024-01-01T10:00:00Z",
  "logs": [
    {
      "id": "log_1234567890_xyz789",
      "sessionId": "session_1234567890_abc123",
      "timestamp": "2024-01-01T10:00:00Z",
      "type": "error",
      "severity": "critical",
      "error": {
        "type": "javascript_error",
        "message": "Cannot read property 'length' of undefined",
        "stack": "Error stack trace...",
        "filename": "app.js",
        "lineno": 42,
        "colno": 15
      },
      "context": {
        "user": {
          "lastActionTime": 1704110400000,
          "actionCount": 15,
          "currentUrl": "https://example.com/dashboard",
          "timeOnPage": 30000,
          "eventType": "click",
          "target": {
            "tagName": "BUTTON",
            "className": "btn-primary",
            "id": "save-btn"
          }
        },
        "system": {
          "userAgent": "Mozilla/5.0...",
          "platform": "MacIntel",
          "screen": {
            "width": 1920,
            "height": 1080
          },
          "memory": {
            "usedJSHeapSize": 52428800,
            "totalJSHeapSize": 104857600
          }
        },
        "url": "https://example.com/dashboard",
        "referrer": "https://example.com/login"
      }
    }
  ],
  "summary": {
    "totalLogs": 10,
    "errorCount": 2,
    "userActionCount": 7,
    "performanceCount": 1
  }
}
```

### 后端存储格式

#### 详细日志文件 (`detailed_logs.jsonl`)
```json
{
  "report_session_id": "session_1234567890_abc123",
  "report_timestamp": "2024-01-01T10:00:00Z",
  "log_entry": {
    "id": "log_1234567890_xyz789",
    "session_id": "session_1234567890_abc123",
    "timestamp": "2024-01-01T10:00:00Z",
    "type": "error",
    "severity": "critical",
    "error": {...},
    "context": {...}
  }
}
```

#### 摘要文件 (`summary.json`)
```json
{
  "date": "2024-01-01",
  "reports": [
    {
      "session_id": "session_1234567890_abc123",
      "timestamp": "2024-01-01T10:00:00Z",
      "summary": {
        "totalLogs": 10,
        "errorCount": 2,
        "userActionCount": 7,
        "performanceCount": 1
      }
    }
  ],
  "total_logs": 10,
  "processed_at": "2024-01-01T10:05:00Z"
}
```

## API接口

### 1. 上报日志
```http
POST /api/logs/frontend
Content-Type: application/json

{
  "sessionId": "session_xxx",
  "timestamp": "2024-01-01T10:00:00Z",
  "logs": [...],
  "summary": {...}
}
```

### 2. 获取日志统计
```http
GET /api/logs/frontend/stats?date=2024-01-01
```

### 3. 获取错误日志
```http
GET /api/logs/frontend/errors?date=2024-01-01&limit=100&severity=critical
```

### 4. 清理旧日志
```http
POST /api/logs/frontend/cleanup
Content-Type: application/json

{
  "days": 30
}
```

### 5. 健康检查
```http
GET /api/logs/frontend/health
```

## 配置选项

### 前端配置
```javascript
// 环境变量配置
REACT_APP_ENABLE_ERROR_LOGGING=true  // 启用错误日志收集
NODE_ENV=development                 // 开发环境自动启用

// 日志收集器配置
const errorLogger = new ErrorLogger({
  maxLogs: 1000,           // 最大日志数量
  reportInterval: 300000,  // 上报间隔（毫秒）
  enablePerformance: true, // 启用性能监控
  enableUserActions: true  // 启用用户操作跟踪
});
```

### 后端配置
```python
# 日志处理器配置
frontend_log_handler = FrontendLogHandler(
    log_dir="logs/frontend",    # 日志存储目录
    batch_size=100,            # 批量处理大小
    flush_interval=30          # 刷新间隔（秒）
)
```

## 分析报告

### 报告内容
- **摘要统计**：总日志数、错误数、用户操作数等
- **错误分析**：错误类型分布、严重程度、重复错误模式
- **用户行为分析**：操作习惯、页面访问统计、时间分布
- **性能分析**：页面加载时间、内存使用、性能问题识别
- **问题模式**：自动识别的问题模式和趋势
- **改进建议**：基于分析结果的优化建议

### 报告格式
- **JSON格式**：`reports/frontend_logs/analysis_report_2024-01-01.json`
- **文本格式**：`reports/frontend_logs/analysis_report_2024-01-01.txt`

## 最佳实践

### 1. 前端最佳实践
- **合理配置**：根据应用规模调整日志收集频率
- **隐私保护**：避免收集敏感用户信息
- **性能考虑**：避免过度收集影响用户体验
- **错误边界**：在React组件中使用错误边界

### 2. 后端最佳实践
- **定期清理**：设置自动清理旧日志文件
- **监控告警**：设置错误率告警机制
- **数据备份**：重要日志数据定期备份
- **性能优化**：使用异步处理和批量写入

### 3. 分析最佳实践
- **定期分析**：设置定时任务定期分析日志
- **趋势监控**：关注错误趋势和用户行为变化
- **问题追踪**：建立问题追踪和解决流程
- **持续改进**：基于分析结果持续优化应用

## 故障排除

### 常见问题

#### 1. 前端日志未上报
```javascript
// 检查日志收集器状态
console.log('日志收集器状态:', errorLogger.isEnabled);
console.log('当前日志数量:', errorLogger.logs.length);

// 手动上报日志
await errorLogger.reportNow();
```

#### 2. 后端接收失败
```python
# 检查日志处理器状态
stats = frontend_log_handler.get_log_stats()
print(f"处理器状态: {stats}")

# 检查日志目录
import os
print(f"日志目录存在: {os.path.exists('logs/frontend')}")
```

#### 3. 分析工具错误
```bash
# 检查日志文件
ls -la logs/frontend/

# 检查报告目录
ls -la reports/frontend_logs/
```

### 调试模式
```javascript
// 前端调试
if (process.env.NODE_ENV === 'development') {
  console.log('日志收集器调试信息:', errorLogger.getLogStats());
}

# 后端调试
import logging
logging.getLogger('bugagaric.modules.logging').setLevel(logging.DEBUG)
```

## 扩展开发

### 添加新的日志类型
```javascript
// 前端：添加自定义日志类型
errorLogger.logCustom('business_error', {
  errorCode: 'USER_NOT_FOUND',
  userId: 123,
  action: 'login'
});

// 后端：扩展日志处理器
class CustomLogHandler(FrontendLogHandler):
    def handle_custom_log(self, log_data):
        # 处理自定义日志
        pass
```

### 自定义分析规则
```python
# 扩展分析器
class CustomLogAnalyzer(FrontendLogAnalyzer):
    def analyze_business_errors(self, logs):
        # 自定义业务错误分析
        pass
```

## 监控和告警

### 错误率监控
```python
# 检查错误率
def check_error_rate(date_str=None):
    stats = frontend_log_handler.get_log_stats(date_str)
    error_logs = frontend_log_handler.get_error_logs(date_str)
    
    if stats['total_logs'] > 0:
        error_rate = len(error_logs) / stats['total_logs']
        if error_rate > 0.1:  # 错误率超过10%
            send_alert(f"前端错误率过高: {error_rate:.2%}")
```

### 性能监控
```python
# 检查性能问题
def check_performance_issues():
    analyzer = FrontendLogAnalyzer()
    result = analyzer.analyze_logs()
    
    for issue in result['performance_analysis']['performance_issues']:
        if issue['percentage'] > 20:  # 超过20%的性能问题
            send_alert(f"性能问题: {issue['type']}")
```

## 总结

本前端错误日志收集和上报系统提供了完整的解决方案，能够：

1. **全面收集**：错误信息、用户操作、系统资源、性能指标
2. **智能分析**：自动识别问题模式、生成改进建议
3. **易于集成**：简单的API接口、灵活的配置选项
4. **高效处理**：异步处理、批量写入、按日期组织
5. **便于维护**：清晰的文档、完整的工具链

通过使用本系统，可以显著提升前端应用的稳定性和用户体验，快速定位和解决问题。 