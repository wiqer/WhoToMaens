"""
规则优先级管理模块
实现规则优先级计算、排序优化、使用统计和上下文相关性评估
"""

import time
import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import logging
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass
class PriorityFactors:
    """优先级因子"""
    usage_frequency: float = 0.0      # 使用频率
    success_rate: float = 0.0         # 成功率
    recency: float = 0.0              # 最近使用时间
    complexity: float = 0.0            # 规则复杂度
    context_relevance: float = 0.0    # 上下文相关性
    user_feedback: float = 0.0        # 用户反馈
    performance_score: float = 0.0    # 性能评分


@dataclass
class PriorityWeights:
    """优先级权重配置"""
    usage_frequency_weight: float = 0.25
    success_rate_weight: float = 0.20
    recency_weight: float = 0.15
    complexity_weight: float = 0.10
    context_relevance_weight: float = 0.15
    user_feedback_weight: float = 0.10
    performance_score_weight: float = 0.05


@dataclass
class RuleUsageRecord:
    """规则使用记录"""
    rule_id: str
    timestamp: float
    success: bool
    execution_time: float
    context_keys: List[str]
    input_size: int
    output_size: int


@dataclass
class ContextProfile:
    """上下文配置文件"""
    context_id: str
    context_keys: List[str]
    rule_usage: Dict[str, int]  # rule_id -> usage_count
    last_updated: float
    relevance_scores: Dict[str, float] = field(default_factory=dict)  # rule_id -> relevance_score


class UsageTracker:
    """使用跟踪器"""
    
    def __init__(self, max_records: int = 10000):
        self.usage_records: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_records))
        self.lock = Lock()
    
    def record_usage(self, rule_id: str, success: bool, execution_time: float, 
                    context_keys: List[str], input_size: int, output_size: int):
        """记录规则使用情况"""
        record = RuleUsageRecord(
            rule_id=rule_id,
            timestamp=time.time(),
            success=success,
            execution_time=execution_time,
            context_keys=context_keys,
            input_size=input_size,
            output_size=output_size
        )
        
        with self.lock:
            self.usage_records[rule_id].append(record)
    
    def get_usage_stats(self, rule_id: str, time_window: float = 3600) -> Dict[str, Any]:
        """获取使用统计"""
        with self.lock:
            records = self.usage_records.get(rule_id, [])
        
        if not records:
            return {
                'total_usage': 0,
                'success_count': 0,
                'success_rate': 0.0,
                'avg_execution_time': 0.0,
                'recent_usage': 0,
                'usage_frequency': 0.0
            }
        
        # 过滤时间窗口内的记录
        current_time = time.time()
        recent_records = [r for r in records if current_time - r.timestamp <= time_window]
        
        total_usage = len(records)
        success_count = sum(1 for r in records if r.success)
        success_rate = success_count / total_usage if total_usage > 0 else 0.0
        avg_execution_time = sum(r.execution_time for r in records) / total_usage if total_usage > 0 else 0.0
        recent_usage = len(recent_records)
        usage_frequency = recent_usage / (time_window / 3600) if time_window > 0 else 0.0  # 每小时使用次数
        
        return {
            'total_usage': total_usage,
            'success_count': success_count,
            'success_rate': success_rate,
            'avg_execution_time': avg_execution_time,
            'recent_usage': recent_usage,
            'usage_frequency': usage_frequency
        }
    
    def get_all_usage_stats(self, time_window: float = 3600) -> Dict[str, Dict[str, Any]]:
        """获取所有规则的使用统计"""
        stats = {}
        with self.lock:
            for rule_id in self.usage_records:
                stats[rule_id] = self.get_usage_stats(rule_id, time_window)
        return stats


class ComplexityAnalyzer:
    """复杂度分析器"""
    
    def __init__(self):
        self.complexity_factors = {
            'condition_count': 0.3,
            'action_count': 0.2,
            'nested_depth': 0.2,
            'pattern_complexity': 0.15,
            'data_dependencies': 0.15
        }
    
    def analyze_complexity(self, rule: Any) -> float:
        """分析规则复杂度"""
        try:
            # 条件数量
            condition_count = len(rule.conditions) if hasattr(rule, 'conditions') else 0
            condition_score = min(condition_count / 10.0, 1.0)  # 归一化到0-1
            
            # 动作数量
            action_count = len(rule.actions) if hasattr(rule, 'actions') else 0
            action_score = min(action_count / 5.0, 1.0)  # 归一化到0-1
            
            # 嵌套深度（简化计算）
            nested_depth = self._calculate_nested_depth(rule)
            nested_score = min(nested_depth / 5.0, 1.0)
            
            # 模式复杂度
            pattern_complexity = self._analyze_pattern_complexity(rule)
            
            # 数据依赖
            data_dependencies = self._analyze_data_dependencies(rule)
            
            # 计算综合复杂度
            complexity = (
                condition_score * self.complexity_factors['condition_count'] +
                action_score * self.complexity_factors['action_count'] +
                nested_score * self.complexity_factors['nested_depth'] +
                pattern_complexity * self.complexity_factors['pattern_complexity'] +
                data_dependencies * self.complexity_factors['data_dependencies']
            )
            
            return min(complexity, 1.0)
            
        except Exception as e:
            logger.error(f"复杂度分析失败: {e}")
            return 0.5  # 默认中等复杂度
    
    def _calculate_nested_depth(self, rule: Any) -> int:
        """计算嵌套深度"""
        # 简化实现，实际应该分析规则结构
        return 1
    
    def _analyze_pattern_complexity(self, rule: Any) -> float:
        """分析模式复杂度"""
        # 简化实现
        return 0.5
    
    def _analyze_data_dependencies(self, rule: Any) -> float:
        """分析数据依赖"""
        # 简化实现
        return 0.5


class ContextRelevanceAnalyzer:
    """上下文相关性分析器"""
    
    def __init__(self):
        self.context_profiles: Dict[str, ContextProfile] = {}
        self.lock = Lock()
    
    def update_context_profile(self, context_id: str, context_keys: List[str], 
                             rule_id: str, success: bool):
        """更新上下文配置文件"""
        with self.lock:
            if context_id not in self.context_profiles:
                self.context_profiles[context_id] = ContextProfile(
                    context_id=context_id,
                    context_keys=context_keys,
                    rule_usage={},
                    last_updated=time.time()
                )
            
            profile = self.context_profiles[context_id]
            profile.rule_usage[rule_id] = profile.rule_usage.get(rule_id, 0) + 1
            profile.last_updated = time.time()
    
    def calculate_relevance(self, rule_id: str, context_keys: List[str]) -> float:
        """计算上下文相关性"""
        with self.lock:
            total_relevance = 0.0
            profile_count = 0
            
            for profile in self.context_profiles.values():
                if rule_id in profile.rule_usage:
                    # 计算上下文键的重叠度
                    overlap = len(set(context_keys) & set(profile.context_keys))
                    total_keys = len(set(context_keys) | set(profile.context_keys))
                    
                    if total_keys > 0:
                        similarity = overlap / total_keys
                        usage_weight = min(profile.rule_usage[rule_id] / 10.0, 1.0)  # 归一化使用次数
                        relevance = similarity * usage_weight
                        total_relevance += relevance
                        profile_count += 1
            
            if profile_count > 0:
                return total_relevance / profile_count
            else:
                return 0.0
    
    def get_context_suggestions(self, context_keys: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """获取上下文建议"""
        suggestions = []
        
        with self.lock:
            for profile in self.context_profiles.values():
                overlap = len(set(context_keys) & set(profile.context_keys))
                if overlap > 0:
                    similarity = overlap / len(set(context_keys) | set(profile.context_keys))
                    
                    for rule_id, usage_count in profile.rule_usage.items():
                        score = similarity * min(usage_count / 10.0, 1.0)
                        suggestions.append((rule_id, score))
        
        # 按分数排序并返回top_k
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return suggestions[:top_k]


class PerformanceScorer:
    """性能评分器"""
    
    def __init__(self):
        self.performance_thresholds = {
            'execution_time': 1.0,  # 秒
            'memory_usage': 100,    # MB
            'throughput': 100       # 请求/秒
        }
    
    def calculate_performance_score(self, execution_time: float, memory_usage: float = 0, 
                                  throughput: float = 0) -> float:
        """计算性能评分"""
        try:
            # 执行时间评分（越短越好）
            time_score = max(0, 1 - execution_time / self.performance_thresholds['execution_time'])
            
            # 内存使用评分（越少越好）
            memory_score = max(0, 1 - memory_usage / self.performance_thresholds['memory_usage'])
            
            # 吞吐量评分（越高越好）
            throughput_score = min(1, throughput / self.performance_thresholds['throughput'])
            
            # 综合评分
            performance_score = (time_score * 0.5 + memory_score * 0.3 + throughput_score * 0.2)
            
            return min(performance_score, 1.0)
            
        except Exception as e:
            logger.error(f"性能评分计算失败: {e}")
            return 0.5  # 默认中等性能


class RulePriorityManager:
    """规则优先级管理器"""
    
    def __init__(self, weights: Optional[PriorityWeights] = None):
        self.weights = weights or PriorityWeights()
        self.usage_tracker = UsageTracker()
        self.complexity_analyzer = ComplexityAnalyzer()
        self.context_analyzer = ContextRelevanceAnalyzer()
        self.performance_scorer = PerformanceScorer()
        self.user_feedback: Dict[str, float] = {}  # rule_id -> feedback_score
        self.lock = Lock()
    
    def calculate_priority(self, rule: Any, context_keys: List[str] = None) -> float:
        """计算规则优先级"""
        try:
            rule_id = getattr(rule, 'rule_id', str(id(rule)))
            context_keys = context_keys or []
            
            # 获取使用统计
            usage_stats = self.usage_tracker.get_usage_stats(rule_id)
            
            # 计算各个因子
            factors = PriorityFactors()
            
            # 使用频率
            factors.usage_frequency = min(usage_stats['usage_frequency'] / 10.0, 1.0)
            
            # 成功率
            factors.success_rate = usage_stats['success_rate']
            
            # 最近使用时间
            factors.recency = self._calculate_recency(rule_id)
            
            # 复杂度
            factors.complexity = 1.0 - self.complexity_analyzer.analyze_complexity(rule)  # 复杂度越低优先级越高
            
            # 上下文相关性
            factors.context_relevance = self.context_analyzer.calculate_relevance(rule_id, context_keys)
            
            # 用户反馈
            factors.user_feedback = self.user_feedback.get(rule_id, 0.5)
            
            # 性能评分
            factors.performance_score = self.performance_scorer.calculate_performance_score(
                usage_stats['avg_execution_time']
            )
            
            # 计算综合优先级
            priority = (
                factors.usage_frequency * self.weights.usage_frequency_weight +
                factors.success_rate * self.weights.success_rate_weight +
                factors.recency * self.weights.recency_weight +
                factors.complexity * self.weights.complexity_weight +
                factors.context_relevance * self.weights.context_relevance_weight +
                factors.user_feedback * self.weights.user_feedback_weight +
                factors.performance_score * self.weights.performance_score_weight
            )
            
            return min(priority, 1.0)
            
        except Exception as e:
            logger.error(f"优先级计算失败: {e}")
            return 0.5  # 默认中等优先级
    
    def record_rule_execution(self, rule_id: str, success: bool, execution_time: float,
                            context_keys: List[str], input_size: int, output_size: int):
        """记录规则执行"""
        self.usage_tracker.record_usage(rule_id, success, execution_time, 
                                      context_keys, input_size, output_size)
        
        # 更新上下文配置文件
        context_id = self._generate_context_id(context_keys)
        self.context_analyzer.update_context_profile(context_id, context_keys, rule_id, success)
    
    def update_user_feedback(self, rule_id: str, feedback_score: float):
        """更新用户反馈"""
        with self.lock:
            self.user_feedback[rule_id] = max(0.0, min(1.0, feedback_score))
    
    def optimize_rule_order(self, rules: List[Any], context_keys: List[str] = None) -> List[Any]:
        """优化规则顺序"""
        try:
            # 计算每个规则的优先级
            rule_priorities = []
            for rule in rules:
                priority = self.calculate_priority(rule, context_keys)
                rule_priorities.append((rule, priority))
            
            # 按优先级排序
            rule_priorities.sort(key=lambda x: x[1], reverse=True)
            
            # 返回排序后的规则
            return [rule for rule, priority in rule_priorities]
            
        except Exception as e:
            logger.error(f"规则顺序优化失败: {e}")
            return rules  # 返回原始顺序
    
    def get_priority_analysis(self, rule: Any, context_keys: List[str] = None) -> Dict[str, Any]:
        """获取优先级分析详情"""
        try:
            rule_id = getattr(rule, 'rule_id', str(id(rule)))
            context_keys = context_keys or []
            
            usage_stats = self.usage_tracker.get_usage_stats(rule_id)
            
            factors = PriorityFactors()
            factors.usage_frequency = min(usage_stats['usage_frequency'] / 10.0, 1.0)
            factors.success_rate = usage_stats['success_rate']
            factors.recency = self._calculate_recency(rule_id)
            factors.complexity = 1.0 - self.complexity_analyzer.analyze_complexity(rule)
            factors.context_relevance = self.context_analyzer.calculate_relevance(rule_id, context_keys)
            factors.user_feedback = self.user_feedback.get(rule_id, 0.5)
            factors.performance_score = self.performance_scorer.calculate_performance_score(
                usage_stats['avg_execution_time']
            )
            
            priority = self.calculate_priority(rule, context_keys)
            
            return {
                'rule_id': rule_id,
                'priority': priority,
                'factors': {
                    'usage_frequency': factors.usage_frequency,
                    'success_rate': factors.success_rate,
                    'recency': factors.recency,
                    'complexity': factors.complexity,
                    'context_relevance': factors.context_relevance,
                    'user_feedback': factors.user_feedback,
                    'performance_score': factors.performance_score
                },
                'weights': {
                    'usage_frequency_weight': self.weights.usage_frequency_weight,
                    'success_rate_weight': self.weights.success_rate_weight,
                    'recency_weight': self.weights.recency_weight,
                    'complexity_weight': self.weights.complexity_weight,
                    'context_relevance_weight': self.weights.context_relevance_weight,
                    'user_feedback_weight': self.weights.user_feedback_weight,
                    'performance_score_weight': self.weights.performance_score_weight
                },
                'usage_stats': usage_stats
            }
            
        except Exception as e:
            logger.error(f"优先级分析失败: {e}")
            return {}
    
    def get_context_suggestions(self, context_keys: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """获取上下文建议"""
        return self.context_analyzer.get_context_suggestions(context_keys, top_k)
    
    def _calculate_recency(self, rule_id: str, time_window: float = 86400) -> float:
        """计算最近使用时间因子"""
        try:
            usage_stats = self.usage_tracker.get_usage_stats(rule_id, time_window)
            recent_usage = usage_stats['recent_usage']
            
            if recent_usage == 0:
                return 0.0
            
            # 使用对数函数计算最近性，避免过度偏向最近使用的规则
            recency = math.log(recent_usage + 1) / math.log(10)
            return min(recency, 1.0)
            
        except Exception as e:
            logger.error(f"最近性计算失败: {e}")
            return 0.0
    
    def _generate_context_id(self, context_keys: List[str]) -> str:
        """生成上下文ID"""
        return "_".join(sorted(context_keys)) if context_keys else "default"
    
    def get_manager_stats(self) -> Dict[str, Any]:
        """获取管理器统计信息"""
        with self.lock:
            total_rules = len(self.usage_tracker.usage_records)
            total_contexts = len(self.context_analyzer.context_profiles)
            total_feedback = len(self.user_feedback)
            
            return {
                'total_tracked_rules': total_rules,
                'total_context_profiles': total_contexts,
                'total_user_feedback': total_feedback,
                'usage_tracker_stats': self.usage_tracker.get_all_usage_stats()
            } 