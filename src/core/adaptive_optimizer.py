"""
自适应优化器模块
实现处理流程的动态优化、性能监控和自适应学习
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
import numpy as np
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """性能指标数据结构"""
    timestamp: float
    processing_time: float
    memory_usage: float
    cpu_usage: float
    accuracy: float
    throughput: float
    error_rate: float


@dataclass
class OptimizationStrategy:
    """优化策略数据结构"""
    strategy_id: str
    strategy_type: str  # 'pipeline', 'model', 'cache', 'resource'
    description: str
    parameters: Dict[str, Any]
    expected_improvement: float
    risk_level: float  # 0-1, 风险等级
    created_at: float
    usage_count: int = 0
    success_rate: float = 0.0


@dataclass
class ProcessingPipeline:
    """处理流程数据结构"""
    pipeline_id: str
    steps: List[Dict[str, Any]]
    performance_history: List[PerformanceMetrics] = field(default_factory=list)
    optimization_history: List[OptimizationStrategy] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)


class MetricsCollector:
    """指标收集器"""
    
    def __init__(self, history_size: int = 1000):
        self.history_size = history_size
        self.metrics_history = deque(maxlen=history_size)
        self.lock = Lock()
        
    def collect(self) -> PerformanceMetrics:
        """收集当前性能指标"""
        try:
            import psutil
            
            # 获取系统资源使用情况
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent(interval=0.1)
            
            metrics = PerformanceMetrics(
                timestamp=time.time(),
                processing_time=0.0,  # 由外部设置
                memory_usage=memory.percent,
                cpu_usage=cpu,
                accuracy=0.0,  # 由外部设置
                throughput=0.0,  # 由外部设置
                error_rate=0.0  # 由外部设置
            )
            
            with self.lock:
                self.metrics_history.append(metrics)
            
            return metrics
            
        except ImportError:
            logger.warning("psutil未安装，无法收集系统指标")
            return PerformanceMetrics(
                timestamp=time.time(),
                processing_time=0.0,
                memory_usage=0.0,
                cpu_usage=0.0,
                accuracy=0.0,
                throughput=0.0,
                error_rate=0.0
            )
        except Exception as e:
            logger.error(f"指标收集失败: {e}")
            return None
    
    def get_recent_metrics(self, count: int = 100) -> List[PerformanceMetrics]:
        """获取最近的性能指标"""
        with self.lock:
            return list(self.metrics_history)[-count:]
    
    def get_average_metrics(self, window_size: int = 100) -> Optional[PerformanceMetrics]:
        """获取平均性能指标"""
        recent_metrics = self.get_recent_metrics(window_size)
        if not recent_metrics:
            return None
        
        avg_metrics = PerformanceMetrics(
            timestamp=time.time(),
            processing_time=np.mean([m.processing_time for m in recent_metrics]),
            memory_usage=np.mean([m.memory_usage for m in recent_metrics]),
            cpu_usage=np.mean([m.cpu_usage for m in recent_metrics]),
            accuracy=np.mean([m.accuracy for m in recent_metrics]),
            throughput=np.mean([m.throughput for m in recent_metrics]),
            error_rate=np.mean([m.error_rate for m in recent_metrics])
        )
        
        return avg_metrics


class BottleneckAnalyzer:
    """瓶颈分析器"""
    
    def __init__(self):
        self.thresholds = {
            'processing_time': 1.0,  # 秒
            'memory_usage': 80.0,    # 百分比
            'cpu_usage': 80.0,       # 百分比
            'error_rate': 0.05,      # 5%
            'accuracy': 0.8          # 80%
        }
    
    def analyze_bottlenecks(self, metrics: PerformanceMetrics) -> List[str]:
        """分析性能瓶颈"""
        bottlenecks = []
        
        # 检查处理时间
        if metrics.processing_time > self.thresholds['processing_time']:
            bottlenecks.append('processing_time')
        
        # 检查内存使用
        if metrics.memory_usage > self.thresholds['memory_usage']:
            bottlenecks.append('memory_usage')
        
        # 检查CPU使用
        if metrics.cpu_usage > self.thresholds['cpu_usage']:
            bottlenecks.append('cpu_usage')
        
        # 检查错误率
        if metrics.error_rate > self.thresholds['error_rate']:
            bottlenecks.append('error_rate')
        
        # 检查准确率
        if metrics.accuracy < self.thresholds['accuracy']:
            bottlenecks.append('accuracy')
        
        return bottlenecks
    
    def get_bottleneck_severity(self, bottleneck: str, metrics: PerformanceMetrics) -> float:
        """获取瓶颈严重程度 (0-1)"""
        if bottleneck == 'processing_time':
            return min(1.0, metrics.processing_time / self.thresholds['processing_time'])
        elif bottleneck == 'memory_usage':
            return min(1.0, metrics.memory_usage / self.thresholds['memory_usage'])
        elif bottleneck == 'cpu_usage':
            return min(1.0, metrics.cpu_usage / self.thresholds['cpu_usage'])
        elif bottleneck == 'error_rate':
            return min(1.0, metrics.error_rate / self.thresholds['error_rate'])
        elif bottleneck == 'accuracy':
            return min(1.0, (1.0 - metrics.accuracy) / (1.0 - self.thresholds['accuracy']))
        else:
            return 0.0


class OptimizationTrigger:
    """优化触发器"""
    
    def __init__(self):
        self.trigger_conditions = {
            'bottleneck_count': 2,      # 瓶颈数量阈值
            'severity_threshold': 0.7,  # 严重程度阈值
            'frequency_threshold': 0.3  # 频率阈值
        }
        self.trigger_history = deque(maxlen=100)
    
    def should_optimize(self, bottlenecks: List[str], metrics: PerformanceMetrics) -> bool:
        """判断是否应该触发优化"""
        # 检查瓶颈数量
        if len(bottlenecks) >= self.trigger_conditions['bottleneck_count']:
            return True
        
        # 检查严重程度
        analyzer = BottleneckAnalyzer()
        for bottleneck in bottlenecks:
            severity = analyzer.get_bottleneck_severity(bottleneck, metrics)
            if severity >= self.trigger_conditions['severity_threshold']:
                return True
        
        # 检查频率
        recent_triggers = self._get_recent_triggers(300)  # 5分钟内
        if len(recent_triggers) / 100 >= self.trigger_conditions['frequency_threshold']:
            return True
        
        return False
    
    def _get_recent_triggers(self, time_window: int) -> List[float]:
        """获取最近的触发记录"""
        current_time = time.time()
        recent_triggers = []
        
        for trigger_time in self.trigger_history:
            if current_time - trigger_time <= time_window:
                recent_triggers.append(trigger_time)
        
        return recent_triggers
    
    def record_trigger(self):
        """记录触发事件"""
        self.trigger_history.append(time.time())


class StrategyGenerator:
    """策略生成器"""
    
    def __init__(self):
        self.strategy_templates = {
            'processing_time': self._generate_processing_time_strategies,
            'memory_usage': self._generate_memory_strategies,
            'cpu_usage': self._generate_cpu_strategies,
            'error_rate': self._generate_error_rate_strategies,
            'accuracy': self._generate_accuracy_strategies
        }
    
    def generate_optimization_strategies(self, bottlenecks: List[str], 
                                       metrics: PerformanceMetrics) -> List[OptimizationStrategy]:
        """生成优化策略"""
        strategies = []
        
        for bottleneck in bottlenecks:
            if bottleneck in self.strategy_templates:
                bottleneck_strategies = self.strategy_templates[bottleneck](metrics)
                strategies.extend(bottleneck_strategies)
        
        return strategies
    
    def _generate_processing_time_strategies(self, metrics: PerformanceMetrics) -> List[OptimizationStrategy]:
        """生成处理时间优化策略"""
        strategies = []
        
        # 策略1: 启用缓存
        strategies.append(OptimizationStrategy(
            strategy_id=f"cache_{int(time.time() * 1000)}",
            strategy_type='cache',
            description="启用结果缓存以减少重复计算",
            parameters={'cache_size': 1000, 'ttl': 3600},
            expected_improvement=0.3,
            risk_level=0.1,
            created_at=time.time()
        ))
        
        # 策略2: 模型优化
        strategies.append(OptimizationStrategy(
            strategy_id=f"model_opt_{int(time.time() * 1000)}",
            strategy_type='model',
            description="使用更轻量级的模型或模型压缩",
            parameters={'model_type': 'lightweight', 'compression_ratio': 0.5},
            expected_improvement=0.4,
            risk_level=0.3,
            created_at=time.time()
        ))
        
        return strategies
    
    def _generate_memory_strategies(self, metrics: PerformanceMetrics) -> List[OptimizationStrategy]:
        """生成内存使用优化策略"""
        strategies = []
        
        # 策略1: 内存清理
        strategies.append(OptimizationStrategy(
            strategy_id=f"memory_clean_{int(time.time() * 1000)}",
            strategy_type='resource',
            description="清理内存缓存和临时数据",
            parameters={'cleanup_interval': 300, 'max_memory': 0.7},
            expected_improvement=0.2,
            risk_level=0.1,
            created_at=time.time()
        ))
        
        # 策略2: 批处理优化
        strategies.append(OptimizationStrategy(
            strategy_id=f"batch_opt_{int(time.time() * 1000)}",
            strategy_type='pipeline',
            description="优化批处理大小以减少内存占用",
            parameters={'batch_size': 8, 'max_workers': 2},
            expected_improvement=0.25,
            risk_level=0.2,
            created_at=time.time()
        ))
        
        return strategies
    
    def _generate_cpu_strategies(self, metrics: PerformanceMetrics) -> List[OptimizationStrategy]:
        """生成CPU使用优化策略"""
        strategies = []
        
        # 策略1: 线程池优化
        strategies.append(OptimizationStrategy(
            strategy_id=f"thread_opt_{int(time.time() * 1000)}",
            strategy_type='resource',
            description="优化线程池大小以减少CPU竞争",
            parameters={'max_workers': 4, 'thread_timeout': 30},
            expected_improvement=0.2,
            risk_level=0.2,
            created_at=time.time()
        ))
        
        return strategies
    
    def _generate_error_rate_strategies(self, metrics: PerformanceMetrics) -> List[OptimizationStrategy]:
        """生成错误率优化策略"""
        strategies = []
        
        # 策略1: 重试机制
        strategies.append(OptimizationStrategy(
            strategy_id=f"retry_{int(time.time() * 1000)}",
            strategy_type='pipeline',
            description="添加重试机制以提高成功率",
            parameters={'max_retries': 3, 'retry_delay': 1.0},
            expected_improvement=0.3,
            risk_level=0.1,
            created_at=time.time()
        ))
        
        return strategies
    
    def _generate_accuracy_strategies(self, metrics: PerformanceMetrics) -> List[OptimizationStrategy]:
        """生成准确率优化策略"""
        strategies = []
        
        # 策略1: 模型融合
        strategies.append(OptimizationStrategy(
            strategy_id=f"ensemble_{int(time.time() * 1000)}",
            strategy_type='model',
            description="使用模型融合提高准确率",
            parameters={'ensemble_size': 3, 'voting_method': 'weighted'},
            expected_improvement=0.15,
            risk_level=0.4,
            created_at=time.time()
        ))
        
        return strategies


class AdaptiveOptimizer:
    """自适应优化器"""
    
    def __init__(self):
        self.performance_metrics = {}
        self.optimization_strategies = {}
        self.learning_rate = 0.1
        self.metrics_collector = MetricsCollector()
        self.bottleneck_analyzer = BottleneckAnalyzer()
        self.optimization_trigger = OptimizationTrigger()
        self.strategy_generator = StrategyGenerator()
        self.pipelines = {}
        self.lock = Lock()
        
        logger.info("自适应优化器初始化完成")
    
    def optimize_processing_pipeline(self, input_data: Dict[str, Any], 
                                   current_pipeline: ProcessingPipeline) -> ProcessingPipeline:
        """优化处理流程"""
        try:
            # 分析当前性能
            metrics = self.metrics_collector.collect()
            if metrics:
                current_pipeline.performance_history.append(metrics)
            
            # 分析瓶颈
            bottlenecks = self.bottleneck_analyzer.analyze_bottlenecks(metrics)
            
            # 预测最优流程
            optimal_pipeline = self.predict_optimal_pipeline(input_data, current_pipeline, bottlenecks)
            
            # 动态调整流程
            optimized_pipeline = self.adjust_pipeline(current_pipeline, optimal_pipeline)
            
            return optimized_pipeline
            
        except Exception as e:
            logger.error(f"流程优化失败: {e}")
            return current_pipeline
    
    def predict_optimal_pipeline(self, input_data: Dict[str, Any], 
                               current_pipeline: ProcessingPipeline,
                               bottlenecks: List[str]) -> ProcessingPipeline:
        """预测最优处理流程"""
        try:
            # 基于输入数据特征选择最优流程
            data_type = input_data.get('type', 'unknown')
            data_size = input_data.get('size', 0)
            
            # 根据数据类型和大小选择不同的处理策略
            if data_type == 'image' and data_size > 1024 * 1024:  # 大图片
                optimal_steps = self._get_large_image_pipeline()
            elif data_type == 'image':
                optimal_steps = self._get_small_image_pipeline()
            else:
                optimal_steps = self._get_default_pipeline()
            
            # 根据瓶颈调整流程
            if 'processing_time' in bottlenecks:
                optimal_steps = self._optimize_for_speed(optimal_steps)
            
            if 'memory_usage' in bottlenecks:
                optimal_steps = self._optimize_for_memory(optimal_steps)
            
            optimal_pipeline = ProcessingPipeline(
                pipeline_id=f"optimal_{int(time.time() * 1000)}",
                steps=optimal_steps
            )
            
            return optimal_pipeline
            
        except Exception as e:
            logger.error(f"最优流程预测失败: {e}")
            return current_pipeline
    
    def _get_large_image_pipeline(self) -> List[Dict[str, Any]]:
        """获取大图片处理流程"""
        return [
            {'step': 'resize', 'params': {'max_size': 1024}},
            {'step': 'feature_extraction', 'params': {'model': 'resnet50'}},
            {'step': 'clustering', 'params': {'algorithm': 'kmeans', 'n_clusters': 10}},
            {'step': 'analysis', 'params': {'depth': 'medium'}}
        ]
    
    def _get_small_image_pipeline(self) -> List[Dict[str, Any]]:
        """获取小图片处理流程"""
        return [
            {'step': 'feature_extraction', 'params': {'model': 'resnet18'}},
            {'step': 'clustering', 'params': {'algorithm': 'dbscan'}},
            {'step': 'analysis', 'params': {'depth': 'fast'}}
        ]
    
    def _get_default_pipeline(self) -> List[Dict[str, Any]]:
        """获取默认处理流程"""
        return [
            {'step': 'feature_extraction', 'params': {'model': 'resnet50'}},
            {'step': 'clustering', 'params': {'algorithm': 'kmeans'}},
            {'step': 'analysis', 'params': {'depth': 'standard'}}
        ]
    
    def _optimize_for_speed(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为速度优化流程"""
        optimized_steps = []
        
        for step in steps:
            if step['step'] == 'feature_extraction':
                # 使用更快的模型
                step['params']['model'] = 'resnet18'
            elif step['step'] == 'clustering':
                # 使用更快的聚类算法
                step['params']['algorithm'] = 'kmeans'
                step['params']['n_clusters'] = 5
            elif step['step'] == 'analysis':
                # 使用快速分析模式
                step['params']['depth'] = 'fast'
            
            optimized_steps.append(step)
        
        return optimized_steps
    
    def _optimize_for_memory(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """为内存优化流程"""
        optimized_steps = []
        
        for step in steps:
            if step['step'] == 'feature_extraction':
                # 添加内存清理
                step['params']['cleanup_memory'] = True
            elif step['step'] == 'clustering':
                # 减少聚类数量
                if 'n_clusters' in step['params']:
                    step['params']['n_clusters'] = min(step['params']['n_clusters'], 5)
            
            optimized_steps.append(step)
        
        return optimized_steps
    
    def adjust_pipeline(self, current_pipeline: ProcessingPipeline, 
                       optimal_pipeline: ProcessingPipeline) -> ProcessingPipeline:
        """调整处理流程"""
        try:
            # 计算调整幅度
            adjustment_factor = self.learning_rate
            
            # 逐步调整流程
            adjusted_steps = []
            
            for i, (current_step, optimal_step) in enumerate(
                zip(current_pipeline.steps, optimal_pipeline.steps)
            ):
                adjusted_step = self._adjust_step(current_step, optimal_step, adjustment_factor)
                adjusted_steps.append(adjusted_step)
            
            # 创建调整后的流程
            adjusted_pipeline = ProcessingPipeline(
                pipeline_id=f"adjusted_{int(time.time() * 1000)}",
                steps=adjusted_steps
            )
            
            # 记录优化历史
            current_pipeline.optimization_history.append(
                OptimizationStrategy(
                    strategy_id=f"pipeline_adjust_{int(time.time() * 1000)}",
                    strategy_type='pipeline',
                    description="流程参数调整",
                    parameters={'adjustment_factor': adjustment_factor},
                    expected_improvement=0.1,
                    risk_level=0.2,
                    created_at=time.time()
                )
            )
            
            return adjusted_pipeline
            
        except Exception as e:
            logger.error(f"流程调整失败: {e}")
            return current_pipeline
    
    def _adjust_step(self, current_step: Dict[str, Any], 
                    optimal_step: Dict[str, Any], 
                    factor: float) -> Dict[str, Any]:
        """调整单个步骤"""
        adjusted_step = current_step.copy()
        
        # 调整参数
        if 'params' in current_step and 'params' in optimal_step:
            adjusted_params = {}
            
            for key in optimal_step['params']:
                if key in current_step['params']:
                    current_val = current_step['params'][key]
                    optimal_val = optimal_step['params'][key]
                    
                    # 数值型参数进行插值
                    if isinstance(current_val, (int, float)) and isinstance(optimal_val, (int, float)):
                        adjusted_val = current_val + factor * (optimal_val - current_val)
                        adjusted_params[key] = adjusted_val
                    else:
                        # 非数值型参数直接采用最优值
                        adjusted_params[key] = optimal_val
                else:
                    # 新参数直接添加
                    adjusted_params[key] = optimal_step['params'][key]
            
            adjusted_step['params'] = adjusted_params
        
        return adjusted_step
    
    def learn_from_feedback(self, feedback: Dict[str, Any]):
        """从用户反馈中学习"""
        try:
            # 更新优化策略
            self.update_strategies(feedback)
            
            # 调整学习参数
            self.adjust_learning_rate(feedback)
            
            logger.info("从反馈中学习完成")
            
        except Exception as e:
            logger.error(f"反馈学习失败: {e}")
    
    def update_strategies(self, feedback: Dict[str, Any]):
        """更新优化策略"""
        try:
            # 根据反馈调整策略权重
            strategy_id = feedback.get('strategy_id')
            success = feedback.get('success', False)
            improvement = feedback.get('improvement', 0.0)
            
            if strategy_id in self.optimization_strategies:
                strategy = self.optimization_strategies[strategy_id]
                strategy.usage_count += 1
                
                # 更新成功率
                if success:
                    strategy.success_rate = (
                        (strategy.success_rate * (strategy.usage_count - 1) + 1.0) / 
                        strategy.usage_count
                    )
                else:
                    strategy.success_rate = (
                        (strategy.success_rate * (strategy.usage_count - 1)) / 
                        strategy.usage_count
                    )
                
                # 根据实际改进调整预期改进
                if improvement > 0:
                    strategy.expected_improvement = (
                        strategy.expected_improvement * 0.9 + improvement * 0.1
                    )
            
        except Exception as e:
            logger.error(f"策略更新失败: {e}")
    
    def adjust_learning_rate(self, feedback: Dict[str, Any]):
        """调整学习率"""
        try:
            # 根据反馈调整学习率
            performance_change = feedback.get('performance_change', 0.0)
            
            if performance_change > 0:
                # 性能提升，增加学习率
                self.learning_rate = min(0.5, self.learning_rate * 1.1)
            else:
                # 性能下降，减少学习率
                self.learning_rate = max(0.01, self.learning_rate * 0.9)
            
            logger.info(f"学习率调整为: {self.learning_rate:.3f}")
            
        except Exception as e:
            logger.error(f"学习率调整失败: {e}")
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """获取优化统计信息"""
        stats = {
            'total_strategies': len(self.optimization_strategies),
            'total_pipelines': len(self.pipelines),
            'learning_rate': self.learning_rate,
            'recent_performance': {},
            'strategy_success_rates': {},
            'bottleneck_frequency': defaultdict(int)
        }
        
        # 获取最近性能指标
        recent_metrics = self.metrics_collector.get_recent_metrics(10)
        if recent_metrics:
            avg_metrics = self.metrics_collector.get_average_metrics(10)
            if avg_metrics:
                stats['recent_performance'] = {
                    'avg_processing_time': avg_metrics.processing_time,
                    'avg_memory_usage': avg_metrics.memory_usage,
                    'avg_cpu_usage': avg_metrics.cpu_usage,
                    'avg_accuracy': avg_metrics.accuracy,
                    'avg_error_rate': avg_metrics.error_rate
                }
        
        # 获取策略成功率
        for strategy_id, strategy in self.optimization_strategies.items():
            stats['strategy_success_rates'][strategy_id] = strategy.success_rate
        
        # 获取瓶颈频率
        for metrics in recent_metrics:
            bottlenecks = self.bottleneck_analyzer.analyze_bottlenecks(metrics)
            for bottleneck in bottlenecks:
                stats['bottleneck_frequency'][bottleneck] += 1
        
        return stats 