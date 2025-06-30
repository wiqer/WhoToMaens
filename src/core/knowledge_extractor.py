"""
知识提取器模块
实现从LLM响应中提取结构化知识，支持模式识别和规则生成
"""

import json
import re
import time
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class Pattern:
    """模式数据结构"""
    pattern_id: str
    pattern_type: str  # 'feature', 'classification', 'processing', 'rule'
    content: Dict[str, Any]
    confidence: float
    context: Dict[str, Any]
    created_at: float
    usage_count: int = 0


@dataclass
class Rule:
    """规则数据结构"""
    rule_id: str
    rule_type: str  # 'classification', 'extraction', 'processing'
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    priority: float
    accuracy: float
    created_at: float
    usage_count: int = 0


class PatternAnalyzer:
    """模式分析器"""
    
    def __init__(self):
        self.pattern_templates = {
            'feature': r'特征[：:]\s*(.+)',
            'classification': r'分类[：:]\s*(.+)',
            'processing': r'处理[：:]\s*(.+)',
            'rule': r'规则[：:]\s*(.+)'
        }
    
    def analyze(self, llm_response: str, input_data: Dict[str, Any]) -> List[Pattern]:
        """分析LLM响应中的模式"""
        patterns = []
        
        try:
            # 解析JSON响应
            if isinstance(llm_response, str):
                response_data = json.loads(llm_response)
            else:
                response_data = llm_response
            
            # 提取特征模式
            feature_patterns = self._extract_feature_patterns(response_data, input_data)
            patterns.extend(feature_patterns)
            
            # 提取分类模式
            classification_patterns = self._extract_classification_patterns(response_data, input_data)
            patterns.extend(classification_patterns)
            
            # 提取处理模式
            processing_patterns = self._extract_processing_patterns(response_data, input_data)
            patterns.extend(processing_patterns)
            
            # 提取规则模式
            rule_patterns = self._extract_rule_patterns(response_data, input_data)
            patterns.extend(rule_patterns)
            
        except Exception as e:
            logger.error(f"模式分析失败: {e}")
        
        return patterns
    
    def _extract_feature_patterns(self, response_data: Dict, input_data: Dict) -> List[Pattern]:
        """提取特征模式"""
        patterns = []
        
        if 'features' in response_data:
            for feature in response_data['features']:
                pattern = Pattern(
                    pattern_id=f"feature_{int(time.time() * 1000)}",
                    pattern_type='feature',
                    content=feature,
                    confidence=feature.get('confidence', 0.8),
                    context=input_data,
                    created_at=time.time()
                )
                patterns.append(pattern)
        
        return patterns
    
    def _extract_classification_patterns(self, response_data: Dict, input_data: Dict) -> List[Pattern]:
        """提取分类模式"""
        patterns = []
        
        if 'classification' in response_data:
            classification = response_data['classification']
            pattern = Pattern(
                pattern_id=f"classification_{int(time.time() * 1000)}",
                pattern_type='classification',
                content=classification,
                confidence=classification.get('confidence', 0.8),
                context=input_data,
                created_at=time.time()
            )
            patterns.append(pattern)
        
        return patterns
    
    def _extract_processing_patterns(self, response_data: Dict, input_data: Dict) -> List[Pattern]:
        """提取处理模式"""
        patterns = []
        
        if 'processing_steps' in response_data:
            for step in response_data['processing_steps']:
                pattern = Pattern(
                    pattern_id=f"processing_{int(time.time() * 1000)}",
                    pattern_type='processing',
                    content=step,
                    confidence=step.get('confidence', 0.8),
                    context=input_data,
                    created_at=time.time()
                )
                patterns.append(pattern)
        
        return patterns
    
    def _extract_rule_patterns(self, response_data: Dict, input_data: Dict) -> List[Pattern]:
        """提取规则模式"""
        patterns = []
        
        if 'rules' in response_data:
            for rule in response_data['rules']:
                pattern = Pattern(
                    pattern_id=f"rule_{int(time.time() * 1000)}",
                    pattern_type='rule',
                    content=rule,
                    confidence=rule.get('confidence', 0.8),
                    context=input_data,
                    created_at=time.time()
                )
                patterns.append(pattern)
        
        return patterns


class RuleGenerator:
    """规则生成器"""
    
    def __init__(self):
        self.rule_templates = {
            'classification': self._generate_classification_rule,
            'extraction': self._generate_extraction_rule,
            'processing': self._generate_processing_rule
        }
    
    def generate_rules(self, patterns: List[Pattern]) -> List[Rule]:
        """基于模式生成规则"""
        rules = []
        
        for pattern in patterns:
            if pattern.pattern_type in self.rule_templates:
                rule = self.rule_templates[pattern.pattern_type](pattern)
                if rule:
                    rules.append(rule)
        
        return rules
    
    def _generate_classification_rule(self, pattern: Pattern) -> Optional[Rule]:
        """生成分类规则"""
        try:
            content = pattern.content
            conditions = []
            actions = []
            
            # 提取条件
            if 'conditions' in content:
                conditions = content['conditions']
            
            # 提取动作
            if 'actions' in content:
                actions = content['actions']
            
            rule = Rule(
                rule_id=f"rule_{int(time.time() * 1000)}",
                rule_type='classification',
                conditions=conditions,
                actions=actions,
                priority=content.get('priority', 0.5),
                accuracy=pattern.confidence,
                created_at=time.time()
            )
            
            return rule
            
        except Exception as e:
            logger.error(f"生成分类规则失败: {e}")
            return None
    
    def _generate_extraction_rule(self, pattern: Pattern) -> Optional[Rule]:
        """生成提取规则"""
        try:
            content = pattern.content
            conditions = []
            actions = []
            
            # 提取条件
            if 'conditions' in content:
                conditions = content['conditions']
            
            # 提取动作
            if 'actions' in content:
                actions = content['actions']
            
            rule = Rule(
                rule_id=f"rule_{int(time.time() * 1000)}",
                rule_type='extraction',
                conditions=conditions,
                actions=actions,
                priority=content.get('priority', 0.5),
                accuracy=pattern.confidence,
                created_at=time.time()
            )
            
            return rule
            
        except Exception as e:
            logger.error(f"生成提取规则失败: {e}")
            return None
    
    def _generate_processing_rule(self, pattern: Pattern) -> Optional[Rule]:
        """生成处理规则"""
        try:
            content = pattern.content
            conditions = []
            actions = []
            
            # 提取条件
            if 'conditions' in content:
                conditions = content['conditions']
            
            # 提取动作
            if 'actions' in content:
                actions = content['actions']
            
            rule = Rule(
                rule_id=f"rule_{int(time.time() * 1000)}",
                rule_type='processing',
                conditions=conditions,
                actions=actions,
                priority=content.get('priority', 0.5),
                accuracy=pattern.confidence,
                created_at=time.time()
            )
            
            return rule
            
        except Exception as e:
            logger.error(f"生成处理规则失败: {e}")
            return None


class RuleValidator:
    """规则验证器"""
    
    def __init__(self):
        self.validation_rules = {
            'min_confidence': 0.7,
            'min_conditions': 1,
            'min_actions': 1
        }
    
    def validate_rules(self, candidate_rules: List[Rule]) -> List[Rule]:
        """验证候选规则"""
        valid_rules = []
        
        for rule in candidate_rules:
            if self._validate_rule(rule):
                valid_rules.append(rule)
            else:
                logger.warning(f"规则验证失败: {rule.rule_id}")
        
        return valid_rules
    
    def _validate_rule(self, rule: Rule) -> bool:
        """验证单个规则"""
        try:
            # 检查置信度
            if rule.accuracy < self.validation_rules['min_confidence']:
                return False
            
            # 检查条件数量
            if len(rule.conditions) < self.validation_rules['min_conditions']:
                return False
            
            # 检查动作数量
            if len(rule.actions) < self.validation_rules['min_actions']:
                return False
            
            # 检查规则结构
            if not self._validate_rule_structure(rule):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"规则验证异常: {e}")
            return False
    
    def _validate_rule_structure(self, rule: Rule) -> bool:
        """验证规则结构"""
        try:
            # 验证条件结构
            for condition in rule.conditions:
                if not isinstance(condition, dict):
                    return False
                if 'field' not in condition or 'operator' not in condition:
                    return False
            
            # 验证动作结构
            for action in rule.actions:
                if not isinstance(action, dict):
                    return False
                if 'type' not in action:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"规则结构验证异常: {e}")
            return False


class KnowledgeExtractor:
    """知识提取器"""
    
    def __init__(self):
        self.knowledge_base = {}
        self.pattern_database = {}
        self.rule_engine = None  # 将在后续模块中初始化
        self.pattern_analyzer = PatternAnalyzer()
        self.rule_generator = RuleGenerator()
        self.rule_validator = RuleValidator()
        
        logger.info("知识提取器初始化完成")
    
    def extract_from_llm_response(self, llm_response: str, context: Dict[str, Any]) -> Tuple[List[Pattern], List[Rule]]:
        """从LLM响应中提取结构化知识"""
        try:
            # 解析LLM输出，提取关键信息
            patterns = self.pattern_analyzer.analyze(llm_response, context)
            
            # 生成规则
            candidate_rules = self.rule_generator.generate_rules(patterns)
            
            # 验证规则
            valid_rules = self.rule_validator.validate_rules(candidate_rules)
            
            # 存储到知识库
            self.store_knowledge(patterns, valid_rules)
            
            logger.info(f"成功提取 {len(patterns)} 个模式，{len(valid_rules)} 个规则")
            
            return patterns, valid_rules
            
        except Exception as e:
            logger.error(f"知识提取失败: {e}")
            return [], []
    
    def store_knowledge(self, patterns: List[Pattern], rules: List[Rule]):
        """存储知识到知识库"""
        try:
            # 存储模式
            for pattern in patterns:
                self.pattern_database[pattern.pattern_id] = pattern
            
            # 存储规则
            for rule in rules:
                if rule.rule_type not in self.knowledge_base:
                    self.knowledge_base[rule.rule_type] = []
                self.knowledge_base[rule.rule_type].append(rule)
            
            logger.info(f"知识存储完成: {len(patterns)} 个模式，{len(rules)} 个规则")
            
        except Exception as e:
            logger.error(f"知识存储失败: {e}")
    
    def get_patterns_by_type(self, pattern_type: str) -> List[Pattern]:
        """根据类型获取模式"""
        patterns = []
        for pattern in self.pattern_database.values():
            if pattern.pattern_type == pattern_type:
                patterns.append(pattern)
        return patterns
    
    def get_rules_by_type(self, rule_type: str) -> List[Rule]:
        """根据类型获取规则"""
        return self.knowledge_base.get(rule_type, [])
    
    def update_pattern_usage(self, pattern_id: str):
        """更新模式使用次数"""
        if pattern_id in self.pattern_database:
            self.pattern_database[pattern_id].usage_count += 1
    
    def update_rule_usage(self, rule_id: str):
        """更新规则使用次数"""
        for rule_type, rules in self.knowledge_base.items():
            for rule in rules:
                if rule.rule_id == rule_id:
                    rule.usage_count += 1
                    break
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """获取知识库统计信息"""
        stats = {
            'total_patterns': len(self.pattern_database),
            'total_rules': sum(len(rules) for rules in self.knowledge_base.values()),
            'pattern_types': defaultdict(int),
            'rule_types': defaultdict(int),
            'most_used_patterns': [],
            'most_used_rules': []
        }
        
        # 统计模式类型
        for pattern in self.pattern_database.values():
            stats['pattern_types'][pattern.pattern_type] += 1
        
        # 统计规则类型
        for rule_type, rules in self.knowledge_base.items():
            stats['rule_types'][rule_type] = len(rules)
        
        # 获取最常用的模式
        sorted_patterns = sorted(
            self.pattern_database.values(),
            key=lambda p: p.usage_count,
            reverse=True
        )[:10]
        stats['most_used_patterns'] = [
            {'id': p.pattern_id, 'type': p.pattern_type, 'usage_count': p.usage_count}
            for p in sorted_patterns
        ]
        
        # 获取最常用的规则
        all_rules = []
        for rules in self.knowledge_base.values():
            all_rules.extend(rules)
        
        sorted_rules = sorted(
            all_rules,
            key=lambda r: r.usage_count,
            reverse=True
        )[:10]
        stats['most_used_rules'] = [
            {'id': r.rule_id, 'type': r.rule_type, 'usage_count': r.usage_count}
            for r in sorted_rules
        ]
        
        return stats 