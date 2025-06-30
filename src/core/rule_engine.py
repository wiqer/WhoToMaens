"""
嵌入式规则引擎核心模块
实现规则库管理、规则匹配、推理执行、规则学习与更新等功能
"""

import time
import json
import re
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import logging
from threading import Lock

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RuleCondition:
    """规则条件"""
    field: str
    operator: str  # 'eq', 'ne', 'gt', 'lt', 'gte', 'lte', 'in', 'contains', 'regex'
    value: Any
    weight: float = 1.0
    
    def __hash__(self):
        # 使用不可变字段生成哈希值
        return hash((self.field, self.operator, str(self.value), self.weight))


@dataclass(frozen=True)
class RuleAction:
    """规则动作"""
    action_type: str  # 'extract', 'classify', 'process', 'transform', 'validate'
    parameters: Dict[str, Any]
    priority: float = 1.0
    
    def __hash__(self):
        # 将 parameters 转换为可哈希的元组
        params_tuple = tuple(sorted(self.parameters.items()))
        return hash((self.action_type, params_tuple, self.priority))


@dataclass
class EngineRule:
    """规则引擎规则"""
    rule_id: str
    name: str
    description: str
    conditions: List[RuleCondition]
    actions: List[RuleAction]
    priority: float
    confidence: float
    created_at: float
    updated_at: float
    usage_count: int = 0
    success_count: int = 0
    tags: List[str] = field(default_factory=list)
    enabled: bool = True
    
    def __hash__(self):
        # 使用 rule_id 作为主要哈希值，因为它是唯一的
        return hash(self.rule_id)


@dataclass
class RuleMatch:
    """规则匹配结果"""
    rule: EngineRule
    match_score: float
    matched_conditions: List[RuleCondition]
    execution_time: float
    timestamp: float


@dataclass
class ExecutionResult:
    """执行结果"""
    rule_id: str
    success: bool
    output: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RuleMatcher:
    """规则匹配器"""
    
    def __init__(self):
        self.operators = {
            'eq': self._eq_operator,
            'ne': self._ne_operator,
            'gt': self._gt_operator,
            'lt': self._lt_operator,
            'gte': self._gte_operator,
            'lte': self._lte_operator,
            'in': self._in_operator,
            'contains': self._contains_operator,
            'regex': self._regex_operator
        }
    
    def match_rule(self, rule: EngineRule, data: Dict[str, Any]) -> Tuple[bool, float, List[RuleCondition]]:
        """匹配规则"""
        matched_conditions = []
        total_score = 0.0
        total_weight = 0.0
        
        for condition in rule.conditions:
            if self._evaluate_condition(condition, data):
                matched_conditions.append(condition)
                total_score += condition.weight
            total_weight += condition.weight
        
        if total_weight == 0:
            return False, 0.0, []
        
        match_score = total_score / total_weight
        is_matched = match_score >= 0.5  # 至少50%的条件匹配
        
        return is_matched, match_score, matched_conditions
    
    def _evaluate_condition(self, condition: RuleCondition, data: Dict[str, Any]) -> bool:
        """评估单个条件"""
        if condition.field not in data:
            return False
        
        field_value = data[condition.field]
        operator_func = self.operators.get(condition.operator)
        
        if operator_func is None:
            logger.warning(f"未知的操作符: {condition.operator}")
            return False
        
        try:
            return operator_func(field_value, condition.value)
        except Exception as e:
            logger.error(f"条件评估失败: {e}")
            return False
    
    def _eq_operator(self, field_value: Any, expected_value: Any) -> bool:
        return field_value == expected_value
    
    def _ne_operator(self, field_value: Any, expected_value: Any) -> bool:
        return field_value != expected_value
    
    def _gt_operator(self, field_value: Any, expected_value: Any) -> bool:
        return field_value > expected_value
    
    def _lt_operator(self, field_value: Any, expected_value: Any) -> bool:
        return field_value < expected_value
    
    def _gte_operator(self, field_value: Any, expected_value: Any) -> bool:
        return field_value >= expected_value
    
    def _lte_operator(self, field_value: Any, expected_value: Any) -> bool:
        return field_value <= expected_value
    
    def _in_operator(self, field_value: Any, expected_values: List[Any]) -> bool:
        return field_value in expected_values
    
    def _contains_operator(self, field_value: Any, expected_value: Any) -> bool:
        if isinstance(field_value, str) and isinstance(expected_value, str):
            return expected_value in field_value
        return False
    
    def _regex_operator(self, field_value: Any, pattern: str) -> bool:
        if isinstance(field_value, str):
            try:
                return bool(re.search(pattern, field_value))
            except re.error:
                return False
        return False


class RuleExecutor:
    """规则执行器"""
    
    def __init__(self):
        self.action_handlers = {
            'extract': self._handle_extract_action,
            'classify': self._handle_classify_action,
            'process': self._handle_process_action,
            'transform': self._handle_transform_action,
            'validate': self._handle_validate_action
        }
    
    def execute_rule(self, rule: EngineRule, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> ExecutionResult:
        """执行规则"""
        start_time = time.time()
        result = ExecutionResult(rule_id=rule.rule_id, success=False, output={})
        
        try:
            # 按优先级排序动作
            sorted_actions = sorted(rule.actions, key=lambda x: x.priority, reverse=True)
            
            output = {}
            for action in sorted_actions:
                handler = self.action_handlers.get(action.action_type)
                if handler:
                    action_result = handler(action, data, context if context is not None else {})
                    output[action.action_type] = action_result
                else:
                    logger.warning(f"未知的动作类型: {action.action_type}")
            
            result.success = True
            result.output = output
            
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"规则执行失败: {e}")
        
        result.execution_time = time.time() - start_time
        return result
    
    def _handle_extract_action(self, action: RuleAction, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """处理提取动作"""
        params = action.parameters
        field = params.get('field', '')
        pattern = params.get('pattern', '')
        
        if field in data:
            value = data[field]
            if pattern and isinstance(value, str):
                import re
                match = re.search(pattern, value)
                if match:
                    return {'extracted': match.group(1) if match.groups() else match.group(0)}
            return {'extracted': value}
        
        return {'extracted': {}}
    
    def _handle_classify_action(self, action: RuleAction, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """处理分类动作"""
        params = action.parameters
        categories = params.get('categories', {})
        field = params.get('field', '')
        
        if field in data:
            value = data[field]
            for category, conditions in categories.items():
                if self._match_category_conditions(conditions, value):
                    return {'classification': category, 'confidence': 0.8}
        
        return {'classification': 'unknown', 'confidence': 0.0}
    
    def _handle_process_action(self, action: RuleAction, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """处理处理动作"""
        params = action.parameters
        processor = params.get('processor', '')
        
        # 这里可以集成具体的处理器
        return {'processed': True, 'processor': processor}
    
    def _handle_transform_action(self, action: RuleAction, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """处理转换动作"""
        params = action.parameters
        transform_type = params.get('type', '')
        
        if transform_type == 'normalize':
            return {'transformed': data}
        elif transform_type == 'filter':
            fields = params.get('fields', [])
            return {'transformed': {k: v for k, v in data.items() if k in fields}}
        
        return {'transformed': data}
    
    def _handle_validate_action(self, action: RuleAction, data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """处理验证动作"""
        params = action.parameters
        validators = params.get('validators', [])
        
        validation_results = []
        for validator in validators:
            field = validator.get('field', '')
            rule = validator.get('rule', '')
            
            if field in data:
                value = data[field]
                is_valid = self._validate_field(value, rule)
                validation_results.append({
                    'field': field,
                    'valid': is_valid,
                    'rule': rule
                })
        
        return {'validation_results': validation_results}
    
    def _match_category_conditions(self, conditions: Dict[str, Any], value: Any) -> bool:
        """匹配分类条件"""
        # 简单的条件匹配实现
        return True
    
    def _validate_field(self, value: Any, rule: str) -> bool:
        """验证字段"""
        # 简单的验证实现
        return True


class RuleLibrary:
    """规则库管理器"""
    
    def __init__(self):
        self.rules: Dict[str, EngineRule] = {}
        self.rule_groups: Dict[str, List[str]] = defaultdict(list)
        self.lock = Lock()
    
    def add_rule(self, rule: EngineRule) -> bool:
        """添加规则"""
        with self.lock:
            if rule.rule_id in self.rules:
                logger.warning(f"规则已存在: {rule.rule_id}")
                return False
            
            self.rules[rule.rule_id] = rule
            
            # 添加到分组
            for tag in rule.tags:
                self.rule_groups[tag].append(rule.rule_id)
            
            logger.info(f"规则已添加: {rule.rule_id}")
            return True
    
    def update_rule(self, rule: EngineRule) -> bool:
        """更新规则"""
        with self.lock:
            if rule.rule_id not in self.rules:
                logger.warning(f"规则不存在: {rule.rule_id}")
                return False
            
            old_rule = self.rules[rule.rule_id]
            
            # 更新分组
            for tag in old_rule.tags:
                if rule.rule_id in self.rule_groups[tag]:
                    self.rule_groups[tag].remove(rule.rule_id)
            
            for tag in rule.tags:
                self.rule_groups[tag].append(rule.rule_id)
            
            rule.updated_at = time.time()
            self.rules[rule.rule_id] = rule
            
            logger.info(f"规则已更新: {rule.rule_id}")
            return True
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除规则"""
        with self.lock:
            if rule_id not in self.rules:
                return False
            
            rule = self.rules[rule_id]
            
            # 从分组中移除
            for tag in rule.tags:
                if rule_id in self.rule_groups[tag]:
                    self.rule_groups[tag].remove(rule_id)
            
            del self.rules[rule_id]
            logger.info(f"规则已删除: {rule_id}")
            return True
    
    def get_rule(self, rule_id: str) -> Optional[EngineRule]:
        """获取规则"""
        return self.rules.get(rule_id)
    
    def get_rules_by_tag(self, tag: str) -> List[EngineRule]:
        """根据标签获取规则"""
        rule_ids = self.rule_groups.get(tag, [])
        return [self.rules[rule_id] for rule_id in rule_ids if rule_id in self.rules]
    
    def get_all_rules(self) -> List[EngineRule]:
        """获取所有规则"""
        return list(self.rules.values())
    
    def get_enabled_rules(self) -> List[EngineRule]:
        """获取启用的规则"""
        return [rule for rule in self.rules.values() if rule.enabled]
    
    def search_rules(self, query: str) -> List[EngineRule]:
        """搜索规则"""
        results = []
        query_lower = query.lower()
        
        for rule in self.rules.values():
            if (query_lower in rule.name.lower() or 
                query_lower in rule.description.lower() or
                any(query_lower in tag.lower() for tag in rule.tags)):
                results.append(rule)
        
        return results


class RuleEngine:
    """规则引擎核心"""
    
    def __init__(self):
        self.rule_library = RuleLibrary()
        self.matcher = RuleMatcher()
        self.executor = RuleExecutor()
        self.execution_history: List[RuleMatch] = []
        self.lock = Lock()
    
    def add_rule(self, rule: EngineRule) -> bool:
        """添加规则"""
        return self.rule_library.add_rule(rule)
    
    def update_rule(self, rule: EngineRule) -> bool:
        """更新规则"""
        return self.rule_library.update_rule(rule)
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除规则"""
        return self.rule_library.remove_rule(rule_id)
    
    def execute_rules(self, data: Dict[str, Any], context: Optional[Dict[str, Any]] = None, 
                     max_rules: int = 10) -> List[ExecutionResult]:
        """执行规则"""
        start_time = time.time()
        results = []
        
        # 获取启用的规则
        enabled_rules = self.rule_library.get_enabled_rules()
        
        # 按优先级排序
        sorted_rules = sorted(enabled_rules, key=lambda x: x.priority, reverse=True)
        
        executed_count = 0
        for rule in sorted_rules:
            if executed_count >= max_rules:
                break
            
            # 匹配规则
            is_matched, match_score, matched_conditions = self.matcher.match_rule(rule, data)
            
            if is_matched:
                # 记录匹配
                match_record = RuleMatch(
                    rule=rule,
                    match_score=match_score,
                    matched_conditions=matched_conditions,
                    execution_time=0.0,
                    timestamp=time.time()
                )
                
                # 执行规则
                execution_start = time.time()
                result = self.executor.execute_rule(rule, data, context if context is not None else {})
                execution_time = time.time() - execution_start
                
                match_record.execution_time = execution_time
                results.append(result)
                
                # 更新使用统计
                rule.usage_count += 1
                if result.success:
                    rule.success_count += 1
                
                executed_count += 1
        
        # 记录执行历史
        with self.lock:
            self.execution_history.extend([match for match in results if hasattr(match, 'rule')])
            if len(self.execution_history) > 1000:  # 限制历史记录数量
                self.execution_history = self.execution_history[-1000:]
        
        total_time = time.time() - start_time
        logger.info(f"规则执行完成，执行了 {len(results)} 个规则，耗时 {total_time:.3f}秒")
        
        return results
    
    def get_rule_stats(self) -> Dict[str, Any]:
        """获取规则统计信息"""
        rules = self.rule_library.get_all_rules()
        
        stats = {
            'total_rules': len(rules),
            'enabled_rules': len([r for r in rules if r.enabled]),
            'rule_types': defaultdict(int),
            'avg_usage_count': 0,
            'avg_success_rate': 0
        }
        
        if rules:
            total_usage = sum(r.usage_count for r in rules)
            total_success = sum(r.success_count for r in rules)
            
            stats['avg_usage_count'] = total_usage / len(rules)
            stats['avg_success_rate'] = total_success / total_usage if total_usage > 0 else 0
        
        return stats
    
    def export_rules(self, format: str = 'json') -> str:
        """导出规则"""
        rules = self.rule_library.get_all_rules()
        
        if format == 'json':
            rules_data = []
            for rule in rules:
                rule_dict = {
                    'rule_id': rule.rule_id,
                    'name': rule.name,
                    'description': rule.description,
                    'conditions': [
                        {
                            'field': c.field,
                            'operator': c.operator,
                            'value': c.value,
                            'weight': c.weight
                        } for c in rule.conditions
                    ],
                    'actions': [
                        {
                            'action_type': a.action_type,
                            'parameters': a.parameters,
                            'priority': a.priority
                        } for a in rule.actions
                    ],
                    'priority': rule.priority,
                    'confidence': rule.confidence,
                    'tags': rule.tags,
                    'enabled': rule.enabled
                }
                rules_data.append(rule_dict)
            
            return json.dumps(rules_data, ensure_ascii=False, indent=2)
        
        return ""
    
    def import_rules(self, rules_data: str, format: str = 'json') -> int:
        """导入规则"""
        if format == 'json':
            try:
                rules_list = json.loads(rules_data)
                imported_count = 0
                
                for rule_dict in rules_list:
                    conditions = [
                        RuleCondition(
                            field=c['field'],
                            operator=c['operator'],
                            value=c['value'],
                            weight=c.get('weight', 1.0)
                        ) for c in rule_dict.get('conditions', [])
                    ]
                    
                    actions = [
                        RuleAction(
                            action_type=a['action_type'],
                            parameters=a['parameters'],
                            priority=a.get('priority', 1.0)
                        ) for a in rule_dict.get('actions', [])
                    ]
                    
                    rule = EngineRule(
                        rule_id=rule_dict['rule_id'],
                        name=rule_dict['name'],
                        description=rule_dict['description'],
                        conditions=conditions,
                        actions=actions,
                        priority=rule_dict.get('priority', 0.5),
                        confidence=rule_dict.get('confidence', 0.8),
                        created_at=time.time(),
                        updated_at=time.time(),
                        tags=rule_dict.get('tags', []),
                        enabled=rule_dict.get('enabled', True)
                    )
                    
                    if self.rule_library.add_rule(rule):
                        imported_count += 1
                
                logger.info(f"成功导入 {imported_count} 个规则")
                return imported_count
                
            except Exception as e:
                logger.error(f"规则导入失败: {e}")
                return 0
        
        return 0 