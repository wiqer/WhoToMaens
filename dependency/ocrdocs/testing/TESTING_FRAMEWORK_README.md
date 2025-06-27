# MaoOCR 测试框架完整指南

## 📋 目录
- [测试目标](#测试目标)
- [测试架构](#测试架构)
- [工具配置](#工具配置)
- [运行方法](#运行方法)
- [测试用例](#测试用例)
- [最佳实践](#最佳实践)
- [故障排除](#故障排除)

---

## 🎯 测试目标

### 质量目标
- **测试覆盖率**: ≥80% (整体覆盖率)
- **关键路径覆盖率**: ≥95% (核心业务逻辑)
- **测试通过率**: 100% (所有测试必须通过)
- **性能目标**: API响应时间 <2秒，前端加载时间 <3秒

### 测试类型分布
```
测试金字塔:
    E2E Tests (10%)
        /\
       /  \
   Integration Tests (20%)
      /    \
     /      \
Unit Tests (70%)
```

### 分层覆盖率要求
- **领域层**: ≥90% - 核心业务逻辑必须充分测试
- **应用层**: ≥85% - 应用服务需要高覆盖率
- **基础设施层**: ≥80% - API客户端和存储需要测试
- **UI层**: ≥75% - 组件和页面需要基本测试

---

## 🏗️ 测试架构

### 后端测试架构

#### 目录结构
```
tests/
├── unit/                    # 单元测试 (70%)
│   ├── domain/             # 领域层测试
│   │   ├── entities/       # 实体测试
│   │   ├── services/       # 领域服务测试
│   │   └── repositories/   # 仓储测试
│   ├── application/        # 应用层测试
│   │   ├── services/       # 应用服务测试
│   │   └── handlers/       # 处理器测试
│   ├── infrastructure/     # 基础设施层测试
│   │   ├── api/           # API客户端测试
│   │   ├── storage/       # 存储测试
│   │   └── external/      # 外部服务测试
│   └── interfaces/         # 接口层测试
│       ├── controllers/   # 控制器测试
│       └── middleware/    # 中间件测试
├── integration/            # 集成测试 (20%)
│   ├── api/               # API集成测试
│   ├── database/          # 数据库集成测试
│   └── external/          # 外部服务集成测试
├── e2e/                   # 端到端测试 (10%)
│   ├── workflows/         # 工作流测试
│   └── scenarios/         # 场景测试
├── performance/           # 性能测试
│   ├── load/             # 负载测试
│   └── stress/           # 压力测试
├── fixtures/              # 测试夹具
├── factories/             # 测试数据工厂
└── conftest.py           # 测试配置
```

#### 测试层次
```python
# 1. 单元测试 - 测试独立组件
def test_document_entity_creation():
    """测试文档实体创建"""
    document = Document.create("test.pdf", 1024)
    assert document.name == "test.pdf"
    assert document.size == 1024

# 2. 集成测试 - 测试组件交互
def test_document_processing_workflow():
    """测试文档处理工作流"""
    service = DocumentProcessingService()
    result = service.process_document("test.pdf")
    assert result.status == "completed"

# 3. E2E测试 - 测试完整流程
def test_full_ocr_workflow():
    """测试完整OCR工作流"""
    # 模拟用户操作
    upload_file("test.jpg")
    wait_for_processing()
    verify_result()
```

### 前端测试架构

#### 目录结构
```
web_app/src/
├── __tests__/              # 测试目录
│   ├── components/         # 组件测试
│   │   ├── common/        # 通用组件测试
│   │   ├── business/      # 业务组件测试
│   │   └── layout/        # 布局组件测试
│   ├── hooks/             # Hook测试
│   ├── services/          # 服务测试
│   ├── utils/             # 工具测试
│   └── pages/             # 页面测试
├── cypress/               # E2E测试
│   ├── e2e/              # 端到端测试
│   ├── fixtures/         # 测试数据
│   └── support/          # 支持文件
└── __mocks__/            # 模拟文件
```

#### 测试层次
```javascript
// 1. 单元测试 - 测试独立组件
describe('DocumentUploader', () => {
  it('should upload file when valid file is selected', () => {
    render(<DocumentUploader onUpload={mockHandler} />);
    fireEvent.change(screen.getByTestId('file-input'), {
      target: { files: [mockFile] }
    });
    expect(mockHandler).toHaveBeenCalledWith(mockFile);
  });
});

// 2. 集成测试 - 测试组件交互
describe('OCR Workflow', () => {
  it('should process document and display result', async () => {
    render(<OCRWorkflow />);
    // 模拟文件上传
    // 等待处理完成
    // 验证结果显示
  });
});

// 3. E2E测试 - 测试完整流程
describe('Full OCR Workflow', () => {
  it('should complete full OCR workflow', () => {
    cy.visit('/ocr');
    cy.get('[data-testid="file-upload"]').attachFile('test-image.jpg');
    cy.get('[data-testid="processing-status"]').should('contain', '处理中');
    cy.get('[data-testid="ocr-result"]').should('be.visible');
  });
});
```

---

## 🔧 工具配置

### 后端测试工具

#### 核心依赖
```bash
# 测试框架
pytest>=7.4.0              # 主要测试框架
pytest-cov>=4.1.0          # 覆盖率统计
pytest-html>=3.2.0         # HTML测试报告
pytest-asyncio>=0.21.0     # 异步测试支持
pytest-mock>=3.11.0        # Mock支持
pytest-xdist>=3.3.0        # 并行测试
pytest-timeout>=2.1.0      # 测试超时
pytest-rerunfailures>=12.0 # 失败重试

# 测试数据
factory-boy>=3.3.0         # 测试数据工厂
faker>=19.0.0              # 假数据生成

# 性能测试
locust>=2.15.0             # 负载测试
artillery>=2.0.0           # 压力测试

# 代码质量
coverage>=7.3.0            # 覆盖率工具
pylint>=2.17.0             # 代码检查
flake8>=6.0.0              # 代码风格
black>=23.0.0              # 代码格式化
isort>=5.12.0              # 导入排序
```

#### 配置文件
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=src
    --cov-report=html:htmlcov
    --cov-report=term-missing
    --cov-report=xml
    --cov-fail-under=80
    --html=reports/test-report.html
    --self-contained-html
    --junitxml=reports/junit.xml
    --maxfail=10
    --durations=10

markers =
    unit: 单元测试
    integration: 集成测试
    e2e: 端到端测试
    performance: 性能测试
    slow: 慢速测试 (>30秒)
    api: API测试
    database: 数据库测试
    external: 外部服务测试
    security: 安全测试
    smoke: 冒烟测试
    regression: 回归测试

minversion = 7.0
timeout = 300
```

### 前端测试工具

#### 核心依赖
```json
{
  "devDependencies": {
    "@testing-library/react": "^16.3.0",
    "@testing-library/jest-dom": "^6.6.3",
    "@testing-library/user-event": "^13.5.0",
    "@testing-library/react-hooks": "^8.0.1",
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "cypress": "^13.0.0",
    "@percy/cli": "^1.27.0",
    "lighthouse": "^11.0.0"
  }
}
```

#### Jest配置
```javascript
// jest.config.js
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.js',
    '!src/serviceWorker.js',
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
  },
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1',
  },
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{test,spec}.{js,jsx,ts,tsx}'
  ],
  moduleFileExtensions: ['js', 'jsx', 'ts', 'tsx', 'json'],
  testPathIgnorePatterns: ['/node_modules/', '/build/'],
  transformIgnorePatterns: [
    '/node_modules/(?!(@babel/runtime)/)'
  ]
};
```

---

## 🚀 运行方法

### 后端测试运行

#### 基础命令
```bash
# 安装测试依赖
pip install -r requirements-test.txt

# 运行所有测试
pytest

# 运行特定类型测试
pytest -m unit              # 单元测试
pytest -m integration       # 集成测试
pytest -m api               # API测试
pytest -m performance       # 性能测试

# 运行特定目录测试
pytest tests/unit/          # 单元测试
pytest tests/integration/   # 集成测试
pytest tests/e2e/           # E2E测试

# 运行特定文件测试
pytest tests/unit/test_document_entity.py
```

#### 覆盖率测试
```bash
# 生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term-missing

# 检查覆盖率阈值
pytest --cov=src --cov-fail-under=80

# 生成XML报告 (用于CI)
pytest --cov=src --cov-report=xml
```

#### 性能测试
```bash
# 运行Locust负载测试
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# 运行Artillery压力测试
artillery run tests/performance/artillery-config.yml
```

#### 并行测试
```bash
# 并行运行测试 (提高速度)
pytest -n auto

# 指定并行进程数
pytest -n 4
```

### 前端测试运行

#### 基础命令
```bash
# 安装依赖
npm install

# 运行单元测试
npm test

# 运行覆盖率测试
npm run test:coverage

# 运行E2E测试
npm run cypress:open
npm run cypress:run
```

#### 测试脚本
```json
{
  "scripts": {
    "test": "react-scripts test",
    "test:coverage": "react-scripts test --coverage --watchAll=false",
    "test:ci": "react-scripts test --coverage --watchAll=false --ci",
    "test:e2e": "cypress run",
    "test:e2e:open": "cypress open",
    "test:performance": "lighthouse http://localhost:3000"
  }
}
```

### 统一测试运行

#### 使用测试运行器
```bash
# 运行所有测试
python run_tests.py

# 运行特定类型测试
python run_tests.py --backend-only
python run_tests.py --frontend-only
python run_tests.py --integration-only

# 不安装依赖运行
python run_tests.py --no-install
```

#### CI/CD集成
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=src --cov-report=xml

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: npm ci
      - run: npm run test:ci
```

---

## 📝 测试用例

### 后端测试用例

#### 单元测试示例
```python
# tests/unit/domain/test_document_entity.py
import pytest
from src.maoocr.domain.entities.document import Document, DocumentStatus, DocumentType

class TestDocumentEntity:
    """文档实体测试"""
    
    def test_should_create_document_when_valid_data_provided(self):
        """测试提供有效数据时应该创建文档"""
        # Arrange
        name = "test.pdf"
        size = 1024
        doc_type = DocumentType.PDF
        
        # Act
        document = Document.create(name, size, doc_type)
        
        # Assert
        assert document.name == name
        assert document.size == size
        assert document.type == doc_type
        assert document.status == DocumentStatus.PENDING
        assert document.id is not None
    
    def test_should_raise_error_when_invalid_file_type(self):
        """测试无效文件类型时应该抛出错误"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="Invalid file type"):
            Document.create("test.txt", 1024, "invalid_type")
    
    def test_should_process_document_when_in_pending_status(self):
        """测试待处理状态的文档应该能够开始处理"""
        # Arrange
        document = Document.create("test.pdf", 1024)
        
        # Act
        document.process()
        
        # Assert
        assert document.status == DocumentStatus.PROCESSING
    
    def test_should_complete_document_when_processing_finished(self):
        """测试处理完成的文档应该能够标记为完成"""
        # Arrange
        document = Document.create("test.pdf", 1024)
        document.process()
        content = "识别的文本内容"
        
        # Act
        document.complete(content)
        
        # Assert
        assert document.status == DocumentStatus.COMPLETED
        assert document.content == content
```

#### 集成测试示例
```python
# tests/integration/api/test_ocr_api.py
import pytest
from fastapi.testclient import TestClient
from src.maoocr.api import app

class TestOCRAPI:
    """OCR API集成测试"""
    
    @pytest.fixture
    def client(self):
        """测试客户端"""
        return TestClient(app)
    
    def test_should_recognize_text_from_image(self, client):
        """测试应该能够从图片识别文本"""
        # Arrange
        with open("tests/fixtures/test_image.jpg", "rb") as f:
            files = {"file": ("test.jpg", f, "image/jpeg")}
            data = {"language": "zh", "accuracy": "high"}
        
        # Act
        response = client.post("/api/ocr/recognize", files=files, data=data)
        
        # Assert
        assert response.status_code == 200
        result = response.json()
        assert "text" in result
        assert "confidence" in result
        assert result["confidence"] > 0
    
    def test_should_return_error_when_invalid_file(self, client):
        """测试无效文件时应该返回错误"""
        # Arrange
        files = {"file": ("test.txt", b"invalid content", "text/plain")}
        
        # Act
        response = client.post("/api/ocr/recognize", files=files)
        
        # Assert
        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]
```

#### 性能测试示例
```python
# tests/performance/test_ocr_performance.py
import pytest
import time
from src.maoocr.application.services.ocr_service import OCRService

class TestOCRPerformance:
    """OCR性能测试"""
    
    @pytest.fixture
    def ocr_service(self):
        """OCR服务"""
        return OCRService()
    
    def test_should_process_image_within_time_limit(self, ocr_service):
        """测试应该在时间限制内处理图片"""
        # Arrange
        image_path = "tests/fixtures/performance_test_image.jpg"
        time_limit = 5.0  # 5秒
        
        # Act
        start_time = time.time()
        result = ocr_service.recognize(image_path)
        end_time = time.time()
        
        processing_time = end_time - start_time
        
        # Assert
        assert processing_time < time_limit
        assert result is not None
        assert result.confidence > 0.8
    
    @pytest.mark.performance
    def test_should_handle_concurrent_requests(self, ocr_service):
        """测试应该能够处理并发请求"""
        # Arrange
        import concurrent.futures
        image_path = "tests/fixtures/test_image.jpg"
        num_requests = 10
        
        # Act
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(ocr_service.recognize, image_path)
                for _ in range(num_requests)
            ]
            results = [future.result() for future in futures]
        
        # Assert
        assert len(results) == num_requests
        assert all(result is not None for result in results)
```

### 前端测试用例

#### 组件测试示例
```javascript
// src/components/business/OCR/__tests__/OCRResultItem.test.jsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import OCRResultItem from '../OCRResultItem';

describe('OCRResultItem', () => {
  const mockResult = {
    id: '1',
    text: '测试文本内容',
    confidence: 0.95,
    processingTime: 1.5,
    timestamp: new Date().toISOString()
  };
  
  const mockOnEdit = jest.fn();
  const mockOnDelete = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('should render OCR result correctly', () => {
    render(
      <OCRResultItem
        result={mockResult}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );
    
    expect(screen.getByText('测试文本内容')).toBeInTheDocument();
    expect(screen.getByText('95%')).toBeInTheDocument();
    expect(screen.getByText('1.5s')).toBeInTheDocument();
  });
  
  it('should call onEdit when edit button is clicked', () => {
    render(
      <OCRResultItem
        result={mockResult}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );
    
    fireEvent.click(screen.getByRole('button', { name: /编辑/i }));
    expect(mockOnEdit).toHaveBeenCalledWith(mockResult.id);
  });
  
  it('should call onDelete when delete button is clicked', () => {
    render(
      <OCRResultItem
        result={mockResult}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );
    
    fireEvent.click(screen.getByRole('button', { name: /删除/i }));
    expect(mockOnDelete).toHaveBeenCalledWith(mockResult.id);
  });
  
  it('should display confidence level with appropriate color', () => {
    render(
      <OCRResultItem
        result={mockResult}
        onEdit={mockOnEdit}
        onDelete={mockOnDelete}
      />
    );
    
    const confidenceElement = screen.getByText('95%');
    expect(confidenceElement).toHaveClass('high-confidence');
  });
});
```

#### Hook测试示例
```javascript
// src/hooks/__tests__/useOCRCache.test.js
import { renderHook, act } from '@testing-library/react-hooks';
import { useOCRCache } from '../useOCRCache';

describe('useOCRCache', () => {
  beforeEach(() => {
    // 清理缓存
    localStorage.clear();
  });
  
  it('should store and retrieve cached result', () => {
    const { result } = renderHook(() => useOCRCache());
    
    const testKey = 'test-image-hash';
    const testResult = { text: '测试文本', confidence: 0.9 };
    
    act(() => {
      result.current.setCachedResult(testKey, testResult);
    });
    
    const cachedResult = result.current.getCachedResult(testKey);
    expect(cachedResult).toEqual(testResult);
  });
  
  it('should return null for non-existent key', () => {
    const { result } = renderHook(() => useOCRCache());
    
    const cachedResult = result.current.getCachedResult('non-existent');
    expect(cachedResult).toBeNull();
  });
  
  it('should clear all cached results', () => {
    const { result } = renderHook(() => useOCRCache());
    
    // 添加一些缓存
    act(() => {
      result.current.setCachedResult('key1', { text: 'test1' });
      result.current.setCachedResult('key2', { text: 'test2' });
    });
    
    // 清理缓存
    act(() => {
      result.current.clearCache();
    });
    
    expect(result.current.getCachedResult('key1')).toBeNull();
    expect(result.current.getCachedResult('key2')).toBeNull();
  });
});
```

#### E2E测试示例
```javascript
// cypress/e2e/ocr-workflow.cy.js
describe('OCR Workflow', () => {
  beforeEach(() => {
    cy.visit('/ocr');
  });
  
  it('should complete full OCR workflow', () => {
    // 上传文件
    cy.get('[data-testid="file-upload"]')
      .attachFile('test-image.jpg');
    
    // 等待上传完成
    cy.get('[data-testid="upload-status"]')
      .should('contain', '上传完成');
    
    // 开始处理
    cy.get('[data-testid="start-processing"]')
      .click();
    
    // 等待处理完成
    cy.get('[data-testid="processing-status"]')
      .should('contain', '处理中');
    
    cy.get('[data-testid="processing-status"]')
      .should('contain', '处理完成', { timeout: 30000 });
    
    // 验证结果
    cy.get('[data-testid="ocr-result"]')
      .should('be.visible');
    
    cy.get('[data-testid="confidence-score"]')
      .should('be.greaterThan', 0.8);
    
    cy.get('[data-testid="recognized-text"]')
      .should('not.be.empty');
  });
  
  it('should handle file upload errors', () => {
    // 上传无效文件
    cy.get('[data-testid="file-upload"]')
      .attachFile('invalid-file.txt');
    
    // 验证错误信息
    cy.get('[data-testid="error-message"]')
      .should('contain', '不支持的文件类型');
  });
  
  it('should allow editing OCR results', () => {
    // 完成OCR流程
    cy.get('[data-testid="file-upload"]')
      .attachFile('test-image.jpg');
    
    cy.get('[data-testid="start-processing"]')
      .click();
    
    cy.get('[data-testid="processing-status"]')
      .should('contain', '处理完成', { timeout: 30000 });
    
    // 编辑结果
    cy.get('[data-testid="edit-result"]')
      .click();
    
    cy.get('[data-testid="text-editor"]')
      .clear()
      .type('编辑后的文本');
    
    cy.get('[data-testid="save-edit"]')
      .click();
    
    // 验证编辑结果
    cy.get('[data-testid="recognized-text"]')
      .should('contain', '编辑后的文本');
  });
});
```

---

## 🎯 最佳实践

### 测试命名规范

#### 后端测试命名
```python
# 测试类命名
class TestDocumentEntity:          # 测试文档实体
class TestOCRService:              # 测试OCR服务
class TestDocumentRepository:      # 测试文档仓储

# 测试方法命名
def test_should_create_document_when_valid_data_provided():
    """测试提供有效数据时应该创建文档"""

def test_should_raise_error_when_invalid_file_type():
    """测试无效文件类型时应该抛出错误"""

def test_should_process_document_when_in_pending_status():
    """测试待处理状态的文档应该能够开始处理"""
```

#### 前端测试命名
```javascript
// 测试套件命名
describe('DocumentUploader', () => {
  describe('when valid file is selected', () => {
    it('should upload file successfully', () => {
      // 测试逻辑
    });
  });
  
  describe('when invalid file is selected', () => {
    it('should show error message', () => {
      // 测试逻辑
    });
  });
});
```

### 测试数据管理

#### 使用工厂模式
```python
# tests/factories/document_factory.py
import factory
from src.maoocr.domain.entities.document import Document, DocumentType, DocumentStatus

class DocumentFactory(factory.Factory):
    class Meta:
        model = Document
    
    id = factory.Faker('uuid4')
    name = factory.Faker('file_name', extension='pdf')
    size = factory.Faker('random_int', min=1000, max=10000000)
    type = DocumentType.PDF
    status = DocumentStatus.PENDING
    content = None
    metadata = factory.Dict({})

class CompletedDocumentFactory(DocumentFactory):
    status = DocumentStatus.COMPLETED
    content = factory.Faker('text', max_nb_chars=200)
```

#### 使用夹具
```python
# tests/conftest.py
import pytest
from tests.factories.document_factory import DocumentFactory

@pytest.fixture
def sample_document():
    """示例文档夹具"""
    return DocumentFactory()

@pytest.fixture
def completed_document():
    """已完成文档夹具"""
    return CompletedDocumentFactory()

@pytest.fixture
def multiple_documents():
    """多个文档夹具"""
    return DocumentFactory.create_batch(5)
```

### 测试隔离

#### 使用Mock
```python
# 使用pytest-mock
def test_ocr_service_with_mock_engine(mocker):
    # Arrange
    mock_engine = mocker.Mock()
    mock_engine.recognize.return_value = {
        'text': '测试文本',
        'confidence': 0.95
    }
    
    service = OCRService(engine=mock_engine)
    
    # Act
    result = service.recognize('test.jpg')
    
    # Assert
    assert result.text == '测试文本'
    assert result.confidence == 0.95
    mock_engine.recognize.assert_called_once_with('test.jpg')
```

#### 使用测试数据库
```python
# 使用pytest-django或类似工具
@pytest.fixture
def test_db():
    """测试数据库夹具"""
    # 设置测试数据库
    # 运行迁移
    # 清理数据
    yield
    # 清理测试数据
```

### 性能测试最佳实践

#### 基准测试
```python
def test_ocr_performance_benchmark(benchmark):
    """OCR性能基准测试"""
    service = OCRService()
    
    def recognize_image():
        return service.recognize('test-image.jpg')
    
    result = benchmark(recognize_image)
    assert result is not None
```

#### 负载测试
```python
# locustfile.py
from locust import HttpUser, task, between

class OCRUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def recognize_image(self):
        with open('test-image.jpg', 'rb') as f:
            self.client.post(
                '/api/ocr/recognize',
                files={'file': f},
                data={'language': 'zh'}
            )
```

### 测试报告和监控

#### 生成测试报告
```bash
# 生成HTML报告
pytest --html=reports/test-report.html --self-contained-html

# 生成覆盖率报告
pytest --cov=src --cov-report=html:htmlcov

# 生成JUnit XML报告
pytest --junitxml=reports/junit.xml
```

#### 监控测试指标
```python
# 测试指标收集
import pytest
import time

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    item.start_time = time.time()

@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    duration = time.time() - item.start_time
    print(f"Test {item.name} took {duration:.2f} seconds")
```

---

## 🔧 故障排除

### 常见问题

#### 1. 测试依赖安装失败
```bash
# 升级pip
python -m pip install --upgrade pip

# 清理缓存
pip cache purge

# 重新安装
pip install -r requirements-test.txt --force-reinstall
```

#### 2. 测试超时
```bash
# 增加超时时间
pytest --timeout=600

# 或者在pytest.ini中配置
[tool:pytest]
timeout = 600
```

#### 3. 覆盖率报告不准确
```bash
# 确保正确配置覆盖率
pytest --cov=src --cov-report=html --cov-report=term-missing

# 检查.coveragerc配置
[run]
source = src
omit = 
    */tests/*
    */test_*
    */__pycache__/*
```

#### 4. 前端测试失败
```bash
# 清理缓存
npm run clean

# 重新安装依赖
rm -rf node_modules package-lock.json
npm install

# 检查测试环境
npm run test:ci
```

#### 5. E2E测试不稳定
```javascript
// 增加等待时间
cy.get('[data-testid="element"]', { timeout: 10000 })

// 使用重试机制
cy.get('[data-testid="element"]').should('be.visible').and('contain', 'text')
```

### 调试技巧

#### 后端测试调试
```python
# 使用pdb调试
import pdb

def test_debug_example():
    result = some_function()
    pdb.set_trace()  # 设置断点
    assert result is not None

# 使用pytest --pdb
pytest --pdb test_file.py::test_function
```

#### 前端测试调试
```javascript
// 使用debugger
it('should debug this test', () => {
  debugger; // 设置断点
  // 测试逻辑
});

// 使用screen.debug()
screen.debug(); // 打印DOM结构
```

### 性能优化

#### 测试执行优化
```bash
# 并行执行测试
pytest -n auto

# 只运行失败的测试
pytest --lf

# 运行上次失败的测试
pytest --ff
```

#### 测试数据优化
```python
# 使用工厂模式减少重复代码
document = DocumentFactory()

# 使用夹具避免重复创建
@pytest.fixture(scope="session")
def shared_data():
    return expensive_setup()
```

---

## 📚 参考资料

### 官方文档
- [pytest官方文档](https://docs.pytest.org/)
- [Jest官方文档](https://jestjs.io/docs/getting-started)
- [Cypress官方文档](https://docs.cypress.io/)
- [React Testing Library文档](https://testing-library.com/docs/react-testing-library/intro/)

### 最佳实践指南
- [测试驱动开发(TDD)](https://en.wikipedia.org/wiki/Test-driven_development)
- [行为驱动开发(BDD)](https://en.wikipedia.org/wiki/Behavior-driven_development)
- [测试金字塔](https://martinfowler.com/articles/practical-test-pyramid.html)

### 工具文档
- [pytest-cov文档](https://pytest-cov.readthedocs.io/)
- [factory-boy文档](https://factoryboy.readthedocs.io/)
- [Locust文档](https://docs.locust.io/)

---

**测试框架维护**: 🔴 高优先级

- 定期更新测试依赖
- 监控测试覆盖率趋势
- 优化测试执行时间
- 持续改进测试质量