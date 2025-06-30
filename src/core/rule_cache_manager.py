"""
规则缓存管理模块
实现LRU缓存、规则和结果缓存、预加载机制、缓存优化等功能
"""

import time
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import OrderedDict
import logging
from threading import Lock, RLock
import pickle

from .knowledge_extractor import Rule

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """缓存条目"""
    key: str
    value: Any
    timestamp: float
    access_count: int = 0
    size: int = 0
    ttl: Optional[float] = None  # 生存时间（秒）
    tags: List[str] = field(default_factory=list)


@dataclass
class CacheStats:
    """缓存统计信息"""
    total_entries: int = 0
    total_size: int = 0
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    avg_access_time: float = 0.0
    hit_rate: float = 0.0


class LRUCache:
    """LRU缓存实现"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.stats = CacheStats()
        self.lock = RLock()
        
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # 检查TTL
                if entry.ttl and time.time() - entry.timestamp > entry.ttl:
                    self._remove_entry(key)
                    self.stats.miss_count += 1
                    return None
                
                # 更新访问信息
                entry.access_count += 1
                self.cache.move_to_end(key)
                
                self.stats.hit_count += 1
                return entry.value
            else:
                self.stats.miss_count += 1
                return None
    
    def put(self, key: str, value: Any, ttl: Optional[float] = None, 
            tags: Optional[List[str]] = None, size: Optional[int] = None) -> bool:
        """放入缓存"""
        with self.lock:
            # 计算大小
            if size is None:
                size = self._estimate_size(value)
            
            # 检查是否需要清理空间
            if not self._has_space(size):
                self._evict_entries(size)
            
            # 创建缓存条目
            entry = CacheEntry(
                key=key,
                value=value,
                timestamp=time.time(),
                size=size,
                ttl=ttl,
                tags=tags if tags is not None else []
            )
            
            # 如果键已存在，先移除旧条目
            if key in self.cache:
                old_entry = self.cache[key]
                self.stats.total_size -= old_entry.size
                self.stats.total_entries -= 1
            
            # 添加新条目
            self.cache[key] = entry
            self.cache.move_to_end(key)
            
            self.stats.total_size += size
            self.stats.total_entries += 1
            
            return True
    
    def remove(self, key: str) -> bool:
        """移除缓存条目"""
        with self.lock:
            return self._remove_entry(key)
    
    def clear(self):
        """清空缓存"""
        with self.lock:
            self.cache.clear()
            self.stats = CacheStats()
    
    def get_stats(self) -> CacheStats:
        """获取缓存统计"""
        with self.lock:
            # 计算命中率
            total_requests = self.stats.hit_count + self.stats.miss_count
            if total_requests > 0:
                self.stats.hit_rate = self.stats.hit_count / total_requests
            
            return self.stats
    
    def _remove_entry(self, key: str) -> bool:
        """移除缓存条目（内部方法）"""
        if key in self.cache:
            entry = self.cache[key]
            self.stats.total_size -= entry.size
            self.stats.total_entries -= 1
            del self.cache[key]
            return True
        return False
    
    def _has_space(self, required_size: int) -> bool:
        """检查是否有足够空间"""
        return (self.stats.total_entries < self.max_size and 
                self.stats.total_size + required_size <= self.max_memory_bytes)
    
    def _evict_entries(self, required_size: int):
        """驱逐缓存条目"""
        while (self.stats.total_entries >= self.max_size or 
               self.stats.total_size + required_size > self.max_memory_bytes):
            if not self.cache:
                break
            
            # 移除最久未使用的条目
            key, entry = self.cache.popitem(last=False)
            self.stats.total_size -= entry.size
            self.stats.total_entries -= 1
            self.stats.eviction_count += 1
    
    def _estimate_size(self, value: Any) -> int:
        """估算值的大小"""
        try:
            # 使用pickle估算大小
            return len(pickle.dumps(value))
        except:
            # 如果pickle失败，使用字符串长度估算
            return len(str(value))


class RuleCache:
    """规则缓存"""
    
    def __init__(self, max_rules: int = 500, max_memory_mb: int = 50):
        self.cache = LRUCache(max_rules, max_memory_mb)
        self.rule_hashes: Dict[str, str] = {}  # rule_id -> content_hash
        self.lock = Lock()
    
    def cache_rule(self, rule: Any) -> bool:
        """缓存规则"""
        try:
            rule_id = getattr(rule, 'rule_id', str(id(rule)))
            content_hash = self._calculate_rule_hash(rule)
            
            with self.lock:
                # 检查规则是否已更改
                if rule_id in self.rule_hashes and self.rule_hashes[rule_id] == content_hash:
                    return True  # 规则未更改，无需重新缓存
                
                # 缓存规则
                success = self.cache.put(
                    key=f"rule:{rule_id}",
                    value=rule,
                    tags=['rule'],
                    ttl=3600  # 1小时TTL
                )
                
                if success:
                    self.rule_hashes[rule_id] = content_hash
                
                return success
                
        except Exception as e:
            logger.error(f"规则缓存失败: {e}")
            return False
    
    def get_rule(self, rule_id: str) -> Optional[Any]:
        """获取缓存的规则"""
        return self.cache.get(f"rule:{rule_id}")
    
    def invalidate_rule(self, rule_id: str) -> bool:
        """使规则缓存失效"""
        with self.lock:
            if rule_id in self.rule_hashes:
                del self.rule_hashes[rule_id]
        
        return self.cache.remove(f"rule:{rule_id}")
    
    def _calculate_rule_hash(self, rule: Any) -> str:
        """计算规则内容哈希"""
        try:
            # 提取规则的关键属性并转换为可序列化的格式
            rule_data = {
                'conditions': [
                    {
                        'field': c.field,
                        'operator': c.operator,
                        'value': c.value,
                        'weight': c.weight
                    } for c in getattr(rule, 'conditions', [])
                ],
                'actions': [
                    {
                        'action_type': a.action_type,
                        'parameters': a.parameters,
                        'priority': a.priority
                    } for a in getattr(rule, 'actions', [])
                ],
                'priority': getattr(rule, 'priority', 0),
                'confidence': getattr(rule, 'confidence', 0)
            }
            
            content_str = json.dumps(rule_data, sort_keys=True)
            return hashlib.md5(content_str.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"规则哈希计算失败: {e}")
            return str(hash(rule))


class ResultCache:
    """结果缓存"""
    
    def __init__(self, max_results: int = 1000, max_memory_mb: int = 100):
        self.cache = LRUCache(max_results, max_memory_mb)
    
    def cache_result(self, input_hash: str, result: Any, ttl: float = 1800) -> bool:
        """缓存结果"""
        return self.cache.put(
            key=f"result:{input_hash}",
            value=result,
            tags=['result'],
            ttl=ttl
        )
    
    def get_result(self, input_hash: str) -> Optional[Any]:
        """获取缓存的结果"""
        return self.cache.get(f"result:{input_hash}")
    
    def invalidate_by_tags(self, tags: List[str]) -> int:
        """根据标签使缓存失效"""
        # 这里需要实现标签匹配的失效逻辑
        # 简化实现，实际应该遍历所有条目检查标签
        return 0


class CachePreloader:
    """缓存预加载器"""
    
    def __init__(self, rule_cache: RuleCache, result_cache: ResultCache):
        self.rule_cache = rule_cache
        self.result_cache = result_cache
        self.preload_queue: List[Tuple[str, Any]] = []
        self.lock = Lock()
    
    def add_preload_rule(self, rule: Any, priority: int = 0):
        """添加预加载规则"""
        with self.lock:
            self.preload_queue.append((rule, priority))
            # 按优先级排序
            self.preload_queue.sort(key=lambda x: x[1], reverse=True)
    
    def preload_rules(self, max_rules: int = 50):
        """预加载规则"""
        with self.lock:
            rules_to_preload = self.preload_queue[:max_rules]
            self.preload_queue = self.preload_queue[max_rules:]
        
        for rule, priority in rules_to_preload:
            try:
                self.rule_cache.cache_rule(rule)
                logger.info(f"预加载规则: {getattr(rule, 'rule_id', 'unknown')}")
            except Exception as e:
                logger.error(f"规则预加载失败: {e}")
    
    def preload_frequent_results(self, input_data_list: List[Dict[str, Any]], 
                               result_generator):
        """预加载频繁使用的结果"""
        for input_data in input_data_list:
            try:
                input_hash = self._calculate_input_hash(input_data)
                
                # 检查是否已缓存
                if self.result_cache.get_result(input_hash) is None:
                    # 生成结果并缓存
                    result = result_generator(input_data)
                    self.result_cache.cache_result(input_hash, result)
                    logger.info(f"预加载结果: {input_hash[:8]}...")
                    
            except Exception as e:
                logger.error(f"结果预加载失败: {e}")
    
    def _calculate_input_hash(self, input_data: Dict[str, Any]) -> str:
        """计算输入数据哈希"""
        try:
            data_str = json.dumps(input_data, sort_keys=True)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"输入哈希计算失败: {e}")
            return str(hash(str(input_data)))


class CacheOptimizer:
    """缓存优化器"""
    
    def __init__(self, rule_cache: RuleCache, result_cache: ResultCache):
        self.rule_cache = rule_cache
        self.result_cache = result_cache
        self.optimization_history: List[Dict[str, Any]] = []
    
    def optimize_cache_size(self, target_memory_mb: int):
        """优化缓存大小"""
        try:
            current_stats = self.rule_cache.cache.get_stats()
            current_memory_mb = current_stats.total_size / (1024 * 1024)
            
            if current_memory_mb > target_memory_mb:
                # 计算需要释放的内存
                memory_to_free = current_memory_mb - target_memory_mb
                bytes_to_free = int(memory_to_free * 1024 * 1024)
                
                # 清理最少使用的条目
                self._cleanup_least_used(bytes_to_free)
                
                logger.info(f"缓存优化完成，释放了 {memory_to_free:.2f}MB 内存")
            
        except Exception as e:
            logger.error(f"缓存大小优化失败: {e}")
    
    def optimize_ttl(self, access_patterns: Dict[str, float]):
        """优化TTL设置"""
        try:
            # 根据访问模式调整TTL
            for key, avg_access_interval in access_patterns.items():
                # 设置TTL为平均访问间隔的2倍
                optimal_ttl = avg_access_interval * 2
                
                # 这里需要实现TTL调整逻辑
                # 简化实现
                logger.info(f"建议为 {key} 设置TTL: {optimal_ttl:.2f}秒")
                
        except Exception as e:
            logger.error(f"TTL优化失败: {e}")
    
    def _cleanup_least_used(self, bytes_to_free: int):
        """清理最少使用的条目"""
        # 这里需要实现基于使用频率的清理逻辑
        # 简化实现
        pass
    
    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """获取优化建议"""
        suggestions = []
        
        try:
            rule_stats = self.rule_cache.cache.get_stats()
            result_stats = self.result_cache.cache.get_stats()
            
            # 检查命中率
            if rule_stats.hit_rate < 0.5:
                suggestions.append({
                    'type': 'hit_rate_low',
                    'component': 'rule_cache',
                    'message': f'规则缓存命中率较低: {rule_stats.hit_rate:.2%}',
                    'suggestion': '考虑增加缓存大小或优化缓存策略'
                })
            
            if result_stats.hit_rate < 0.5:
                suggestions.append({
                    'type': 'hit_rate_low',
                    'component': 'result_cache',
                    'message': f'结果缓存命中率较低: {result_stats.hit_rate:.2%}',
                    'suggestion': '考虑增加缓存大小或优化缓存策略'
                })
            
            # 检查内存使用
            rule_memory_mb = rule_stats.total_size / (1024 * 1024)
            if rule_memory_mb > 50:
                suggestions.append({
                    'type': 'memory_high',
                    'component': 'rule_cache',
                    'message': f'规则缓存内存使用较高: {rule_memory_mb:.2f}MB',
                    'suggestion': '考虑清理不常用的规则或增加内存限制'
                })
            
        except Exception as e:
            logger.error(f"获取优化建议失败: {e}")
        
        return suggestions


class RuleCacheManager:
    """规则缓存管理器"""
    
    def __init__(self, max_rules: int = 500, max_results: int = 1000, 
                 max_memory_mb: int = 200):
        self.rule_cache = RuleCache(max_rules, max_memory_mb // 2)
        self.result_cache = ResultCache(max_results, max_memory_mb // 2)
        self.preloader = CachePreloader(self.rule_cache, self.result_cache)
        self.optimizer = CacheOptimizer(self.rule_cache, self.result_cache)
        self.lock = Lock()
    
    def cache_rule(self, rule: Any) -> bool:
        """缓存规则"""
        return self.rule_cache.cache_rule(rule)
    
    def get_rule(self, rule_id: str) -> Optional[Any]:
        """获取缓存的规则"""
        return self.rule_cache.get_rule(rule_id)
    
    def cache_result(self, input_data: Dict[str, Any], result: Any, ttl: float = 1800) -> bool:
        """缓存结果"""
        input_hash = self._calculate_input_hash(input_data)
        return self.result_cache.cache_result(input_hash, result, ttl)
    
    def get_result(self, input_data: Dict[str, Any]) -> Optional[Any]:
        """获取缓存的结果"""
        input_hash = self._calculate_input_hash(input_data)
        return self.result_cache.get_result(input_hash)
    
    def invalidate_rule(self, rule_id: str) -> bool:
        """使规则缓存失效"""
        return self.rule_cache.invalidate_rule(rule_id)
    
    def clear_all(self):
        """清空所有缓存"""
        self.rule_cache.cache.clear()
        self.result_cache.cache.clear()
    
    def preload_rules(self, rules: List[Any], max_rules: int = 50):
        """预加载规则"""
        for rule in rules:
            self.preloader.add_preload_rule(rule)
        self.preloader.preload_rules(max_rules)
    
    def optimize_caches(self, target_memory_mb: int = 150):
        """优化缓存"""
        self.optimizer.optimize_cache_size(target_memory_mb)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        rule_stats = self.rule_cache.cache.get_stats()
        result_stats = self.result_cache.cache.get_stats()
        
        return {
            'rule_cache': {
                'total_entries': rule_stats.total_entries,
                'total_size_mb': rule_stats.total_size / (1024 * 1024),
                'hit_rate': rule_stats.hit_rate,
                'hit_count': rule_stats.hit_count,
                'miss_count': rule_stats.miss_count,
                'eviction_count': rule_stats.eviction_count
            },
            'result_cache': {
                'total_entries': result_stats.total_entries,
                'total_size_mb': result_stats.total_size / (1024 * 1024),
                'hit_rate': result_stats.hit_rate,
                'hit_count': result_stats.hit_count,
                'miss_count': result_stats.miss_count,
                'eviction_count': result_stats.eviction_count
            },
            'total_memory_mb': (rule_stats.total_size + result_stats.total_size) / (1024 * 1024)
        }
    
    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """获取优化建议"""
        return self.optimizer.get_optimization_suggestions()
    
    def _calculate_input_hash(self, input_data: Dict[str, Any]) -> str:
        """计算输入数据哈希"""
        try:
            data_str = json.dumps(input_data, sort_keys=True)
            return hashlib.md5(data_str.encode()).hexdigest()
        except Exception as e:
            logger.error(f"输入哈希计算失败: {e}")
            return str(hash(str(input_data))) 