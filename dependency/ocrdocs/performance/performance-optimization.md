# MaoOCR 性能优化指南

## 性能优化概述

MaoOCR系统采用多层次性能优化策略，从模型层面到系统层面进行全面优化，确保在各种硬件环境下都能获得最佳性能。

## 模型层面优化

### 1. 模型量化

#### INT8量化
```python
# 使用TensorRT进行INT8量化
import tensorrt as trt

def quantize_model_int8(model_path, calibration_data):
    """INT8量化模型"""
    builder = trt.Builder(TRT_LOGGER)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, TRT_LOGGER)
    
    # 解析ONNX模型
    with open(model_path, 'rb') as model:
        parser.parse(model.read())
    
    # 配置量化
    config = builder.create_builder_config()
    config.max_workspace_size = 1 << 30
    config.set_flag(trt.BuilderFlag.INT8)
    config.set_flag(trt.BuilderFlag.STRICT_TYPES)
    
    # 创建量化校准器
    config.int8_calibrator = Int8Calibrator(calibration_data)
    
    # 构建引擎
    engine = builder.build_engine(network, config)
    return engine
```

#### INT4量化 (GPTQ/AWQ)
```python
# 使用GPTQ进行INT4量化
from transformers import AutoTokenizer, AutoModelForCausalLM
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig

def quantize_model_gptq(model_name, bits=4):
    """GPTQ量化模型"""
    quantize_config = BaseQuantizeConfig(
        bits=bits,
        group_size=128,
        damp_percent=0.1,
        desc_act=False,
        static_groups=False,
        sym=True,
        true_sequential=True,
        model_name_or_path=None,
        model_file_base_name="model"
    )
    
    # 加载模型
    model = AutoGPTQForCausalLM.from_pretrained(
        model_name,
        quantize_config=quantize_config,
        device_map="auto"
    )
    
    # 量化模型
    model.quantize()
    return model
```

### 2. 模型剪枝

#### 结构化剪枝
```python
import torch
import torch.nn.utils.prune as prune

def prune_model_structured(model, pruning_ratio=0.3):
    """结构化剪枝"""
    for name, module in model.named_modules():
        if isinstance(module, torch.nn.Conv2d):
            prune.ln_structured(
                module,
                name='weight',
                amount=pruning_ratio,
                n=2,
                dim=0
            )
        elif isinstance(module, torch.nn.Linear):
            prune.ln_structured(
                module,
                name='weight',
                amount=pruning_ratio,
                n=2,
                dim=0
            )
    
    return model
```

#### 知识蒸馏
```python
class DistillationTrainer:
    def __init__(self, teacher_model, student_model, temperature=4.0):
        self.teacher_model = teacher_model
        self.student_model = student_model
        self.temperature = temperature
        self.criterion = nn.KLDivLoss()
    
    def distill_loss(self, student_output, teacher_output, labels):
        """计算蒸馏损失"""
        # 软标签损失
        soft_loss = self.criterion(
            F.log_softmax(student_output / self.temperature, dim=1),
            F.softmax(teacher_output / self.temperature, dim=1)
        )
        
        # 硬标签损失
        hard_loss = F.cross_entropy(student_output, labels)
        
        # 总损失
        total_loss = 0.7 * soft_loss + 0.3 * hard_loss
        return total_loss
```

### 3. 模型缓存

#### 内存缓存
```python
class ModelCache:
    def __init__(self, max_size=5):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
    
    def get(self, model_name):
        """获取模型"""
        if model_name in self.cache:
            # 更新访问顺序
            self.access_order.remove(model_name)
            self.access_order.append(model_name)
            return self.cache[model_name]
        return None
    
    def put(self, model_name, model):
        """缓存模型"""
        if len(self.cache) >= self.max_size:
            # 移除最久未使用的模型
            oldest = self.access_order.pop(0)
            del self.cache[oldest]
        
        self.cache[model_name] = model
        self.access_order.append(model_name)
```

#### 磁盘缓存
```python
class DiskModelCache:
    def __init__(self, cache_dir="cache/models"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def get(self, model_name):
        """从磁盘加载模型"""
        model_path = self.cache_dir / f"{model_name}.pth"
        if model_path.exists():
            return torch.load(model_path)
        return None
    
    def put(self, model_name, model):
        """保存模型到磁盘"""
        model_path = self.cache_dir / f"{model_name}.pth"
        torch.save(model, model_path)
```

## 推理层面优化

### 1. 批处理优化

#### 动态批处理
```python
class DynamicBatcher:
    def __init__(self, max_batch_size=32, timeout=5.0):
        self.max_batch_size = max_batch_size
        self.timeout = timeout
        self.batch_queue = []
        self.last_batch_time = time.time()
    
    async def add_to_batch(self, item):
        """添加项目到批处理队列"""
        self.batch_queue.append(item)
        
        # 检查是否达到批处理条件
        if (len(self.batch_queue) >= self.max_batch_size or 
            time.time() - self.last_batch_time >= self.timeout):
            return await self.process_batch()
        
        return None
    
    async def process_batch(self):
        """处理批处理"""
        if not self.batch_queue:
            return []
        
        batch = self.batch_queue.copy()
        self.batch_queue.clear()
        self.last_batch_time = time.time()
        
        # 执行批处理推理
        results = await self.inference_batch(batch)
        return results
```

#### 自适应批大小
```python
class AdaptiveBatchSize:
    def __init__(self, initial_size=8, min_size=1, max_size=64):
        self.current_size = initial_size
        self.min_size = min_size
        self.max_size = max_size
        self.performance_history = []
    
    def adjust_batch_size(self, processing_time, throughput):
        """根据性能调整批大小"""
        self.performance_history.append({
            'batch_size': self.current_size,
            'processing_time': processing_time,
            'throughput': throughput
        })
        
        # 保持最近10次记录
        if len(self.performance_history) > 10:
            self.performance_history.pop(0)
        
        # 计算平均性能
        avg_throughput = sum(p['throughput'] for p in self.performance_history) / len(self.performance_history)
        
        # 调整策略
        if throughput > avg_throughput * 1.1:
            # 性能提升，增加批大小
            self.current_size = min(self.current_size * 2, self.max_size)
        elif throughput < avg_throughput * 0.9:
            # 性能下降，减少批大小
            self.current_size = max(self.current_size // 2, self.min_size)
```

### 2. 异步处理

#### 异步推理
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

class AsyncInferenceEngine:
    def __init__(self, max_workers=4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.loop = asyncio.get_event_loop()
    
    async def inference_async(self, model, inputs):
        """异步推理"""
        # 在线程池中执行推理
        result = await self.loop.run_in_executor(
            self.executor,
            self._inference_sync,
            model,
            inputs
        )
        return result
    
    def _inference_sync(self, model, inputs):
        """同步推理（在线程池中执行）"""
        with torch.no_grad():
            return model(inputs)
```

#### 流式处理
```python
class StreamingProcessor:
    def __init__(self, chunk_size=1024):
        self.chunk_size = chunk_size
    
    async def process_stream(self, input_stream):
        """流式处理"""
        async for chunk in input_stream:
            # 处理数据块
            processed_chunk = await self.process_chunk(chunk)
            yield processed_chunk
    
    async def process_chunk(self, chunk):
        """处理单个数据块"""
        # 实现具体的数据块处理逻辑
        return chunk
```

### 3. 内存优化

#### 梯度检查点
```python
import torch.utils.checkpoint as checkpoint

def use_checkpoint(model, inputs):
    """使用梯度检查点节省内存"""
    def create_custom_forward(module):
        def custom_forward(*inputs):
            return module(*inputs)
        return custom_forward
    
    return checkpoint.checkpoint(
        create_custom_forward(model),
        inputs,
        preserve_rng_state=False
    )
```

#### 内存池管理
```python
class MemoryPool:
    def __init__(self, pool_size=1024*1024*1024):  # 1GB
        self.pool_size = pool_size
        self.allocated = 0
        self.blocks = {}
    
    def allocate(self, size):
        """分配内存块"""
        if self.allocated + size > self.pool_size:
            # 内存不足，清理一些块
            self.cleanup()
        
        if self.allocated + size <= self.pool_size:
            block_id = len(self.blocks)
            self.blocks[block_id] = size
            self.allocated += size
            return block_id
        
        return None
    
    def deallocate(self, block_id):
        """释放内存块"""
        if block_id in self.blocks:
            self.allocated -= self.blocks[block_id]
            del self.blocks[block_id]
    
    def cleanup(self):
        """清理内存"""
        # 实现内存清理逻辑
        pass
```

## 系统层面优化

### 1. 多GPU优化

#### 数据并行
```python
import torch.nn.parallel as parallel

def setup_data_parallel(model, device_ids):
    """设置数据并行"""
    if len(device_ids) > 1:
        model = parallel.DataParallel(model, device_ids=device_ids)
    return model
```

#### 模型并行
```python
def setup_model_parallel(model, device_ids):
    """设置模型并行"""
    if len(device_ids) > 1:
        # 将模型分割到多个GPU
        model = parallel.DistributedDataParallel(model, device_ids=device_ids)
    return model
```

#### 流水线并行
```python
class PipelineParallel:
    def __init__(self, model, num_stages, device_ids):
        self.num_stages = num_stages
        self.device_ids = device_ids
        self.stages = self.split_model(model)
    
    def split_model(self, model):
        """分割模型为多个阶段"""
        stages = []
        layers_per_stage = len(model) // self.num_stages
        
        for i in range(self.num_stages):
            start_idx = i * layers_per_stage
            end_idx = (i + 1) * layers_per_stage if i < self.num_stages - 1 else len(model)
            
            stage = nn.Sequential(*list(model.children())[start_idx:end_idx])
            stage.to(self.device_ids[i])
            stages.append(stage)
        
        return stages
    
    def forward(self, inputs):
        """流水线前向传播"""
        current_input = inputs
        
        for stage in self.stages:
            current_input = stage(current_input)
        
        return current_input
```

### 2. 负载均衡

#### 动态负载均衡
```python
class LoadBalancer:
    def __init__(self, workers):
        self.workers = workers
        self.worker_loads = {worker: 0 for worker in workers}
        self.worker_capacities = {worker: 1.0 for worker in workers}
    
    def select_worker(self, task_size):
        """选择负载最低的工作节点"""
        available_workers = [
            worker for worker in self.workers
            if self.worker_loads[worker] + task_size <= self.worker_capacities[worker]
        ]
        
        if not available_workers:
            return None
        
        # 选择负载最低的工作节点
        selected_worker = min(
            available_workers,
            key=lambda w: self.worker_loads[w]
        )
        
        # 更新负载
        self.worker_loads[selected_worker] += task_size
        return selected_worker
    
    def update_worker_capacity(self, worker, capacity):
        """更新工作节点容量"""
        self.worker_capacities[worker] = capacity
```

### 3. 缓存优化

#### 多级缓存
```python
class MultiLevelCache:
    def __init__(self):
        self.l1_cache = {}  # 内存缓存
        self.l2_cache = {}  # 磁盘缓存
        self.l3_cache = {}  # 分布式缓存
    
    def get(self, key):
        """多级缓存查找"""
        # L1缓存查找
        if key in self.l1_cache:
            return self.l1_cache[key]
        
        # L2缓存查找
        if key in self.l2_cache:
            value = self.l2_cache[key]
            self.l1_cache[key] = value  # 提升到L1
            return value
        
        # L3缓存查找
        if key in self.l3_cache:
            value = self.l3_cache[key]
            self.l2_cache[key] = value  # 提升到L2
            return value
        
        return None
    
    def put(self, key, value):
        """多级缓存存储"""
        self.l1_cache[key] = value
        self.l2_cache[key] = value
        self.l3_cache[key] = value
```

## 监控和调优

### 1. 性能监控

#### 实时性能监控
```python
class PerformanceMonitor:
    def __init__(self):
        self.metrics = {}
        self.history = []
    
    def record_metric(self, name, value, timestamp=None):
        """记录性能指标"""
        if timestamp is None:
            timestamp = time.time()
        
        if name not in self.metrics:
            self.metrics[name] = []
        
        self.metrics[name].append({
            'value': value,
            'timestamp': timestamp
        })
        
        # 保持最近1000个数据点
        if len(self.metrics[name]) > 1000:
            self.metrics[name] = self.metrics[name][-1000:]
    
    def get_average(self, name, window=100):
        """获取平均性能指标"""
        if name not in self.metrics:
            return 0
        
        recent_metrics = self.metrics[name][-window:]
        if not recent_metrics:
            return 0
        
        return sum(m['value'] for m in recent_metrics) / len(recent_metrics)
    
    def get_trend(self, name, window=100):
        """获取性能趋势"""
        if name not in self.metrics:
            return 0
        
        recent_metrics = self.metrics[name][-window:]
        if len(recent_metrics) < 2:
            return 0
        
        # 计算线性回归斜率
        x = [m['timestamp'] for m in recent_metrics]
        y = [m['value'] for m in recent_metrics]
        
        slope = self.calculate_slope(x, y)
        return slope
```

### 2. 自动调优

#### 自动参数调优
```python
class AutoTuner:
    def __init__(self, target_metric='throughput'):
        self.target_metric = target_metric
        self.parameter_space = {
            'batch_size': [1, 2, 4, 8, 16, 32],
            'num_workers': [1, 2, 4, 8],
            'cache_size': [100, 500, 1000, 2000]
        }
        self.best_config = None
        self.best_score = 0
    
    def optimize(self, model, dataset):
        """自动优化参数"""
        for batch_size in self.parameter_space['batch_size']:
            for num_workers in self.parameter_space['num_workers']:
                for cache_size in self.parameter_space['cache_size']:
                    config = {
                        'batch_size': batch_size,
                        'num_workers': num_workers,
                        'cache_size': cache_size
                    }
                    
                    # 测试配置
                    score = self.evaluate_config(model, dataset, config)
                    
                    if score > self.best_score:
                        self.best_score = score
                        self.best_config = config
        
        return self.best_config
    
    def evaluate_config(self, model, dataset, config):
        """评估配置性能"""
        # 实现配置评估逻辑
        return 0.0
```

## 最佳实践

### 1. 开发阶段优化

- **使用性能分析工具**: cProfile, line_profiler, memory_profiler
- **及早进行性能测试**: 在开发早期就进行性能基准测试
- **优化关键路径**: 识别和优化性能瓶颈
- **使用异步编程**: 充分利用异步I/O提高并发性能

### 2. 部署阶段优化

- **选择合适的硬件**: 根据需求选择合适的GPU和CPU
- **优化系统配置**: 调整操作系统参数以获得最佳性能
- **使用容器化**: 使用Docker等容器技术确保环境一致性
- **监控生产环境**: 持续监控生产环境性能指标

### 3. 运维阶段优化

- **定期性能评估**: 定期评估系统性能并进行优化
- **容量规划**: 根据业务增长进行容量规划
- **故障预防**: 建立故障预防和快速恢复机制
- **持续优化**: 根据实际使用情况持续优化系统性能