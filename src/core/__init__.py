"""
核心模块导出
包含知识提取器、自适应优化器、规则引擎、优先级管理、缓存管理等核心组件
"""

# 知识提取器模块
from .knowledge_extractor import (
    Pattern,
    Rule,
    PatternAnalyzer,
    RuleGenerator,
    RuleValidator,
    KnowledgeExtractor
)

# 自适应优化器模块
from .adaptive_optimizer import (
    PerformanceMetrics,
    OptimizationStrategy,
    ProcessingPipeline,
    MetricsCollector,
    BottleneckAnalyzer,
    OptimizationTrigger,
    StrategyGenerator,
    AdaptiveOptimizer
)

# 规则引擎模块
from .rule_engine import (
    RuleCondition,
    RuleAction,
    EngineRule,
    RuleMatch,
    ExecutionResult,
    RuleMatcher,
    RuleExecutor,
    RuleLibrary,
    RuleEngine
)

# 规则优先级管理模块
from .rule_priority_manager import (
    PriorityFactors,
    PriorityWeights,
    RuleUsageRecord,
    ContextProfile,
    UsageTracker,
    ComplexityAnalyzer,
    ContextRelevanceAnalyzer,
    PerformanceScorer,
    RulePriorityManager
)

# 规则缓存管理模块
from .rule_cache_manager import (
    CacheEntry,
    CacheStats,
    LRUCache,
    RuleCache,
    ResultCache,
    CachePreloader,
    CacheOptimizer,
    RuleCacheManager
)

# 其他核心模块
from .content_analyzer import ContentAnalyzer
from .feature_extractor import FeatureExtractor
from .hotspot_detector import HotspotDetector
from .image_processor import ImageProcessor
from .cluster_analyzer import ClusterAnalyzer

__all__ = [
    # 知识提取器
    'Pattern',
    'Rule',
    'PatternAnalyzer',
    'RuleGenerator',
    'RuleValidator',
    'KnowledgeExtractor',
    
    # 自适应优化器
    'PerformanceMetrics',
    'OptimizationStrategy',
    'ProcessingPipeline',
    'MetricsCollector',
    'BottleneckAnalyzer',
    'OptimizationTrigger',
    'StrategyGenerator',
    'AdaptiveOptimizer',
    
    # 规则引擎
    'RuleCondition',
    'RuleAction',
    'EngineRule',
    'RuleMatch',
    'ExecutionResult',
    'RuleMatcher',
    'RuleExecutor',
    'RuleLibrary',
    'RuleEngine',
    
    # 规则优先级管理
    'PriorityFactors',
    'PriorityWeights',
    'RuleUsageRecord',
    'ContextProfile',
    'UsageTracker',
    'ComplexityAnalyzer',
    'ContextRelevanceAnalyzer',
    'PerformanceScorer',
    'RulePriorityManager',
    
    # 规则缓存管理
    'CacheEntry',
    'CacheStats',
    'LRUCache',
    'RuleCache',
    'ResultCache',
    'CachePreloader',
    'CacheOptimizer',
    'RuleCacheManager',
    
    # 其他核心模块
    'ContentAnalyzer',
    'FeatureExtractor',
    'HotspotDetector',
    'ImageProcessor',
    'ClusterAnalyzer'
] 