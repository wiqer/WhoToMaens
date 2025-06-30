# WhoToMaens 规则引擎SDK使用指南

## 概述

WhoToMaens是一个基于自学习自编程优化机制的智能图片特征分析与子图提取系统。本SDK提供了完整的规则引擎、知识提取器、自适应优化器等功能模块，支持以SDK方式接入BlitzkriegFlow。

## 核心功能

### 1. 知识提取器 (KnowledgeExtractor)
- 从LLM响应中提取结构化知识
- 模式识别和规则生成
- 知识库管理和验证

### 2. 自适应优化器 (AdaptiveOptimizer)
- 处理流程动态优化
- 性能监控和瓶颈分析
- 自适应学习机制

### 3. 嵌入式规则引擎 (EmbeddedRuleEngine)
- 规则匹配和推理执行
- 规则学习和更新
- 性能缓存和优化

### 4. 规则优先级管理 (RulePriorityManager)
- 智能优先级计算
- 使用频率分析
- 上下文相关性评估

### 5. 规则缓存管理 (RuleCacheManager)
- LRU缓存实现
- 预加载机制
- 缓存优化策略

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 基本使用

```python
from src.sdk.blitzkrieg_flow_sdk import BlitzkriegFlowSDK, BlitzkriegFlowConfig
from src.core import Rule

# 创建SDK配置
config = BlitzkriegFlowConfig(
    api_endpoint="http://localhost:8000",
    enable_cache=True,
    enable_optimization=True,
    enable_learning=True
)

# 初始化SDK
sdk = BlitzkriegFlowSDK(config)

# 创建规则
rule = Rule(
    rule_id="my_rule",
    rule_type="classification",
    conditions=[
        {"type": "field_match", "field": "color", "operator": "eq", "value": "red"}
    ],
    actions=[
        {"type": "classification", "field": "category", "target": "red_object"}
    ],
    priority=0.8,
    accuracy=0.9
)

# 添加规则
sdk.add_rule(rule)

# 处理请求
import asyncio

async def process_request():
    from src.sdk.blitzkrieg_flow_sdk import FlowRequest
    
    request = FlowRequest(
        request_id="test_request",
        input_data={"color": "red", "shape": "circle"},
        flow_type="image_analysis"
    )
    
    response = await sdk.process_flow(request)
    print(f"处理结果: {response.result}")

asyncio.run(process_request())
```

### 3. 便捷函数使用

```python
from src.sdk.blitzkrieg_flow_sdk import process_flow, add_rule, get_stats

# 添加规则
rule = Rule(...)
add_rule(rule)

# 处理流程
response = await process_flow(
    input_data={"color": "red"},
    flow_type="image_analysis"
)

# 获取统计信息
stats = get_stats()
print(f"规则命中率: {stats['sdk_stats']['rule_hit_rate']}")
```

## API接口

### 1. 规则引擎API

启动API服务：

```bash
uvicorn src.api.rule_engine_api:app --host 0.0.0.0 --port 8000
```

#### 主要端点：

- `POST /process` - 处理请求
- `POST /rules` - 创建规则
- `GET /rules` - 获取规则列表
- `GET /rules/{rule_id}` - 获取规则详情
- `DELETE /rules/{rule_id}` - 删除规则
- `POST /feedback` - 提交反馈
- `GET /stats` - 获取统计信息
- `POST /optimize` - 触发优化

### 2. 请求示例

```python
import requests

# 处理请求
response = requests.post("http://localhost:8000/process", json={
    "input_data": {"color": "red", "shape": "circle"},
    "context": {"data_type": "image"},
    "use_cache": True,
    "fallback_to_llm": True
})

print(response.json())

# 创建规则
rule_data = {
    "rule_type": "classification",
    "conditions": [
        {"type": "field_match", "field": "color", "operator": "eq", "value": "red"}
    ],
    "actions": [
        {"type": "classification", "field": "category", "target": "red_object"}
    ],
    "priority": 0.8,
    "accuracy": 0.9
}

response = requests.post("http://localhost:8000/rules", json=rule_data)
print(response.json())
```

## 核心组件详解

### 1. 知识提取器

```python
from src.core import KnowledgeExtractor

extractor = KnowledgeExtractor()

# 从LLM响应中提取知识
llm_response = {
    "features": [...],
    "classification": {...},
    "rules": [...]
}

patterns, rules = extractor.extract_from_llm_response(
    json.dumps(llm_response),
    context={"data_type": "image"}
)

print(f"提取到 {len(patterns)} 个模式")
print(f"生成 {len(rules)} 条规则")
```

### 2. 自适应优化器

```python
from src.core import AdaptiveOptimizer, ProcessingPipeline

optimizer = AdaptiveOptimizer()

# 创建处理流程
pipeline = ProcessingPipeline(
    pipeline_id="my_pipeline",
    steps=[
        {"name": "feature_extraction", "method": "resnet"},
        {"name": "classification", "method": "svm"}
    ]
)

# 优化流程
input_data = {"image_size": "large", "complexity": "high"}
optimized_pipeline = optimizer.optimize_processing_pipeline(input_data, pipeline)

print(f"优化后步骤数: {len(optimized_pipeline.steps)}")
```

### 3. 规则引擎

```python
from src.core import EmbeddedRuleEngine, Rule

engine = EmbeddedRuleEngine()

# 添加规则
rule = Rule(
    rule_id="my_rule",
    rule_type="classification",
    conditions=[{"type": "field_match", "field": "color", "operator": "eq", "value": "red"}],
    actions=[{"type": "classification", "field": "category", "target": "red_object"}],
    priority=0.8,
    accuracy=0.9
)

engine.add_rule(rule)

# 处理请求
result, rule_used = engine.process_request(
    {"color": "red", "shape": "circle"},
    {"data_type": "image"}
)

print(f"处理结果: {result}")
print(f"是否使用规则: {rule_used}")
```

### 4. 优先级管理

```python
from src.core import RulePriorityManager

priority_manager = RulePriorityManager()

# 计算规则优先级
priority_score = priority_manager.calculate_rule_priority(rule, context)

# 记录使用情况
priority_manager.record_rule_usage(
    rule_id="my_rule",
    success=True,
    execution_time=0.1,
    context={"data_type": "image"}
)

# 获取优先级信息
priority_info = priority_manager.get_rule_priority_info("my_rule")
print(f"优先级信息: {priority_info}")
```

### 5. 缓存管理

```python
from src.core import RuleCacheManager

cache_manager = RuleCacheManager()

# 缓存规则
cache_manager.cache_rule(rule)

# 缓存执行结果
cache_manager.cache_rule_result(rule, input_data, result)

# 获取缓存
cached_rule = cache_manager.get_cached_rule(rule.rule_id)
cached_result = cache_manager.get_cached_result(rule, input_data)

# 优化缓存
cache_manager.optimize_cache()
```

## 配置选项

### SDK配置

```python
config = BlitzkriegFlowConfig(
    api_endpoint="http://localhost:8000",  # API端点
    api_key=None,                          # API密钥
    timeout=30,                            # 超时时间
    max_retries=3,                         # 最大重试次数
    enable_cache=True,                     # 启用缓存
    enable_optimization=True,              # 启用优化
    enable_learning=True                   # 启用学习
)
```

### 缓存配置

```python
cache_config = {
    'result_expiry': 3600,      # 结果缓存过期时间（秒）
    'rule_expiry': 7200,        # 规则缓存过期时间（秒）
    'preload_threshold': 10,    # 预加载阈值
    'max_preload_size': 100     # 最大预加载数量
}

cache_manager.set_cache_config(cache_config)
```

## 性能优化

### 1. 缓存优化

- 启用结果缓存减少重复计算
- 预加载频繁使用的规则
- 定期清理过期缓存项

### 2. 规则优化

- 使用优先级管理优化规则执行顺序
- 根据使用频率动态调整规则权重
- 定期清理低效规则

### 3. 系统优化

- 启用自适应优化器自动调整处理流程
- 监控性能指标识别瓶颈
- 使用后台任务执行优化操作

## 监控和统计

### 1. 获取统计信息

```python
# SDK统计
sdk_stats = sdk.get_stats()

# 引擎统计
engine_stats = rule_engine.get_engine_stats()

# 缓存统计
cache_stats = cache_manager.get_cache_stats()

# 优先级统计
priority_stats = priority_manager.get_priority_stats()
```

### 2. 关键指标

- **规则命中率**: 规则引擎处理请求的比例
- **缓存命中率**: 缓存命中请求的比例
- **平均处理时间**: 请求的平均处理时间
- **成功率**: 成功处理的请求比例

## 错误处理

### 1. 异常处理

```python
try:
    response = await sdk.process_flow(request)
    if not response.success:
        print(f"处理失败: {response.error_message}")
except Exception as e:
    print(f"系统错误: {e}")
```

### 2. 回退机制

- 规则引擎未匹配时自动回退到LLM
- 缓存失效时重新计算
- 优化失败时使用默认配置

## 扩展开发

### 1. 自定义流程处理器

```python
def custom_processor(request: FlowRequest) -> Dict[str, Any]:
    # 自定义处理逻辑
    return {
        'success': True,
        'result': {'custom': 'result'},
        'processed_by': 'custom_processor'
    }

# 注册处理器
sdk.register_flow_processor("custom_flow", custom_processor)
```

### 2. 自定义规则类型

```python
# 创建自定义规则
custom_rule = Rule(
    rule_id="custom_rule",
    rule_type="custom_type",
    conditions=[...],
    actions=[...],
    priority=0.8,
    accuracy=0.9
)
```

## 最佳实践

### 1. 规则设计

- 保持规则简洁明确
- 合理设置优先级和准确性
- 定期更新和优化规则

### 2. 性能优化

- 启用缓存减少重复计算
- 使用优先级管理优化执行顺序
- 定期清理无用数据

### 3. 监控维护

- 定期检查系统统计信息
- 监控性能指标变化
- 及时处理异常情况

## 示例代码

完整示例请参考 `examples/rule_engine_demo.py` 文件。

## 技术支持

如有问题，请查看：
- API文档: `http://localhost:8000/docs`
- 示例代码: `examples/`
- 核心模块: `src/core/`
- SDK模块: `src/sdk/` 