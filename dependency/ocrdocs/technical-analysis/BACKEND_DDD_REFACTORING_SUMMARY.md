# 后端DDD重构总结

## 重构概述

本次重构将MaoOCR后端从单体架构重构为基于领域驱动设计(DDD)的分层架构，实现了业务与技术分离，提升了代码的可维护性和可扩展性。

## 重构前后对比

### 重构前的问题
1. **api.py文件过大**（1897行），混合了API路由、业务逻辑、数据处理
2. **document_api.py**虽然分离了，但仍包含业务逻辑
3. **缺乏清晰的领域模型**，业务规则分散在各处
4. **没有统一的状态管理和错误处理**
5. **职责边界模糊**，难以扩展和维护

### 重构后的架构
```
src/maoocr/
├── domain/                    # 领域层 - 核心业务逻辑
│   ├── document/             # 文档领域
│   │   ├── models/          # 实体
│   │   │   ├── document.py  # 文档实体
│   │   │   └── page.py      # 页面实体
│   │   ├── value_objects.py # 值对象
│   │   ├── events/          # 领域事件
│   │   └── repositories/    # 仓储接口
│   └── ocr/                 # OCR领域
│       ├── models/          # 实体
│       └── value_objects.py # 值对象
├── application/              # 应用层 - 用例协调
│   ├── document_app_service.py
│   ├── ocr_app_service.py
│   └── batch_processing_service.py
├── interfaces/               # 接口适配层 - 外部接口
│   ├── api/                 # API路由
│   │   └── document_routes.py
│   └── schemas/             # 请求响应Schema
│       └── document_schema.py
└── infrastructure/          # 基础设施层 - 技术支持
    ├── event_bus.py         # 事件总线
    ├── file_storage.py      # 文件存储
    ├── dependency_injection.py # 依赖注入
    ├── document_processors.py  # 文档处理器
    └── persistence/         # 数据持久化
        └── document_repository_impl.py
```

## 核心改进

### 1. 领域层（Domain Layer）
- **文档实体（Document）**：包含业务行为和状态管理
- **页面实体（Page）**：表示文档中的单个页面
- **值对象（Value Objects）**：不可变对象，如DocumentMetadata、ProcessingStatus
- **领域事件（Domain Events）**：DocumentUploaded、DocumentProcessed等
- **仓储接口（Repository Interface）**：抽象数据访问

### 2. 应用层（Application Layer）
- **文档应用服务（DocumentAppService）**：协调文档处理流程
- **OCR应用服务（OCRAppService）**：协调OCR处理流程
- **批量处理服务（BatchProcessingService）**：协调批量处理流程
- **不包含业务规则**，只负责用例编排

### 3. 接口适配层（Interface Layer）
- **API路由**：只负责参数校验和调用应用服务
- **Schema定义**：统一的请求响应格式
- **错误处理**：标准化的错误响应

### 4. 基础设施层（Infrastructure Layer）
- **事件总线（EventBus）**：领域事件的发布订阅
- **文件存储（FileStorage）**：文件管理服务
- **依赖注入（Dependency Injection）**：管理各层依赖
- **文档处理器工厂（DocumentProcessorFactory）**：根据文件类型创建处理器
- **仓储实现（Repository Implementation）**：具体的数据访问实现

## 关键特性

### 1. 领域事件驱动
```python
# 发布领域事件
event = DocumentUploaded(
    document_id=document.id,
    filename=filename,
    file_size=file_size,
    file_type=file_type,
    metadata=metadata
)
await self.event_bus.publish(event)
```

### 2. 依赖注入
```python
# 依赖注入配置
def get_document_app_service() -> DocumentAppService:
    return container.get_service('document_app_service')

# 在API中使用
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    app_service: DocumentAppService = Depends(get_document_app_service)
):
```

### 3. 统一错误处理
```python
# 标准化的错误响应
class ErrorResponseSchema(BaseModel):
    error: str = Field(..., description="错误信息")
    code: str = Field(..., description="错误代码")
    details: Optional[Dict[str, Any]] = Field(default=None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
```

### 4. 业务规则封装
```python
# 文档实体的业务行为
class Document:
    def can_be_processed(self) -> bool:
        """检查是否可以处理"""
        return self.status.value in ["pending", "processing"]
    
    def _update_status(self, new_state: str) -> None:
        """更新处理状态"""
        if not self.status.can_transition_to(new_state):
            raise ValueError(f"无效的状态转换: {self.status.value} → {new_state}")
        self.status = ProcessingStatus(new_state)
```

## 重构收益

### 1. 可维护性提升
- **清晰的职责分离**：每层都有明确的职责
- **业务逻辑集中**：领域层包含所有业务规则
- **易于理解**：代码结构符合业务概念

### 2. 可扩展性增强
- **新功能易添加**：通过添加领域对象而非修改现有代码
- **模块化设计**：不同模块可独立开发和部署
- **接口稳定**：领域接口稳定，实现可替换

### 3. 可测试性改善
- **单元测试友好**：领域服务独立于基础设施
- **模拟测试**：可轻松模拟外部依赖
- **集成测试**：清晰的层次结构便于测试

### 4. 团队协作优化
- **并行开发**：不同团队可并行开发不同限界上下文
- **代码规范**：统一的架构模式便于代码审查
- **知识传递**：领域模型即文档

## 使用方式

### 启动新版本API
```bash
# 启动DDD重构版API
python -m src.maoocr.api_new

# 或者使用uvicorn
uvicorn src.maoocr.api_new:app --host 0.0.0.0 --port 8000
```

### API端点
- **文档上传**：`POST /api/v2/documents/upload`
- **文档处理**：`POST /api/v2/documents/process`
- **文档列表**：`GET /api/v2/documents/`
- **文档详情**：`GET /api/v2/documents/{document_id}`
- **健康检查**：`GET /health`
- **服务状态**：`GET /api/status`

## 后续优化计划

### 1. 完善领域模型
- 添加更多业务实体和值对象
- 实现完整的领域事件系统
- 增强业务规则验证

### 2. 基础设施优化
- 实现数据库持久化
- 添加缓存层
- 集成消息队列

### 3. 监控和日志
- 添加性能监控
- 完善日志系统
- 实现分布式追踪

### 4. 测试覆盖
- 添加单元测试
- 实现集成测试
- 添加端到端测试

## 总结

本次DDD重构成功地将MaoOCR后端从单体架构转换为分层架构，实现了：

1. **业务与技术分离**：领域层专注业务规则，技术实现解耦
2. **清晰的架构边界**：四层架构职责明确，依赖关系清晰
3. **可维护性提升**：代码结构符合业务概念，易于理解和修改
4. **可扩展性增强**：新功能可通过添加领域对象实现，无需修改现有代码
5. **团队协作优化**：统一的架构模式便于团队协作和知识传递

重构后的架构为MaoOCR的长期发展奠定了坚实的基础，支持业务复杂度的持续增长。