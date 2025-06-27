# BugAgaric Test Coverage Plan

## 1. 测试范围

### 1.1 核心模块测试
- **数据库模块**
  - Elasticsearch 索引操作
  - Milvus 向量检索
  - PostgreSQL 数据存储
- **知识管理模块**
  - 文档处理
  - 知识提取
  - 知识对齐
- **检索增强模块**
  - 混合检索策略
  - 重排序
  - 上下文理解
- **模型微调模块**
  - 嵌入模型训练
  - LoRA 微调
  - 模型评估

### 1.2 集成测试
- API 接口测试
- 服务间通信测试
- 端到端流程测试

### 1.3 性能测试
- 并发处理能力
- 响应时间
- 资源使用效率

## 2. 测试框架

### 2.1 单元测试
- **框架**: pytest
- **覆盖率工具**: pytest-cov
- **Mock工具**: pytest-mock

### 2.2 集成测试
- **API测试**: pytest-asyncio
- **数据库测试**: pytest-postgresql
- **容器测试**: pytest-docker

### 2.3 性能测试
- **负载测试**: locust
- **基准测试**: pytest-benchmark

## 3. 测试实现

### 3.1 目录结构
```
test/
├── unit/
│   ├── test_database.py
│   ├── test_knowledge.py
│   ├── test_retrieval.py
│   └── test_finetune.py
├── integration/
│   ├── test_api.py
│   ├── test_services.py
│   └── test_workflow.py
├── performance/
│   ├── test_load.py
│   └── test_benchmark.py
└── conftest.py
```

### 3.2 测试用例示例

#### 数据库测试
```python
# test/unit/test_database.py
import pytest
from bugagaric.modules.database import ESIndex, MilvusIndex

@pytest.fixture
async def es_client():
    client = ESIndex("http://localhost:9201")
    yield client
    await client.cleanup()

async def test_es_create_index(es_client):
    result = await es_client.create("test_index")
    assert result["acknowledged"] is True

async def test_es_search(es_client):
    await es_client.insert("test_index", [{"content": "test"}])
    results = await es_client.search("test_index", "test")
    assert len(results["hits"]["hits"]) > 0
```

#### 知识管理测试
```python
# test/unit/test_knowledge.py
import pytest
from bugagaric.modules.knowledge_management import KnowledgeManager

@pytest.fixture
def knowledge_manager():
    return KnowledgeManager()

def test_document_processing(knowledge_manager):
    doc = "Test document content"
    processed = knowledge_manager.process_document(doc)
    assert processed["content"] == doc
    assert "embeddings" in processed
```

#### API测试
```python
# test/integration/test_api.py
import pytest
from fastapi.testclient import TestClient
from bugagaric.api.main import app

@pytest.fixture
def client():
    return TestClient(app)

def test_search_endpoint(client):
    response = client.post("/api/search", json={"query": "test"})
    assert response.status_code == 200
    assert "results" in response.json()
```

## 4. CI/CD 集成

### 4.1 GitHub Actions 配置
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      elasticsearch:
        image: elasticsearch:7.9.3
        ports:
          - 9201:9200
      milvus:
        image: milvusdb/milvus:latest
        ports:
          - 19530:19530
          - 19121:19121

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.8'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov pytest-asyncio pytest-mock
    - name: Run tests
      run: |
        pytest test/ --cov=bugagaric --cov-report=xml
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

### 4.2 覆盖率要求
- 单元测试覆盖率 ≥ 80%
- 集成测试覆盖率 ≥ 60%
- 关键模块覆盖率 ≥ 90%

## 5. 测试维护

### 5.1 定期检查
- 每周检查测试覆盖率报告
- 每月审查测试用例完整性
- 每季度更新测试数据

### 5.2 测试数据管理
- 使用固定测试数据集
- 定期更新测试数据
- 维护测试数据版本

### 5.3 文档更新
- 及时更新测试文档
- 记录测试用例变更
- 维护测试环境配置说明 