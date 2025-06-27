# KBAlign模块优化实现计划

## 一、优化目标

### 1.1 核心目标
1. **代码质量提升**
   - 修复类名拼写错误
   - 添加完整的类型注解
   - 规范化异常处理
   - 提高代码可读性

2. **性能优化**
   - 减少响应时间（目标：<100ms）
   - 降低内存使用（目标：<1GB）
   - 提升并发能力（目标：>100 QPS）

3. **稳定性提升**
   - 完善错误处理
   - 添加监控告警
   - 实现优雅降级

### 1.2 具体指标
- 响应时间：<100ms
- 内存使用：<1GB
- CPU使用率：<60%
- 错误率：<0.1%

## 二、实现步骤

### 2.1 准备阶段（1周）

1. **环境准备**
```python
# 创建测试环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

2. **测试用例编写**
```python
# tests/test_kbalign.py
import pytest
from bugagaric.modules.kbalign import KBAlign

def test_kbalign_initialization():
    # 测试初始化
    pass

def test_kbalign_arun():
    # 测试异步运行
    pass

def test_error_handling():
    # 测试错误处理
    pass
```

### 2.2 实现阶段（2周）

1. **代码重构**
```python
# bugagaric/modules/kbalign/kbalign.py
from typing import AsyncGenerator, Dict, List, Optional, Union
from pathlib import Path
from loguru import logger
from pydantic import BaseModel

class KBAlignConfig(BaseModel):
    """KBAlign配置类"""
    prompt_file: str = ""
    stream: bool = True
    system_prompt: Optional[str] = None
    batch_size: int = 32
    max_retries: int = 3

class KBAlign:
    def __init__(
        self,
        retriever: Callable,
        generator: Callable,
        config: Optional[KBAlignConfig] = None
    ) -> None:
        """
        初始化KBAlign模块
        
        Args:
            retriever: 检索函数
            generator: 生成函数
            config: 配置对象
        """
        self.config = config or KBAlignConfig()
        self._validate_callables(retriever, generator)
        self.retriever = retriever
        self.generator = generator
        self.prompt = self._load_prompt()
        
    def _validate_callables(self, retriever: Callable, generator: Callable) -> None:
        """验证可调用对象"""
        if not callable(retriever):
            raise ValueError("retriever must be callable")
        if not callable(generator):
            raise ValueError("generator must be callable")
            
    async def arun(
        self,
        query: str,
        collection: str,
        messages: List[Dict[str, str]],
        topn: int
    ) -> AsyncGenerator[Dict[str, Union[str, List[str]]], None]:
        """
        异步运行知识对齐
        
        Args:
            query: 查询文本
            collection: 集合名称
            messages: 历史消息
            topn: 返回结果数量
            
        Yields:
            包含状态和值的字典
        """
        try:
            # 第一次检索
            top_docs = await self._retrieve_with_retry(query, topn)
            yield {"state": "recall", "value": [doc.content for doc in top_docs]}
            
            # 生成第一次回答
            first_response = await self._generate_response(query, messages, top_docs)
            yield {"state": "first_answer", "value": first_response}
            
            # 第二次检索
            expanded_query = f"{query}{first_response}"
            top_docs2 = await self._retrieve_with_retry(expanded_query, topn)
            yield {"state": "query_expansion_recall", "value": [doc.content for doc in top_docs2]}
            
            # 生成最终回答
            final_response = await self._generate_final_response(
                query, messages, top_docs2
            )
            async for item in final_response:
                yield {"state": "data", "value": item}
                
        except Exception as e:
            logger.error(f"Error in arun: {str(e)}")
            yield {"state": "error", "value": str(e)}
```

2. **配置管理**
```python
# bugagaric/config/kbalign_config.py
from pydantic import BaseModel
from typing import Optional

class KBAlignConfig(BaseModel):
    """KBAlign配置类"""
    model_path: str
    batch_size: int = 32
    max_retries: int = 3
    timeout: int = 30
    cache_size: int = 1000
```

3. **错误处理**
```python
# bugagaric/modules/kbalign/exceptions.py
class KBAlignError(Exception):
    """KBAlign基础异常类"""
    pass

class RetrievalError(KBAlignError):
    """检索错误"""
    pass

class GenerationError(KBAlignError):
    """生成错误"""
    pass
```

### 2.3 验证阶段（1周）

1. **性能测试**
```python
# tests/performance/test_kbalign_performance.py
import asyncio
import time
from bugagaric.modules.kbalign import KBAlign

async def test_performance():
    # 测试响应时间
    start_time = time.time()
    # 执行测试
    end_time = time.time()
    assert end_time - start_time < 0.1  # 100ms
```

2. **压力测试**
```python
# tests/stress/test_kbalign_stress.py
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def test_concurrent_requests():
    # 测试并发请求
    pass
```

## 三、回滚计划

### 3.1 代码回滚
```bash
# 回滚到指定版本
git checkout <version_tag>

# 恢复配置
python scripts/restore_config.py

# 重启服务
python scripts/restart_server.py
```

### 3.2 数据回滚
```python
# 恢复数据
python scripts/restore_data.py --backup_dir <backup_path>
```

## 四、监控方案

### 4.1 性能监控
```python
# bugagaric/monitoring/kbalign_monitor.py
from prometheus_client import Counter, Histogram
import time

class KBAlignMonitor:
    def __init__(self):
        self.request_count = Counter(
            'kbalign_requests_total',
            'Total number of KBAlign requests'
        )
        self.response_time = Histogram(
            'kbalign_response_time_seconds',
            'Response time in seconds'
        )
```

### 4.2 资源监控
```python
# bugagaric/monitoring/resource_monitor.py
import psutil

def monitor_resources():
    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    if cpu_percent > 60 or memory.percent > 80:
        logger.warning("High resource usage detected")
```

## 五、文档更新

### 5.1 API文档
```markdown
# KBAlign API文档

## 初始化
```python
from bugagaric.modules.kbalign import KBAlign, KBAlignConfig

config = KBAlignConfig(
    model_path="path/to/model",
    batch_size=32
)
kbalign = KBAlign(retriever, generator, config)
```

## 使用方法
```python
async for result in kbalign.arun(query, collection, messages, topn):
    print(result)
```
```

### 5.2 部署指南
```markdown
# KBAlign部署指南

## 环境要求
- Python 3.8+
- CUDA 11.0+
- 8GB+ RAM

## 安装步骤
1. 安装依赖
2. 配置环境变量
3. 启动服务
```

## 六、后续规划

### 6.1 短期目标
1. 完善单元测试覆盖
2. 优化监控系统
3. 更新文档

### 6.2 长期目标
1. 支持分布式部署
2. 提升算法效率
3. 扩展功能模块 