# MaoOCR 监控系统文档

## 📋 概述

MaoOCR监控系统是一个完整的生产级监控解决方案，包含性能监控、日志聚合、告警系统和健康检查四个核心组件。该系统为MaoOCR提供了全面的可观测性，确保系统稳定运行和快速问题定位。

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    MaoOCR 监控系统                          │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   性能监控   │  │   日志聚合   │  │   告警系统   │         │
│  │ Performance │  │ Log Aggreg. │  │ Alert System│         │
│  │  Dashboard  │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   健康检查   │  │   API接口   │  │   配置管理   │         │
│  │ Health Check│  │ Monitoring  │  │   Config    │         │
│  │             │  │    API      │  │ Management  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 核心组件

### 1. 性能监控面板 (Performance Dashboard)

#### 功能特性
- **实时指标收集**: CPU、内存、GPU、磁盘、网络等系统资源
- **性能指标监控**: 请求率、错误率、响应时间、吞吐量
- **缓存性能**: 命中率、缓存大小、请求统计
- **历史数据**: 可配置时间范围的历史数据查询
- **数据导出**: 支持JSON格式的数据导出
- **PP-OCRv5监控**: 推理速度、准确率、模型加载状态
- **OpenVINO监控**: 设备使用率、推理流状态、模型缓存命中率
- **引擎性能对比**: 各OCR引擎的性能对比分析

#### 主要API
```python
# 获取仪表板数据
GET /api/monitoring/dashboard?time_range=60

# 获取实时指标
GET /api/monitoring/realtime

# 导出指标数据
GET /api/monitoring/export?format=json

# 获取PP-OCRv5性能指标
GET /api/monitoring/pp_ocrv5_metrics

# 获取OpenVINO设备状态
GET /api/monitoring/openvino_status

# 获取引擎性能对比
GET /api/monitoring/engine_comparison
```

#### 配置参数
```yaml
performance_dashboard:
  monitoring_interval: 5  # 监控间隔（秒）
  max_history_size: 1000  # 最大历史记录数
  cache_duration: 1.0     # 缓存时间（秒）
  
  # PP-OCRv5监控配置
  pp_ocrv5_monitoring:
    enabled: true
    inference_time_threshold: 1000  # 推理时间阈值（毫秒）
    accuracy_threshold: 0.8         # 准确率阈值
    model_load_timeout: 30          # 模型加载超时（秒）
    
  # OpenVINO监控配置
  openvino_monitoring:
    enabled: true
    device_usage_threshold: 90      # 设备使用率阈值
    stream_utilization_threshold: 80 # 流利用率阈值
    cache_hit_rate_threshold: 70    # 缓存命中率阈值
```

### 2. 日志聚合分析 (Log Aggregator)

#### 功能特性
- **日志收集**: 自动收集系统所有日志
- **模式匹配**: 预定义日志模式识别
- **错误分析**: 自动分类和统计错误
- **日志搜索**: 全文搜索和过滤
- **统计分析**: 按级别、模块、时间统计
- **数据持久化**: SQLite数据库存储

#### 预定义日志模式
```python
# OCR识别失败
pattern: "OCR recognition failed: (.+)"

# 模型加载失败
pattern: "Failed to load (.+): (.+)"

# 性能优化
pattern: "Performance optimization: (.+)"

# 缓存命中率
pattern: "Cache hit rate: (.+)%"

# 资源使用情况
pattern: "Resource usage: CPU=(.+)%, Memory=(.+)%, GPU=(.+)%"
```

#### 主要API
```python
# 获取日志
GET /api/logs?level=ERROR&limit=100&hours=24

# 获取日志统计
GET /api/logs/statistics?hours=24

# 获取错误分析
GET /api/logs/errors?hours=24

# 搜索日志
GET /api/logs/search?query=OCR&case_sensitive=false

# 导出日志
GET /api/logs/export?format=json&hours=24
```

### 3. 告警系统 (Alert System)

#### 功能特性
- **多级别告警**: INFO、WARNING、ERROR、CRITICAL
- **灵活规则**: 支持多种条件和阈值
- **通知渠道**: 邮件、Webhook、Slack等
- **告警管理**: 确认、解决、历史记录
- **实时监控**: 自动检测和触发告警

#### 默认告警规则
```yaml
# 高CPU使用率
high_cpu_usage:
  metric: "cpu_usage"
  condition: ">"
  threshold: 80.0
  level: "warning"
  duration: 300

# 高内存使用率
high_memory_usage:
  metric: "memory_usage"
  condition: ">"
  threshold: 85.0
  level: "warning"
  duration: 300

# 高错误率
high_error_rate:
  metric: "error_rate"
  condition: ">"
  threshold: 5.0
  level: "error"
  duration: 60

# PP-OCRv5推理时间过长
pp_ocrv5_slow_inference:
  metric: "pp_ocrv5_inference_time"
  condition: ">"
  threshold: 1000.0  # 毫秒
  level: "warning"
  duration: 60

# PP-OCRv5准确率过低
pp_ocrv5_low_accuracy:
  metric: "pp_ocrv5_accuracy"
  condition: "<"
  threshold: 0.8
  level: "error"
  duration: 300

# PP-OCRv5模型加载失败
pp_ocrv5_model_load_failed:
  metric: "pp_ocrv5_model_status"
  condition: "=="
  threshold: "failed"
  level: "critical"
  duration: 0

# OpenVINO设备使用率过高
openvino_high_device_usage:
  metric: "openvino_device_usage"
  condition: ">"
  threshold: 90.0
  level: "warning"
  duration: 120

# OpenVINO缓存命中率过低
openvino_low_cache_hit_rate:
  metric: "openvino_cache_hit_rate"
  condition: "<"
  threshold: 70.0
  level: "warning"
  duration: 300

# OpenVINO推理流利用率过低
openvino_low_stream_utilization:
  metric: "openvino_stream_utilization"
  condition: "<"
  threshold: 50.0
  level: "info"
  duration: 600
```

#### 通知渠道配置
```yaml
notification_channels:
  email:
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-app-password"
    
  webhook:
    url: "https://your-webhook-url.com/alerts"
    headers:
      Authorization: "Bearer your-token"
      
  slack:
    webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    channel: "#alerts"
```

#### 主要API
```python
# 获取活跃告警
GET /api/alerts

# 获取告警历史
GET /api/alerts/history?hours=24

# 获取告警统计
GET /api/alerts/statistics?hours=24

# 确认告警
POST /api/alerts/{rule_name}/acknowledge?user=admin

# 解决告警
POST /api/alerts/{rule_name}/resolve
```

### 4. 健康检查 (Health Checker)

#### 功能特性
- **多维度检查**: 系统资源、缓存、模型服务、网络、磁盘
- **可配置检查项**: 支持自定义检查规则
- **超时控制**: 防止检查项阻塞系统
- **状态分级**: HEALTHY、WARNING、CRITICAL、UNKNOWN
- **实时监控**: 定期自动检查

#### 默认检查项
```yaml
default_checks:
  system_resources:
    description: "系统资源检查"
    timeout: 10.0
    interval: 60.0
    critical: true
    
  cache_system:
    description: "缓存系统检查"
    timeout: 5.0
    interval: 120.0
    critical: false
    
  model_services:
    description: "模型服务检查"
    timeout: 15.0
    interval: 180.0
    critical: true
    
  network_connectivity:
    description: "网络连接检查"
    timeout: 10.0
    interval: 300.0
    critical: false
```

#### 主要API
```python
# 获取健康状态
GET /api/health

# 获取特定检查结果
GET /api/health/{check_name}

# 立即运行检查
POST /api/health/{check_name}/run
```

## ⚙️ 配置管理

### 配置文件结构
```yaml
# configs/monitoring_config.yaml
performance_dashboard:
  # 性能监控配置
  
log_aggregation:
  # 日志聚合配置
  
alert_system:
  # 告警系统配置
  
health_checker:
  # 健康检查配置
  
monitoring_api:
  # API配置
  
export:
  # 导出配置
  
dashboard:
  # 仪表板配置
```

### 环境变量
```bash
# 监控系统配置
MAOOCR_MONITORING_ENABLED=true
MAOOCR_MONITORING_CONFIG_PATH=configs/monitoring_config.yaml

# 日志配置
MAOOCR_LOG_LEVEL=INFO
MAOOCR_LOG_FILE=logs/monitoring.log

# 数据库配置
MAOOCR_LOG_DB_PATH=logs/maoocr_logs.db
```

## 🔧 部署指南

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置监控系统
```bash
# 复制配置文件
cp configs/monitoring_config.yaml.example configs/monitoring_config.yaml

# 编辑配置
vim configs/monitoring_config.yaml
```

### 3. 启动监控系统
```bash
# 启动MaoOCR服务（包含监控）
python run_server.py

# 或者单独运行监控演示
python examples/monitoring_demo.py
```

### 4. 验证监控系统
```bash
# 检查健康状态
curl http://localhost:8000/api/health

# 获取性能指标
curl http://localhost:8000/api/monitoring/realtime

# 获取日志统计
curl http://localhost:8000/api/logs/statistics
```

## 📊 监控仪表板

### 访问地址
- 主监控页面: `http://localhost:8000/monitoring`
- API文档: `http://localhost:8000/docs`

### 主要功能
1. **实时监控**: 显示当前系统状态
2. **历史趋势**: 展示性能指标变化趋势
3. **告警管理**: 查看和管理告警
4. **日志查看**: 实时日志流和历史日志查询
5. **健康状态**: 系统健康检查结果

## 🚨 告警处理

### 告警级别说明
- **INFO**: 信息性告警，不影响系统运行
- **WARNING**: 警告告警，需要关注但非紧急
- **ERROR**: 错误告警，影响部分功能
- **CRITICAL**: 严重告警，影响系统核心功能

### 告警处理流程
1. **告警触发**: 系统自动检测并触发告警
2. **通知发送**: 通过配置的渠道发送通知
3. **告警确认**: 管理员确认告警
4. **问题处理**: 解决导致告警的问题
5. **告警解决**: 标记告警为已解决

### 告警规则管理
```python
# 添加自定义告警规则
from src.maoocr.monitoring.alert_system import alert_system, AlertRule, AlertLevel

custom_rule = AlertRule(
    name="custom_rule",
    description="自定义告警规则",
    metric="custom_metric",
    condition: ">",
    threshold: 100.0,
    level: AlertLevel.WARNING,
    duration: 60
)
alert_system.add_rule(custom_rule)
```

## 📈 性能优化

### 监控系统性能
- **数据缓存**: 减少重复计算
- **异步处理**: 避免阻塞主线程
- **数据压缩**: 减少存储空间
- **定期清理**: 自动清理过期数据

### 资源使用优化
```yaml
# 优化配置示例
performance_dashboard:
  max_history_size: 500  # 减少历史记录数
  cache_duration: 2.0    # 增加缓存时间

log_aggregation:
  max_entries: 5000      # 减少日志条目数
  retention_days: 7      # 减少保留天数
```

## 🔍 故障排查

### 常见问题

#### 1. 监控系统启动失败
```bash
# 检查日志
tail -f logs/monitoring.log

# 检查配置
python -c "import yaml; yaml.safe_load(open('configs/monitoring_config.yaml'))"
```

#### 2. 告警不触发
```bash
# 检查告警规则
curl http://localhost:8000/api/alerts/statistics

# 检查指标值
curl http://localhost:8000/api/monitoring/realtime
```

#### 3. 通知发送失败
```bash
# 检查网络连接
ping smtp.gmail.com

# 检查认证信息
python -c "import smtplib; print('SMTP配置正确')"
```

### 调试模式
```python
# 启用调试日志
import logging
logging.getLogger('src.maoocr.monitoring').setLevel(logging.DEBUG)
```

## 📚 API参考

### 监控API端点
| 端点 | 方法 | 描述 |
|------|------|------|
| `/api/monitoring/dashboard` | GET | 获取性能监控面板数据 |
| `/api/monitoring/realtime` | GET | 获取实时性能指标 |
| `/api/monitoring/export` | GET | 导出性能指标数据 |
| `/api/logs` | GET | 获取日志 |
| `/api/logs/statistics` | GET | 获取日志统计 |
| `/api/logs/errors` | GET | 获取错误分析 |
| `/api/logs/search` | GET | 搜索日志 |
| `/api/logs/export` | GET | 导出日志 |
| `/api/alerts` | GET | 获取活跃告警 |
| `/api/alerts/history` | GET | 获取告警历史 |
| `/api/alerts/statistics` | GET | 获取告警统计 |
| `/api/alerts/{rule_name}/acknowledge` | POST | 确认告警 |
| `/api/alerts/{rule_name}/resolve` | POST | 解决告警 |
| `/api/health` | GET | 获取健康状态 |
| `/api/health/{check_name}` | GET | 获取特定检查结果 |
| `/api/health/{check_name}/run` | POST | 立即运行检查 |

### 响应格式
```json
{
  "success": true,
  "data": {
    // 具体数据
  },
  "error": null
}
```

## 🔮 未来规划

### 计划功能
1. **分布式监控**: 支持多节点监控
2. **机器学习告警**: 基于ML的异常检测
3. **可视化增强**: 更多图表类型和交互
4. **移动端支持**: 移动应用监控
5. **集成第三方**: Prometheus、Grafana等

### 性能优化
1. **数据压缩**: 更高效的数据存储
2. **缓存优化**: 多级缓存策略
3. **并发处理**: 提高处理能力
4. **资源限制**: 防止监控系统影响主服务

## 📞 支持

### 文档资源
- [API文档](http://localhost:8000/docs)
- [配置示例](configs/monitoring_config.yaml)
- [演示代码](examples/monitoring_demo.py)

### 问题反馈
- GitHub Issues: [提交问题](https://github.com/your-repo/maoocr/issues)
- 邮件支持: support@maoocr.com

---

**注意**: 本监控系统为MaoOCR项目提供生产级监控能力，建议在生产环境中充分测试后再部署使用。 