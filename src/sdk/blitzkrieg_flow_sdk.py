"""
BlitzkriegFlow SDK集成模块
支持SDK方式调用规则引擎及相关功能，支持异步流程处理、自定义流程处理器、规则管理、反馈提交和统计查询
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional, Callable, Union, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import logging
from concurrent.futures import ThreadPoolExecutor
import threading

from ..core.rule_engine import RuleEngine, EngineRule, RuleCondition, RuleAction
from ..core.rule_priority_manager import RulePriorityManager
from ..core.rule_cache_manager import RuleCacheManager
from ..core.knowledge_extractor import KnowledgeExtractor
from ..core.adaptive_optimizer import AdaptiveOptimizer

logger = logging.getLogger(__name__)


class FlowStatus(Enum):
    """流程状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FlowType(Enum):
    """流程类型枚举"""
    RULE_EXECUTION = "rule_execution"
    KNOWLEDGE_EXTRACTION = "knowledge_extraction"
    OPTIMIZATION = "optimization"
    CUSTOM = "custom"


@dataclass
class FlowContext:
    """流程上下文"""
    flow_id: str
    flow_type: FlowType
    status: FlowStatus
    input_data: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FlowResult:
    """流程结果"""
    flow_id: str
    success: bool
    result: Optional[Dict[str, Any]] = None
    execution_time: float = 0.0
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class FlowProcessor:
    """流程处理器基类"""
    
    def __init__(self, name: str):
        self.name = name
        self.processor_id = f"processor_{int(time.time() * 1000)}"
    
    async def process(self, context: FlowContext) -> FlowResult:
        """处理流程（子类需要实现）"""
        raise NotImplementedError("子类必须实现process方法")
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据（子类可以重写）"""
        return True
    
    def get_processor_info(self) -> Dict[str, Any]:
        """获取处理器信息"""
        return {
            "processor_id": self.processor_id,
            "name": self.name,
            "type": self.__class__.__name__
        }


class RuleExecutionProcessor(FlowProcessor):
    """规则执行处理器"""
    
    def __init__(self, rule_engine: RuleEngine, priority_manager: RulePriorityManager):
        super().__init__("Rule Execution Processor")
        self.rule_engine = rule_engine
        self.priority_manager = priority_manager
    
    async def process(self, context: FlowContext) -> FlowResult:
        """执行规则处理"""
        start_time = time.time()
        
        try:
            # 验证输入
            if not self.validate_input(context.input_data):
                raise ValueError("输入数据验证失败")
            
            # 执行规则
            results = self.rule_engine.execute_rules(
                data=context.input_data,
                context=context.context,
                max_rules=context.metadata.get('max_rules', 10)
            )
            
            # 记录执行统计
            for result in results:
                if result.success:
                    self.priority_manager.record_rule_execution(
                        rule_id=result.rule_id,
                        success=True,
                        execution_time=result.execution_time,
                        context_keys=list(context.context.keys()),
                        input_size=len(str(context.input_data)),
                        output_size=len(str(result.output))
                    )
            
            execution_time = time.time() - start_time
            
            return FlowResult(
                flow_id=context.flow_id,
                success=True,
                result={
                    "results": [
                        {
                            "rule_id": r.rule_id,
                            "success": r.success,
                            "output": r.output,
                            "execution_time": r.execution_time,
                            "error_message": r.error_message
                        } for r in results
                    ],
                    "total_rules_executed": len(results),
                    "execution_time": execution_time
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"规则执行失败: {e}")
            
            return FlowResult(
                flow_id=context.flow_id,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        return isinstance(input_data, dict) and len(input_data) > 0


class KnowledgeExtractionProcessor(FlowProcessor):
    """知识提取处理器"""
    
    def __init__(self, knowledge_extractor: KnowledgeExtractor):
        super().__init__("Knowledge Extraction Processor")
        self.knowledge_extractor = knowledge_extractor
    
    async def process(self, context: FlowContext) -> FlowResult:
        """执行知识提取处理"""
        start_time = time.time()
        
        try:
            # 验证输入
            if not self.validate_input(context.input_data):
                raise ValueError("输入数据验证失败")
            
            llm_response = context.input_data.get('llm_response', '')
            extraction_context = context.input_data.get('context', {})
            
            # 执行知识提取
            patterns, rules = self.knowledge_extractor.extract_from_llm_response(
                llm_response, extraction_context
            )
            
            # 存储知识
            self.knowledge_extractor.store_knowledge(patterns, rules)
            
            execution_time = time.time() - start_time
            
            return FlowResult(
                flow_id=context.flow_id,
                success=True,
                result={
                    "patterns_extracted": len(patterns),
                    "rules_generated": len(rules),
                    "patterns": [
                        {
                            "pattern_id": p.pattern_id,
                            "pattern_type": p.pattern_type,
                            "confidence": p.confidence
                        } for p in patterns
                    ],
                    "rules": [
                        {
                            "rule_id": r.rule_id,
                            "rule_type": r.rule_type,
                            "priority": r.priority,
                            "accuracy": r.accuracy
                        } for r in rules
                    ],
                    "execution_time": execution_time
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"知识提取失败: {e}")
            
            return FlowResult(
                flow_id=context.flow_id,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        return (isinstance(input_data, dict) and 
                'llm_response' in input_data and 
                input_data['llm_response'])


class OptimizationProcessor(FlowProcessor):
    """优化处理器"""
    
    def __init__(self, adaptive_optimizer: AdaptiveOptimizer, cache_manager: RuleCacheManager):
        super().__init__("Optimization Processor")
        self.adaptive_optimizer = adaptive_optimizer
        self.cache_manager = cache_manager
    
    async def process(self, context: FlowContext) -> FlowResult:
        """执行优化处理"""
        start_time = time.time()
        
        try:
            # 验证输入
            if not self.validate_input(context.input_data):
                raise ValueError("输入数据验证失败")
            
            optimization_type = context.input_data.get('optimization_type', 'general')
            
            if optimization_type == 'cache':
                # 缓存优化
                target_memory = context.input_data.get('target_memory_mb', 150)
                self.cache_manager.optimize_caches(target_memory)
                optimization_result = {"cache_optimized": True}
                
            elif optimization_type == 'pipeline':
                # 流程优化
                current_pipeline = context.input_data.get('current_pipeline')
                if current_pipeline:
                    optimized_pipeline = self.adaptive_optimizer.optimize_processing_pipeline(
                        context.input_data, current_pipeline
                    )
                    optimization_result = {"pipeline_optimized": True, "pipeline": optimized_pipeline}
                else:
                    optimization_result = {"pipeline_optimized": False, "error": "No pipeline provided"}
                    
            else:
                # 通用优化
                optimization_result = {"general_optimization": True}
            
            execution_time = time.time() - start_time
            
            return FlowResult(
                flow_id=context.flow_id,
                success=True,
                result={
                    "optimization_type": optimization_type,
                    "optimization_result": optimization_result,
                    "execution_time": execution_time
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"优化处理失败: {e}")
            
            return FlowResult(
                flow_id=context.flow_id,
                success=False,
                error_message=str(e),
                execution_time=execution_time
            )
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入数据"""
        return isinstance(input_data, dict) and 'optimization_type' in input_data


class FlowManager:
    """流程管理器"""
    
    def __init__(self):
        self.processors: Dict[FlowType, FlowProcessor] = {}
        self.active_flows: Dict[str, FlowContext] = {}
        self.flow_history: List[FlowContext] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.lock = threading.Lock()
    
    def register_processor(self, flow_type: FlowType, processor: FlowProcessor):
        """注册流程处理器"""
        with self.lock:
            self.processors[flow_type] = processor
            logger.info(f"注册流程处理器: {flow_type.value} -> {processor.name}")
    
    def unregister_processor(self, flow_type: FlowType):
        """注销流程处理器"""
        with self.lock:
            if flow_type in self.processors:
                del self.processors[flow_type]
                logger.info(f"注销流程处理器: {flow_type.value}")
    
    async def execute_flow(self, flow_type: FlowType, input_data: Dict[str, Any], 
                          context: Dict[str, Any] = None, metadata: Dict[str, Any] = None) -> FlowResult:
        """执行流程"""
        flow_id = f"flow_{int(time.time() * 1000)}"
        
        # 创建流程上下文
        flow_context = FlowContext(
            flow_id=flow_id,
            flow_type=flow_type,
            status=FlowStatus.PENDING,
            input_data=input_data,
            context=context or {},
            metadata=metadata or {}
        )
        
        # 注册流程
        with self.lock:
            self.active_flows[flow_id] = flow_context
        
        try:
            # 获取处理器
            processor = self.processors.get(flow_type)
            if not processor:
                raise ValueError(f"未找到流程类型 {flow_type.value} 的处理器")
            
            # 更新状态
            flow_context.status = FlowStatus.RUNNING
            flow_context.started_at = time.time()
            
            # 执行处理
            result = await processor.process(flow_context)
            
            # 更新状态
            flow_context.status = FlowStatus.COMPLETED if result.success else FlowStatus.FAILED
            flow_context.completed_at = time.time()
            flow_context.result = result.result
            flow_context.error_message = result.error_message
            
            return result
            
        except Exception as e:
            # 更新状态
            flow_context.status = FlowStatus.FAILED
            flow_context.completed_at = time.time()
            flow_context.error_message = str(e)
            
            logger.error(f"流程执行失败: {e}")
            
            return FlowResult(
                flow_id=flow_id,
                success=False,
                error_message=str(e)
            )
        
        finally:
            # 移动到历史记录
            with self.lock:
                if flow_id in self.active_flows:
                    self.flow_history.append(self.active_flows[flow_id])
                    del self.active_flows[flow_id]
                    
                    # 限制历史记录数量
                    if len(self.flow_history) > 1000:
                        self.flow_history = self.flow_history[-1000:]
    
    def get_flow_status(self, flow_id: str) -> Optional[FlowContext]:
        """获取流程状态"""
        with self.lock:
            # 先检查活动流程
            if flow_id in self.active_flows:
                return self.active_flows[flow_id]
            
            # 再检查历史记录
            for flow in self.flow_history:
                if flow.flow_id == flow_id:
                    return flow
            
            return None
    
    def cancel_flow(self, flow_id: str) -> bool:
        """取消流程"""
        with self.lock:
            if flow_id in self.active_flows:
                flow = self.active_flows[flow_id]
                flow.status = FlowStatus.CANCELLED
                flow.completed_at = time.time()
                
                # 移动到历史记录
                self.flow_history.append(flow)
                del self.active_flows[flow_id]
                
                logger.info(f"流程已取消: {flow_id}")
                return True
            
            return False
    
    def get_active_flows(self) -> List[FlowContext]:
        """获取活动流程列表"""
        with self.lock:
            return list(self.active_flows.values())
    
    def get_flow_history(self, limit: int = 100) -> List[FlowContext]:
        """获取流程历史"""
        with self.lock:
            return self.flow_history[-limit:]


class BlitzkriegFlowSDK:
    """BlitzkriegFlow SDK主类"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # 初始化核心组件
        self.rule_engine = RuleEngine()
        self.priority_manager = RulePriorityManager()
        self.cache_manager = RuleCacheManager()
        self.knowledge_extractor = KnowledgeExtractor()
        self.adaptive_optimizer = AdaptiveOptimizer()
        
        # 初始化流程管理器
        self.flow_manager = FlowManager()
        
        # 注册默认处理器
        self._register_default_processors()
        
        logger.info("BlitzkriegFlow SDK 初始化完成")
    
    def _register_default_processors(self):
        """注册默认处理器"""
        # 规则执行处理器
        rule_processor = RuleExecutionProcessor(self.rule_engine, self.priority_manager)
        self.flow_manager.register_processor(FlowType.RULE_EXECUTION, rule_processor)
        
        # 知识提取处理器
        knowledge_processor = KnowledgeExtractionProcessor(self.knowledge_extractor)
        self.flow_manager.register_processor(FlowType.KNOWLEDGE_EXTRACTION, knowledge_processor)
        
        # 优化处理器
        optimization_processor = OptimizationProcessor(self.adaptive_optimizer, self.cache_manager)
        self.flow_manager.register_processor(FlowType.OPTIMIZATION, optimization_processor)
    
    # 规则管理方法
    def add_rule(self, rule: EngineRule) -> bool:
        """添加规则"""
        success = self.rule_engine.add_rule(rule)
        if success:
            self.cache_manager.cache_rule(rule)
        return success
    
    def update_rule(self, rule: EngineRule) -> bool:
        """更新规则"""
        success = self.rule_engine.update_rule(rule)
        if success:
            self.cache_manager.invalidate_rule(rule.rule_id)
            self.cache_manager.cache_rule(rule)
        return success
    
    def remove_rule(self, rule_id: str) -> bool:
        """删除规则"""
        success = self.rule_engine.remove_rule(rule_id)
        if success:
            self.cache_manager.invalidate_rule(rule_id)
        return success
    
    def get_rule(self, rule_id: str) -> Optional[EngineRule]:
        """获取规则"""
        return self.rule_engine.rule_library.get_rule(rule_id)
    
    def list_rules(self, tag: Optional[str] = None, enabled: Optional[bool] = None) -> List[EngineRule]:
        """列出规则"""
        if tag:
            return self.rule_engine.rule_library.get_rules_by_tag(tag)
        elif enabled is not None:
            if enabled:
                return self.rule_engine.rule_library.get_enabled_rules()
            else:
                all_rules = self.rule_engine.rule_library.get_all_rules()
                return [r for r in all_rules if not r.enabled]
        else:
            return self.rule_engine.rule_library.get_all_rules()
    
    # 规则执行方法
    async def execute_rules(self, data: Dict[str, Any], context: Dict[str, Any] = None, 
                           max_rules: int = 10) -> FlowResult:
        """执行规则"""
        return await self.flow_manager.execute_flow(
            flow_type=FlowType.RULE_EXECUTION,
            input_data=data,
            context=context,
            metadata={'max_rules': max_rules}
        )
    
    def execute_rules_sync(self, data: Dict[str, Any], context: Dict[str, Any] = None, 
                          max_rules: int = 10) -> FlowResult:
        """同步执行规则"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(
                self.execute_rules(data, context, max_rules)
            )
        finally:
            loop.close()
    
    # 知识提取方法
    async def extract_knowledge(self, llm_response: str, context: Dict[str, Any] = None) -> FlowResult:
        """提取知识"""
        input_data = {
            'llm_response': llm_response,
            'context': context or {}
        }
        
        return await self.flow_manager.execute_flow(
            flow_type=FlowType.KNOWLEDGE_EXTRACTION,
            input_data=input_data
        )
    
    # 优化方法
    async def optimize_system(self, optimization_type: str = 'general', 
                            optimization_params: Dict[str, Any] = None) -> FlowResult:
        """优化系统"""
        input_data = {
            'optimization_type': optimization_type,
            **(optimization_params or {})
        }
        
        return await self.flow_manager.execute_flow(
            flow_type=FlowType.OPTIMIZATION,
            input_data=input_data
        )
    
    # 反馈方法
    def submit_feedback(self, rule_id: str, feedback_type: str, score: float, 
                       comment: str = None, context: Dict[str, Any] = None):
        """提交反馈"""
        self.priority_manager.update_user_feedback(rule_id, score)
        logger.info(f"收到反馈 - 规则: {rule_id}, 类型: {feedback_type}, 分数: {score}")
    
    # 统计方法
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "rule_engine": self.rule_engine.get_rule_stats(),
            "cache": self.cache_manager.get_cache_stats(),
            "priority_manager": self.priority_manager.get_manager_stats(),
            "knowledge_extractor": self.knowledge_extractor.get_knowledge_stats(),
            "adaptive_optimizer": self.adaptive_optimizer.get_optimization_stats(),
            "flow_manager": {
                "active_flows": len(self.flow_manager.get_active_flows()),
                "total_flows": len(self.flow_manager.flow_history)
            }
        }
    
    def get_rule_stats(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """获取规则统计"""
        rule = self.get_rule(rule_id)
        if rule:
            return self.priority_manager.get_priority_analysis(rule)
        return None
    
    # 缓存管理方法
    def cache_rule(self, rule: EngineRule) -> bool:
        """缓存规则"""
        return self.cache_manager.cache_rule(rule)
    
    def get_cached_rule(self, rule_id: str) -> Optional[EngineRule]:
        """获取缓存的规则"""
        return self.cache_manager.get_rule(rule_id)
    
    def clear_cache(self):
        """清空缓存"""
        self.cache_manager.clear_all()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return self.cache_manager.get_cache_stats()
    
    # 流程管理方法
    def get_flow_status(self, flow_id: str) -> Optional[FlowContext]:
        """获取流程状态"""
        return self.flow_manager.get_flow_status(flow_id)
    
    def cancel_flow(self, flow_id: str) -> bool:
        """取消流程"""
        return self.flow_manager.cancel_flow(flow_id)
    
    def get_active_flows(self) -> List[FlowContext]:
        """获取活动流程"""
        return self.flow_manager.get_active_flows()
    
    def get_flow_history(self, limit: int = 100) -> List[FlowContext]:
        """获取流程历史"""
        return self.flow_manager.get_flow_history(limit)
    
    # 自定义处理器方法
    def register_custom_processor(self, processor: FlowProcessor):
        """注册自定义处理器"""
        self.flow_manager.register_processor(FlowType.CUSTOM, processor)
    
    async def execute_custom_flow(self, processor: FlowProcessor, input_data: Dict[str, Any], 
                                context: Dict[str, Any] = None) -> FlowResult:
        """执行自定义流程"""
        # 临时注册处理器
        temp_flow_type = FlowType.CUSTOM
        self.flow_manager.register_processor(temp_flow_type, processor)
        
        try:
            return await self.flow_manager.execute_flow(
                flow_type=temp_flow_type,
                input_data=input_data,
                context=context
            )
        finally:
            # 清理临时处理器
            self.flow_manager.unregister_processor(temp_flow_type)
    
    # 导入导出方法
    def export_rules(self, format: str = 'json') -> str:
        """导出规则"""
        return self.rule_engine.export_rules(format)
    
    def import_rules(self, rules_data: str, format: str = 'json') -> int:
        """导入规则"""
        return self.rule_engine.import_rules(rules_data, format)
    
    # 上下文建议方法
    def get_context_suggestions(self, context_keys: List[str], top_k: int = 5) -> List[tuple]:
        """获取上下文建议"""
        return self.priority_manager.get_context_suggestions(context_keys, top_k)
    
    # 优化建议方法
    def get_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """获取优化建议"""
        return self.cache_manager.get_optimization_suggestions()
    
    # 配置方法
    def update_config(self, config: Dict[str, Any]):
        """更新配置"""
        self.config.update(config)
        logger.info("配置已更新")
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config.copy()
    
    # 清理方法
    def cleanup(self):
        """清理资源"""
        try:
            # 取消所有活动流程
            active_flows = self.get_active_flows()
            for flow in active_flows:
                self.cancel_flow(flow.flow_id)
            
            # 清空缓存
            self.clear_cache()
            
            # 关闭线程池
            self.flow_manager.executor.shutdown(wait=True)
            
            logger.info("BlitzkriegFlow SDK 清理完成")
            
        except Exception as e:
            logger.error(f"清理资源失败: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.cleanup()


# 便捷函数
def create_sdk(config: Optional[Dict[str, Any]] = None) -> BlitzkriegFlowSDK:
    """创建SDK实例"""
    return BlitzkriegFlowSDK(config)


def create_rule(rule_id: str, name: str, description: str, conditions: List[Dict[str, Any]], 
               actions: List[Dict[str, Any]], priority: float = 0.5, confidence: float = 0.8,
               tags: List[str] = None) -> EngineRule:
    """创建规则"""
    # 转换条件
    rule_conditions = [
        RuleCondition(
            field=c['field'],
            operator=c['operator'],
            value=c['value'],
            weight=c.get('weight', 1.0)
        ) for c in conditions
    ]
    
    # 转换动作
    rule_actions = [
        RuleAction(
            action_type=a['action_type'],
            parameters=a['parameters'],
            priority=a.get('priority', 1.0)
        ) for a in actions
    ]
    
    return EngineRule(
        rule_id=rule_id,
        name=name,
        description=description,
        conditions=rule_conditions,
        actions=rule_actions,
        priority=priority,
        confidence=confidence,
        created_at=time.time(),
        updated_at=time.time(),
        tags=tags or []
    ) 