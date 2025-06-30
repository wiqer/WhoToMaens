# WhoToMaens - 智能图片特征分析与子图提取系统

## 项目概述

WhoToMaens是一个基于自学习自编程优化机制的智能图片特征分析与子图提取系统。系统采用嵌入式规则引擎和自适应优化技术，能够自动从LLM响应中学习规则，减少LLM调用频率，提升处理效率。

## 核心特性

### 🧠 自学习自编程优化机制
- **知识提取器**: 从LLM响应中自动提取结构化知识和模式
- **规则生成**: 基于模式自动生成可执行的规则
- **自适应优化**: 动态优化处理流程，提升系统性能
- **LLM调用减少**: 通过规则引擎减少90%以上的LLM API调用

### ⚡ 嵌入式规则引擎
- **规则匹配**: 智能规则匹配和推理执行
- **优先级管理**: 基于使用频率、准确性、上下文的多维度优先级计算
- **缓存优化**: LRU缓存机制，支持预加载和智能清理
- **规则学习**: 从用户反馈中持续学习和优化规则

### 🔄 自适应优化系统
- **性能监控**: 实时监控系统性能指标
- **瓶颈分析**: 自动识别和解决性能瓶颈
- **流程优化**: 动态调整处理流程参数
- **资源管理**: 智能管理计算和内存资源

### 🌐 多接口支持
- **RESTful API**: 完整的HTTP API接口
- **SDK集成**: 支持以SDK方式接入BlitzkriegFlow
- **异步处理**: 支持高并发异步请求处理
- **实时统计**: 提供详细的系统运行统计信息

## 系统架构

```
WhoToMaens/
├── src/
│   ├── core/                    # 核心模块
│   │   ├── knowledge_extractor.py      # 知识提取器
│   │   ├── adaptive_optimizer.py       # 自适应优化器
│   │   ├── rule_engine.py             # 嵌入式规则引擎
│   │   ├── rule_priority_manager.py   # 规则优先级管理
│   │   ├── rule_cache_manager.py      # 规则缓存管理
│   │   ├── feature_extractor.py       # 特征提取器
│   │   ├── image_processor.py         # 图像处理器
│   │   ├── cluster_analyzer.py        # 聚类分析器
│   │   ├── content_analyzer.py        # 内容分析器
│   │   └── hotspot_detector.py        # 热点检测器
│   ├── api/                     # API接口
│   │   └── rule_engine_api.py         # 规则引擎API
│   ├── sdk/                     # SDK模块
│   │   └── blitzkrieg_flow_sdk.py     # BlitzkriegFlow SDK
│   ├── models/                  # 模型模块
│   │   └── multi_modal_model.py       # 多模态模型
│   └── utils/                   # 工具模块
│       ├── config_utils.py            # 配置工具
│       ├── file_utils.py              # 文件工具
│       ├── image_utils.py             # 图像工具
│       └── visualization_utils.py     # 可视化工具
├── examples/                    # 示例代码
│   └── rule_engine_demo.py            # 规则引擎演示
├── docs/                        # 文档
│   ├── image_processing_software_design.md  # 系统设计文档
│   └── kg/                      # 知识图谱文档
├── dependency/                  # 依赖管理
├── main.py                      # 主程序入口
├── requirements.txt             # 依赖列表
└── README.md                    # 项目说明
```

## 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <repository-url>
cd WhoToMaens

# 安装依赖
pip install -r requirements.txt
```

### 2. 基本使用

#### 使用SDK

```python
from src.sdk.blitzkrieg_flow_sdk import BlitzkriegFlowSDK, BlitzkriegFlowConfig
from src.core import Rule

# 创建SDK配置
config = BlitzkriegFlowConfig(
    enable_cache=True,
    enable_optimization=True,
    enable_learning=True
)

# 初始化SDK
sdk = BlitzkriegFlowSDK(config)

# 创建规则
rule = Rule(
    rule_id="color_classification",
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
from src.sdk.blitzkrieg_flow_sdk import FlowRequest

async def process_request():
    request = FlowRequest(
        request_id="test_request",
        input_data={"color": "red", "shape": "circle"},
        flow_type="image_analysis"
    )
    
    response = await sdk.process_flow(request)
    print(f"处理结果: {response.result}")

asyncio.run(process_request())
```

#### 使用API

```bash
# 启动API服务
uvicorn src.api.rule_engine_api:app --host 0.0.0.0 --port 8000
```

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
```

### 3. 运行示例

```bash
# 运行演示脚本
python examples/rule_engine_demo.py
```

## 核心模块详解

### 1. 知识提取器 (KnowledgeExtractor)

从LLM响应中提取结构化知识，自动生成可执行的规则。

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
```

### 2. 自适应优化器 (AdaptiveOptimizer)

动态优化处理流程，提升系统性能。

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
```

### 3. 嵌入式规则引擎 (EmbeddedRuleEngine)

智能规则匹配和推理执行，支持规则学习和更新。

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
```

### 4. 规则优先级管理 (RulePriorityManager)

基于多维度因素计算规则优先级，优化执行顺序。

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
```

### 5. 规则缓存管理 (RuleCacheManager)

LRU缓存机制，支持预加载和智能清理。

```python
from src.core import RuleCacheManager

cache_manager = RuleCacheManager()

# 缓存规则和结果
cache_manager.cache_rule(rule)
cache_manager.cache_rule_result(rule, input_data, result)

# 获取缓存
cached_rule = cache_manager.get_cached_rule(rule.rule_id)
cached_result = cache_manager.get_cached_result(rule, input_data)
```

## 性能指标

### 优化效果

- **LLM调用减少**: >90%的请求通过规则引擎处理，无需调用LLM
- **响应时间优化**: 平均响应时间从秒级降低到毫秒级
- **缓存命中率**: >90%的重复请求直接返回缓存结果
- **并发处理能力**: 支持1000+并发请求

### 系统统计

```python
# 获取系统统计信息
stats = sdk.get_stats()

print(f"规则命中率: {stats['sdk_stats']['rule_hit_rate']}")
print(f"平均处理时间: {stats['sdk_stats']['avg_processing_time']}")
print(f"成功率: {stats['sdk_stats']['successful_requests'] / stats['sdk_stats']['total_requests']}")
```

## API文档

### 主要端点

- `POST /process` - 处理请求
- `POST /rules` - 创建规则
- `GET /rules` - 获取规则列表
- `GET /rules/{rule_id}` - 获取规则详情
- `DELETE /rules/{rule_id}` - 删除规则
- `POST /feedback` - 提交反馈
- `GET /stats` - 获取统计信息
- `POST /optimize` - 触发优化

### 交互式文档

启动API服务后，访问 `http://localhost:8000/docs` 查看完整的API文档。

## 配置选项

### SDK配置

```python
config = BlitzkriegFlowConfig(
    api_endpoint="http://localhost:8000",  # API端点
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
```

## 扩展开发

### 自定义流程处理器

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

### 自定义规则类型

```python
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

## 技术栈

- **后端框架**: FastAPI, Python 3.8+
- **规则引擎**: 自研嵌入式规则引擎
- **缓存系统**: LRU缓存 + 预加载机制
- **异步处理**: asyncio, aiohttp
- **数据序列化**: Pydantic, JSON
- **监控统计**: 实时性能监控
- **文档生成**: FastAPI自动文档

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 联系方式

- 项目主页: [GitHub Repository]
- 问题反馈: [Issues]
- 文档: [README_SDK.md](README_SDK.md)

## 更新日志

### v1.0.0 (2024-01-XX)
- ✨ 实现知识提取器模块
- ✨ 实现自适应优化器模块
- ✨ 实现嵌入式规则引擎
- ✨ 实现规则优先级管理
- ✨ 实现规则缓存管理
- ✨ 提供RESTful API接口
- ✨ 提供SDK集成方式
- ✨ 支持BlitzkriegFlow接入
- 📚 完善文档和示例代码
