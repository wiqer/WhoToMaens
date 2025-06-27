# 后端代码分层开发方案（DDD增强版）

## 问题分析
当前后端代码存在以下架构问题：
1. **职责边界模糊**：<mcfile name="document_api.py" path="src/maoocr/document_api.py"></mcfile>混合API路由、业务逻辑和数据处理
2. **领域逻辑缺失**：业务规则散落在API层，缺乏显式领域模型抽象
3. **扩展性受限**：现有架构难以支持复杂业务规则变更和新功能迭代

## DDD分层架构设计
基于领域驱动设计(DDD)思想，采用以下分层架构：

### 1. 领域层（核心业务逻辑）
```
src/maoocr/domain/
├── document/
│   ├── models/
│   │   ├── document.py        # 文档实体
│   │   ├── page.py            # 页面实体
│   │   └── value_objects.py   # 值对象（如DocumentMetadata、PageLayout）
│   ├── services/
│   │   ├── document_processor.py  # 文档处理领域服务
│   │   └── layout_analyzer.py     # 布局分析领域服务
│   ├── repositories/
│   │   └── document_repository.py # 仓储接口
│   └── events/
│       ├── document_uploaded.py
│       └── document_processed.py
└── ocr/
    ├── models/
    │   ├── ocr_result.py      # OCR结果实体
    │   └── correction_rule.py # 校正规则值对象
    ├── services/
    │   ├── ocr_engine.py      # OCR识别领域服务
    │   └── text_corrector.py  # 文本校正领域服务
    └── repositories/
        └── ocr_repository.py
```

### 2. 应用层
协调领域对象执行特定应用任务，不包含业务规则：
```
src/maoocr/application/
├── document_app_service.py    # 文档处理应用服务
├── ocr_app_service.py        # OCR处理应用服务
└── notification_service.py   # 通知服务
```

### 3. 接口适配层
处理外部请求与响应格式转换：
```
src/maoocr/interfaces/
├── api/
│   ├── document_routes.py    # API路由
│   ├── ocr_routes.py
│   └── schemas/
│       ├── document_schema.py
│       └── ocr_schema.py
├── cli/
│   └── commands.py           # 命令行接口
└── webhooks/
    └── document_webhooks.py  # 外部系统回调处理
```

### 4. 基础设施层
提供技术支持能力：
```
src/maoocr/infrastructure/
├── persistence/
│   ├── document_repository_impl.py
│   └── database.py           # 数据库连接
├── file_storage/
│   ├── local_storage.py      # 本地文件存储
│   └── cloud_storage.py      # 云存储适配
├── external_services/
│   ├── pdf_processor.py      # PDF处理外部服务封装
│   └── nlp_service.py        # NLP服务客户端
└── monitoring/
    ├── metrics.py            # 性能指标收集
    └── logging.py           # 日志系统
```

## DDD核心实践

### 1. 领域驱动设计关键元素
1. **限界上下文**：明确划分文档处理、OCR识别、布局分析等业务上下文
2. **聚合根**：以Document和OcrResult为核心聚合根
3. **值对象**：如DocumentMetadata、PageLayout等不可变对象
4. **领域事件**：文档上传完成、处理完成等事件的发布与订阅
5. **仓储模式**：抽象数据访问，隔离领域层与数据持久化

### 2. 领域事件实现示例
```python
# src/maoocr/domain/events/event_bus.py
from dataclasses import dataclass
from typing import Callable, Dict, List

class EventBus:
    def __init__(self):
        self.subscribers = defaultdict(list)

    def subscribe(self, event_type: str, handler: Callable):
        self.subscribers[event_type].append(handler)

    async def publish(self, event):
        event_type = event.__class__.__name__
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                await handler(event)

# 使用示例
# src/maoocr/infrastructure/event_bus_impl.py
event_bus = EventBus()

event_bus.subscribe("DocumentProcessed", notification_service.send_processed_notification)
event_bus.subscribe("DocumentProcessed", metrics_collector.record_processing_time)
```

### 3. 依赖注入配置
```python
# src/maoocr/infrastructure/dependency_injection.py
from fastapi import Depends
from ..domain.repositories import DocumentRepository
from .persistence.document_repository_impl import SqlAlchemyDocumentRepository

async def get_document_repository() -> DocumentRepository:
    return SqlAlchemyDocumentRepository()

# 在API路由中使用
@router.post("/documents")
async def create_document(
    document: DocumentCreateSchema,
    repo: DocumentRepository = Depends(get_document_repository)
):
    return await repo.create(document)
```

## 实施步骤

### 1. 迁移现有代码
1. 创建上述目录结构，按DDD原则重构现有代码
2. 提取领域模型：识别实体、值对象和聚合根
3. 实现仓储接口及其数据库实现
4. 重构API层，依赖注入领域服务

### 2. 验证与测试
1. 为核心领域服务编写单元测试
2. 添加集成测试验证跨层交互
3. 实施契约测试确保接口兼容性

## 实施收益
1. **业务与技术分离**：领域层专注业务规则，与技术实现解耦
2. **可维护性提升**：清晰的领域模型使业务逻辑更易于理解和修改
3. **可扩展性增强**：新业务功能可通过添加领域对象而非修改现有代码实现
4. **团队协作优化**：不同团队可并行开发不同限界上下文
5. **演进式架构**：支持业务复杂度增长时的架构自然演进

## 额外优化策略

### 1. 跨层一致性设计
- **统一错误模型**：在<mcfile name="error_types.py" path="src/maoocr/domain/common/error_types.py"></mcfile>中定义标准错误类型层次结构
- **标准化响应格式**：所有API返回统一格式：`{"success": bool, "data": object, "error": ErrorObject}`
- **跨层日志策略**：实现统一日志接口，确保各层日志格式一致

### 2. 自动化测试策略
```
# 测试目录结构
src/maoocr/tests/
├── domain/
│   ├── test_document_entity.py       # 领域实体单元测试
│   └── test_ocr_service.py           # 领域服务测试
├── application/
│   └── test_document_app_service.py  # 应用服务集成测试
├── interfaces/
│   └── test_api_controllers.py       # API契约测试
└── infrastructure/
    └── test_repositories.py          # 仓储实现测试
```

### 3. 模块化优化
- **子域进一步拆分**：将文档处理拆分为文档元数据管理、内容提取、格式转换等子域
- **依赖规则强化**：严格执行依赖方向（领域层不依赖外层）
- **接口稳定性**：为所有跨层接口添加版本控制和兼容性测试