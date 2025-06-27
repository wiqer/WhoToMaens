# MaoOCR 配置说明

## 主配置文件

### maoocr_config.yaml

```yaml
# configs/maoocr_config.yaml
system:
  gpu_memory_limit: 10
  cpu_cores_limit: 4
  enable_caching: true
  cache_size: 1000

models:
  cnocr:
    model_path: "models/cnocr"
    confidence_threshold: 0.5
    enable_gpu: true
    
  monkey_ocr:
    model_path: "models/monkey_ocr"
    confidence_threshold: 0.7
    enable_gpu: true
    
  ocrlite:
    model_path: "models/ocrlite"
    confidence_threshold: 0.6
    enable_gpu: false
    
  # PP-OCRv5 + OpenVINO 配置
  pp_ocrv5_openvino:
    model_path: "models/ppocrv5_openvino"
    confidence_threshold: 0.6
    enable_gpu: false  # OpenVINO使用CPU优化
    device: "CPU"  # CPU, GPU, MYRIAD
    num_streams: 4  # 并行流数量
    enable_dynamic_batch: true
    max_batch_size: 8
    enable_async_inference: true
    cache_dir: "cache/openvino"
    
  # PP-OCRv5 原始配置（备用）
  pp_ocrv5:
    model_path: "models/ppocrv5"
    confidence_threshold: 0.6
    enable_gpu: true
    use_angle_cls: true
    lang: "ch"  # ch, en, chinese_cht, french, german, korean, japan

# 集成引擎配置
engines:
  ensemble:
    weights:
      cnocr: 0.20
      paddleocr: 0.20
      easyocr: 0.15
      tesseract: 0.15
      openvino_ppocrv5: 0.30  # PP-OCRv5 + OpenVINO权重最高
    enable_dynamic_weight_adjustment: true
    confidence_threshold: 0.5
    
  openvino:
    device: "CPU"
    num_streams: 4
    enable_dynamic_batch: true
    max_batch_size: 8
    enable_async_inference: true
    cache_dir: "cache/openvino"
    model_optimization:
      enable_fp16: true
      enable_int8: false
      enable_pruning: false

vllm:
  enabled: true
  models:
    qwen2.5-vl:
      model_path: "models/qwen2.5-vl"
      tensor_parallel_size: 1
      gpu_memory_utilization: 0.9
      quantization: "awq"

output:
  format: "markdown"
  output_dir: "output"
  enable_image_segmentation: true
  save_failed_images: true
```

### vLLM模型配置

```yaml
# configs/vllm_models.yaml
models:
  qwen2.5-vl:
    model_path: "models/qwen2.5-vl"
    model_type: "multimodal"
    tensor_parallel_size: 2
    gpu_memory_utilization: 0.9
    max_model_len: 8192
    quantization: "awq"
    
  qwen2.5-7b:
    model_path: "models/qwen2.5-7b"
    model_type: "text"
    tensor_parallel_size: 1
    gpu_memory_utilization: 0.8
    max_model_len: 4096
    quantization: "gptq"

api_interfaces:
  openai:
    enabled: true
    port: 8000
    host: "0.0.0.0"
    
  rest:
    enabled: true
    port: 8001
    host: "0.0.0.0"
    
  websocket:
    enabled: true
    port: 8002
    host: "0.0.0.0"
```

## 外部API配置

### external_apis.yaml

```yaml
# configs/external_apis.yaml
apis:
  openai:
    base_url: "https://api.openai.com/v1"
    api_key: "${OPENAI_API_KEY}"
    timeout: 30
    max_retries: 3
    
  azure_openai:
    base_url: "https://your-resource.openai.azure.com"
    api_key: "${AZURE_OPENAI_API_KEY}"
    api_version: "2024-02-15-preview"
    deployment_name: "gpt-4"
    
  anthropic:
    base_url: "https://api.anthropic.com"
    api_key: "${ANTHROPIC_API_KEY}"
    timeout: 30
    
  google_ai:
    base_url: "https://generativelanguage.googleapis.com"
    api_key: "${GOOGLE_AI_API_KEY}"
    timeout: 30

fallback_strategy:
  enable_fallback: true
  fallback_order: ["openai", "azure_openai", "anthropic", "google_ai"]
  max_fallback_attempts: 3
```

## 性能监控配置

### monitoring_config.yaml

```yaml
# configs/monitoring_config.yaml
monitoring:
  enabled: true
  interval: 5  # 监控间隔（秒）
  retention_days: 30  # 数据保留天数
  
metrics:
  cpu_usage:
    enabled: true
    threshold: 80  # CPU使用率阈值
    
  memory_usage:
    enabled: true
    threshold: 85  # 内存使用率阈值
    
  gpu_usage:
    enabled: true
    threshold: 90  # GPU使用率阈值
    
  disk_usage:
    enabled: true
    threshold: 90  # 磁盘使用率阈值

alerts:
  email:
    enabled: false
    smtp_server: "smtp.gmail.com"
    smtp_port: 587
    username: "${EMAIL_USERNAME}"
    password: "${EMAIL_PASSWORD}"
    recipients: ["admin@example.com"]
    
  webhook:
    enabled: false
    url: "${WEBHOOK_URL}"
    timeout: 10
```

## 性能优化配置

### performance_config.yaml

```yaml
# configs/performance_config.yaml
optimization:
  enable_auto_optimization: true
  max_gpu_memory_usage: 0.9
  max_cpu_usage: 0.8
  enable_model_caching: true
  cache_size_limit: 5
  enable_dynamic_batching: true
  batch_size_optimization: true

caching:
  memory_cache:
    enabled: true
    max_size: 1000
    ttl: 3600  # 1小时
    
  disk_cache:
    enabled: true
    max_size: 10000
    ttl: 86400  # 24小时
    cache_dir: "cache"

batching:
  max_batch_size: 32
  min_batch_size: 1
  batch_timeout: 5  # 秒
  enable_dynamic_batching: true
```

## 文档处理配置

### document_processing_config.yaml

```yaml
# configs/document_processing_config.yaml
pdf_processing:
  enable_text_extraction: true
  enable_layout_analysis: true
  enable_cross_page_continuity: true
  max_pages_per_batch: 50
  
epub_processing:
  enable_conversion: true
  conversion_tool: "calibre"  # calibre, pandoc
  temp_dir: "temp"
  cleanup_temp_files: true
  
docx_processing:
  enable_structure_recognition: true
  enable_style_inference: true
  enable_cross_page_continuity: true
  
markdown_output:
  format: "standard"  # standard, github, gitlab
  enable_toc: true
  enable_metadata: true
  enable_images: true
  image_format: "png"
  max_image_size: 1024
```

## 环境变量配置

### .env 文件示例

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_AI_API_KEY=your_google_ai_api_key

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/maoocr
REDIS_URL=redis://localhost:6379

# Monitoring
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
WEBHOOK_URL=https://your-webhook-url.com

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/maoocr.log

# Model Paths
MODEL_BASE_PATH=/path/to/models
CACHE_DIR=/path/to/cache
TEMP_DIR=/path/to/temp
```

## 配置验证

### 配置验证脚本

```python
from src.maoocr.utils.settings_manager import SettingsManager

# 验证配置
settings = SettingsManager()
is_valid = settings.validate_config()

if is_valid:
    print("配置验证通过")
else:
    print("配置验证失败，请检查配置文件")
```

## 配置热重载

### 启用配置热重载

```python
from src.maoocr.utils.settings_manager import SettingsManager

# 启用配置热重载
settings = SettingsManager(enable_hot_reload=True)

# 监听配置变化
@settings.on_config_change
def handle_config_change(new_config):
    print("配置已更新:", new_config)
```

## 配置最佳实践

### 1. 环境分离
- 开发环境：使用最小配置，快速启动
- 测试环境：模拟生产环境配置
- 生产环境：优化性能和稳定性

### 2. 安全配置
- 使用环境变量存储敏感信息
- 定期轮换API密钥
- 启用访问日志和监控

### 3. 性能调优
- 根据硬件资源调整缓存大小
- 优化批处理参数
- 监控资源使用情况

### 4. 故障恢复
- 配置API降级策略
- 启用自动重试机制
- 设置合理的超时时间 