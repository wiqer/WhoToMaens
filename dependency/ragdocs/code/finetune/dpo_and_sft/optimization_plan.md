# DPO 和 SFT 训练代码优化方案

## 一、代码审查方法论

### 1.1 静态代码分析
- **类型检查**：使用 `pyright` 进行严格的类型检查
- **代码风格**：使用 `pylint` 和 `black` 确保代码风格一致性
- **复杂度分析**：使用 `radon` 检查代码复杂度
- **依赖分析**：使用 `pipreqs` 管理依赖关系

### 1.2 动态代码分析
- **单元测试**：使用 `pytest` 进行单元测试
- **覆盖率分析**：使用 `pytest-cov` 检查测试覆盖率
- **性能分析**：使用 `cProfile` 和 `line_profiler` 进行性能分析
- **内存分析**：使用 `memory_profiler` 检查内存使用

### 1.3 代码审查清单
1. **数据预处理**
   - [ ] 字段存在性检查
   - [ ] 数据类型验证
   - [ ] 数据格式验证
   - [ ] 异常处理机制

2. **模型训练**
   - [ ] 梯度管理配置
   - [ ] 学习率调度策略
   - [ ] 显存优化策略
   - [ ] 训练状态监控

3. **模型保存**
   - [ ] 文件路径验证
   - [ ] 权限检查
   - [ ] 异常处理
   - [ ] 备份机制

## 二、典型风险示例

### 2.1 红色风险（严重）
1. **数据泄露**
   ```python
   # 错误示例
   train_dataset = dataset.shuffle(seed=42).train_test_split(test_size=0.1, seed=42)["train"]
   eval_dataset = dataset.shuffle(seed=42).train_test_split(test_size=0.1, seed=42)["test"]
   
   # 正确示例
   split_dataset = dataset.shuffle(seed=42).train_test_split(test_size=0.1, seed=42)
   train_dataset = split_dataset["train"]
   eval_dataset = split_dataset["test"]
   ```

2. **显存溢出**
   ```python
   # 错误示例
   model = AutoModelForCausalLM.from_pretrained(model_path)
   
   # 正确示例
   bnb_config = BitsAndBytesConfig(
       load_in_4bit=True,
       bnb_4bit_use_double_quant=True,
       bnb_4bit_quant_type="nf4",
       bnb_4bit_compute_dtype=torch.bfloat16
   )
   model = AutoModelForCausalLM.from_pretrained(
       model_path,
       quantization_config=bnb_config,
       device_map='auto'
   )
   ```

### 2.2 黄色风险（中等）
1. **配置参数缺失**
   ```python
   # 错误示例
   training_args = TrainingArguments(
       output_dir="output",
       learning_rate=2e-5
   )
   
   # 正确示例
   training_args = TrainingArguments(
       output_dir="output",
       learning_rate=2e-5,
       gradient_accumulation_steps=4,
       gradient_checkpointing=True,
       gradient_clipping=1.0,
       warmup_steps=100,
       logging_steps=10
   )
   ```

2. **异常处理不完整**
   ```python
   # 错误示例
   model.save_pretrained(output_dir)
   
   # 正确示例
   try:
       output_path = Path(output_dir)
       output_path.mkdir(parents=True, exist_ok=True)
       model.save_pretrained(output_path)
       logger.info(f"Model saved to {output_path}")
   except Exception as e:
       logger.error(f"Model saving failed: {str(e)}", exc_info=True)
       raise
   ```

### 2.3 蓝色风险（轻微）
1. **日志记录不完整**
   ```python
   # 错误示例
   print(f"Training started with {len(train_dataset)} examples")
   
   # 正确示例
   logger.info(
       "Training started with %d examples, batch size: %d, learning rate: %f",
       len(train_dataset),
       training_args.per_device_train_batch_size,
       training_args.learning_rate
   )
   ```

2. **代码注释不足**
   ```python
   # 错误示例
   def train_model(model, dataset):
       return model.train(dataset)
   
   # 正确示例
   def train_model(model: PreTrainedModel, dataset: Dataset) -> Dict[str, float]:
       """
       训练模型并返回训练指标
       
       Args:
           model: 预训练模型
           dataset: 训练数据集
           
       Returns:
           Dict[str, float]: 包含训练指标的字典
           
       Raises:
           ValueError: 当数据集为空时
           RuntimeError: 当训练过程中出现错误时
       """
       if len(dataset) == 0:
           raise ValueError("Dataset is empty")
       return model.train(dataset)
   ```

## 三、改进建议

### 3.1 红色改进（立即修复）
1. **数据验证增强**
   ```python
   class DataValidator:
       def __init__(self, required_fields: List[str]):
           self.required_fields = required_fields
           
       def validate(self, data: Dict) -> None:
           for field in self.required_fields:
               if field not in data:
                   raise ValueError(f"Missing required field: {field}")
   ```

2. **显存管理优化**
   ```python
   class MemoryManager:
       def __init__(self, model: PreTrainedModel):
           self.model = model
           
       def optimize(self) -> None:
           self.model.gradient_checkpointing_enable()
           torch.cuda.empty_cache()
   ```

### 3.2 黄色改进（计划修复）
1. **配置管理优化**
   ```python
   @dataclass
   class TrainingConfig:
       learning_rate: float
       batch_size: int
       gradient_accumulation_steps: int
       warmup_steps: int
       
       def validate(self) -> None:
           if self.learning_rate <= 0:
               raise ValueError("Learning rate must be positive")
   ```

2. **训练监控增强**
   ```python
   class TrainingMonitor:
       def __init__(self, log_dir: str):
           self.writer = SummaryWriter(log_dir)
           
       def log_metrics(self, metrics: Dict[str, float], step: int) -> None:
           for name, value in metrics.items():
               self.writer.add_scalar(name, value, step)
   ```

### 3.3 蓝色改进（持续优化）
1. **日志系统优化**
   ```python
   class TrainingLogger:
       def __init__(self, log_file: str):
           self.logger = logging.getLogger(__name__)
           self.setup_logger(log_file)
           
       def setup_logger(self, log_file: str) -> None:
           handler = logging.FileHandler(log_file)
           formatter = logging.Formatter(
               '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
           )
           handler.setFormatter(formatter)
           self.logger.addHandler(handler)
   ```

2. **代码文档完善**
   ```python
   class ModelTrainer:
       """
       模型训练器类，负责处理模型训练的所有相关操作
       
       Attributes:
           model: 待训练的模型
           config: 训练配置
           logger: 日志记录器
       """
       
       def __init__(self, model: PreTrainedModel, config: TrainingConfig):
           self.model = model
           self.config = config
           self.logger = TrainingLogger("training.log")
   ```

## 四、可复用检测脚本

### 4.1 数据验证脚本
```python
#!/usr/bin/env python3
"""
数据验证脚本，用于检查训练数据的完整性和正确性
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any

class DataValidator:
    def __init__(self, schema: Dict[str, Any]):
        self.schema = schema
        self.logger = logging.getLogger(__name__)
        
    def validate_file(self, file_path: Path) -> bool:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self.validate_data(data)
        except Exception as e:
            self.logger.error(f"Validation failed for {file_path}: {str(e)}")
            return False
            
    def validate_data(self, data: List[Dict]) -> bool:
        for item in data:
            if not self._validate_item(item):
                return False
        return True
        
    def _validate_item(self, item: Dict) -> bool:
        for field, rules in self.schema.items():
            if not self._check_field(item, field, rules):
                return False
        return True
```

### 4.2 性能监控脚本
```python
#!/usr/bin/env python3
"""
性能监控脚本，用于跟踪训练过程中的资源使用情况
"""

import psutil
import GPUtil
import logging
from datetime import datetime
from typing import Dict, List

class PerformanceMonitor:
    def __init__(self, log_file: str):
        self.logger = logging.getLogger(__name__)
        self.setup_logger(log_file)
        
    def log_metrics(self) -> Dict[str, float]:
        metrics = {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'gpu_utilization': self._get_gpu_metrics()
        }
        self.logger.info(f"Performance metrics: {metrics}")
        return metrics
        
    def _get_gpu_metrics(self) -> List[Dict[str, float]]:
        try:
            gpus = GPUtil.getGPUs()
            return [{
                'id': gpu.id,
                'load': gpu.load,
                'memory_used': gpu.memoryUsed,
                'memory_total': gpu.memoryTotal
            } for gpu in gpus]
        except Exception as e:
            self.logger.error(f"Failed to get GPU metrics: {str(e)}")
            return []
```

### 4.3 训练状态检查脚本
```python
#!/usr/bin/env python3
"""
训练状态检查脚本，用于监控训练进度和模型状态
"""

import torch
import logging
from pathlib import Path
from typing import Dict, Optional

class TrainingStateChecker:
    def __init__(self, model: torch.nn.Module, log_file: str):
        self.model = model
        self.logger = logging.getLogger(__name__)
        self.setup_logger(log_file)
        
    def check_state(self) -> Dict[str, Any]:
        state = {
            'gradient_norm': self._get_gradient_norm(),
            'parameter_stats': self._get_parameter_stats(),
            'optimizer_state': self._get_optimizer_state()
        }
        self.logger.info(f"Training state: {state}")
        return state
        
    def _get_gradient_norm(self) -> float:
        total_norm = 0.0
        for p in self.model.parameters():
            if p.grad is not None:
                total_norm += p.grad.data.norm(2).item() ** 2
        return total_norm ** 0.5
```

## 五、总结

本文档提供了 DPO 和 SFT 训练代码的全面优化方案，包括：
1. 详细的代码审查方法论
2. 典型风险示例及解决方案
3. 分级的改进建议
4. 可复用的检测脚本

建议按照以下顺序实施优化：
1. 首先解决红色风险问题
2. 然后处理黄色风险问题
3. 最后进行蓝色优化改进

同时，建议建立定期的代码审查机制，确保代码质量持续改进。 