"""
规则引擎演示脚本
展示知识提取器、自适应优化器、规则引擎、优先级管理、缓存管理和SDK的使用
"""

import asyncio
import time
import json
from typing import Dict, List, Any

# 导入核心组件
from src.core import (
    KnowledgeExtractor,
    AdaptiveOptimizer,
    RuleEngine,
    RulePriorityManager,
    RuleCacheManager,
    EngineRule,
    RuleCondition,
    RuleAction
)

# 导入SDK
from src.sdk.blitzkrieg_flow_sdk import BlitzkriegFlowSDK, create_rule


def demo_knowledge_extractor():
    """演示知识提取器"""
    print("=== 知识提取器演示 ===")
    
    # 创建知识提取器
    extractor = KnowledgeExtractor()
    
    # 模拟LLM响应
    llm_response = """
    {
        "features": [
            {
                "type": "color",
                "value": "red",
                "confidence": 0.9
            },
            {
                "type": "size",
                "value": "large",
                "confidence": 0.8
            }
        ],
        "classification": {
            "category": "vehicle",
            "subcategory": "car",
            "confidence": 0.85
        },
        "processing_steps": [
            {
                "step": "color_detection",
                "method": "hsv_threshold",
                "confidence": 0.9
            }
        ],
        "rules": [
            {
                "type": "classification",
                "conditions": ["color=red", "size=large"],
                "actions": ["classify=vehicle"],
                "confidence": 0.8
            }
        ]
    }
    """
    
    # 提取知识
    patterns, rules = extractor.extract_from_llm_response(llm_response, {"context": "image_analysis"})
    
    print(f"提取到 {len(patterns)} 个模式:")
    for pattern in patterns:
        print(f"  - {pattern.pattern_type}: {pattern.content}")
    
    print(f"生成 {len(rules)} 个规则:")
    for rule in rules:
        print(f"  - {rule.rule_type}: {rule.conditions}")
    
    # 获取统计信息
    stats = extractor.get_knowledge_stats()
    print(f"知识提取统计: {stats}")


def demo_adaptive_optimizer():
    """演示自适应优化器"""
    print("\n=== 自适应优化器演示 ===")
    
    # 创建自适应优化器
    optimizer = AdaptiveOptimizer()
    
    # 模拟性能指标
    metrics = optimizer.metrics_collector.collect()
    metrics.processing_time = 2.5  # 模拟较长的处理时间
    metrics.memory_usage = 85.0    # 模拟高内存使用
    metrics.accuracy = 0.75        # 模拟较低准确率
    
    # 分析瓶颈
    bottlenecks = optimizer.bottleneck_analyzer.analyze_bottlenecks(metrics)
    print(f"检测到的瓶颈: {bottlenecks}")
    
    # 检查是否需要优化
    should_optimize = optimizer.optimization_trigger.should_optimize(bottlenecks, metrics)
    print(f"是否需要优化: {should_optimize}")
    
    if should_optimize:
        # 生成优化策略
        strategies = optimizer.strategy_generator.generate_optimization_strategies(bottlenecks, metrics)
        print(f"生成的优化策略数量: {len(strategies)}")
        
        for strategy in strategies:
            print(f"  - {strategy.strategy_type}: {strategy.description}")
    
    # 获取优化统计
    stats = optimizer.get_optimization_stats()
    print(f"优化统计: {stats}")


def demo_rule_engine():
    """演示规则引擎"""
    print("\n=== 规则引擎演示 ===")
    
    # 创建规则引擎
    engine = RuleEngine()
    
    # 创建示例规则
    conditions = [
        RuleCondition(field="color", operator="eq", value="red", weight=1.0),
        RuleCondition(field="size", operator="eq", value="large", weight=0.8)
    ]
    
    actions = [
        RuleAction(
            action_type="classify",
            parameters={"categories": {"vehicle": {"color": "red", "size": "large"}}},
            priority=1.0
        ),
        RuleAction(
            action_type="extract",
            parameters={"field": "color", "pattern": r"red"},
            priority=0.8
        )
    ]
    
    rule = EngineRule(
        rule_id="rule_001",
        name="红色大物体分类规则",
        description="识别红色大物体并分类为车辆",
        conditions=conditions,
        actions=actions,
        priority=0.9,
        confidence=0.85,
        created_at=time.time(),
        updated_at=time.time(),
        tags=["classification", "color", "size"]
    )
    
    # 添加规则
    success = engine.add_rule(rule)
    print(f"规则添加成功: {success}")
    
    # 执行规则
    test_data = {
        "color": "red",
        "size": "large",
        "shape": "rectangular"
    }
    
    results = engine.execute_rules(test_data, {"context": "image_analysis"})
    print(f"规则执行结果数量: {len(results)}")
    
    for result in results:
        print(f"  - 规则 {result.rule_id}: {'成功' if result.success else '失败'}")
        if result.success:
            print(f"    输出: {result.output}")
    
    # 获取规则统计
    stats = engine.get_rule_stats()
    print(f"规则引擎统计: {stats}")


def demo_priority_manager():
    """演示优先级管理器"""
    print("\n=== 优先级管理器演示 ===")
    
    # 创建优先级管理器
    priority_manager = RulePriorityManager()
    
    # 创建示例规则
    rule = EngineRule(
        rule_id="rule_002",
        name="测试规则",
        description="用于测试优先级管理的规则",
        conditions=[RuleCondition(field="test", operator="eq", value="true")],
        actions=[RuleAction(action_type="test", parameters={})],
        priority=0.5,
        confidence=0.8,
        created_at=time.time(),
        updated_at=time.time()
    )
    
    # 记录规则使用
    priority_manager.record_rule_execution(
        rule_id=rule.rule_id,
        success=True,
        execution_time=0.1,
        context_keys=["test_context"],
        input_size=100,
        output_size=50
    )
    
    # 计算优先级
    priority = priority_manager.calculate_priority(rule, ["test_context"])
    print(f"规则优先级: {priority:.3f}")
    
    # 获取优先级分析
    analysis = priority_manager.get_priority_analysis(rule, ["test_context"])
    print(f"优先级分析: {analysis}")
    
    # 获取上下文建议
    suggestions = priority_manager.get_context_suggestions(["test_context"], top_k=3)
    print(f"上下文建议: {suggestions}")


def demo_cache_manager():
    """演示缓存管理器"""
    print("\n=== 缓存管理器演示 ===")
    
    # 创建缓存管理器
    cache_manager = RuleCacheManager()
    
    # 创建示例规则
    rule = EngineRule(
        rule_id="rule_003",
        name="缓存测试规则",
        description="用于测试缓存管理的规则",
        conditions=[RuleCondition(field="cache_test", operator="eq", value="true")],
        actions=[RuleAction(action_type="cache_test", parameters={})],
        priority=0.6,
        confidence=0.9,
        created_at=time.time(),
        updated_at=time.time()
    )
    
    # 缓存规则
    cache_success = cache_manager.cache_rule(rule)
    print(f"规则缓存成功: {cache_success}")
    
    # 获取缓存的规则
    cached_rule = cache_manager.get_rule(rule.rule_id)
    print(f"获取缓存规则: {'成功' if cached_rule else '失败'}")
    
    # 缓存结果
    test_data = {"cache_test": "true"}
    test_result = {"result": "cached_data"}
    result_cache_success = cache_manager.cache_result(test_data, test_result)
    print(f"结果缓存成功: {result_cache_success}")
    
    # 获取缓存的结果
    cached_result = cache_manager.get_result(test_data)
    print(f"获取缓存结果: {'成功' if cached_result else '失败'}")
    
    # 获取缓存统计
    stats = cache_manager.get_cache_stats()
    print(f"缓存统计: {stats}")
    
    # 获取优化建议
    suggestions = cache_manager.get_optimization_suggestions()
    print(f"优化建议: {suggestions}")


async def demo_sdk():
    """演示SDK使用"""
    print("\n=== BlitzkriegFlow SDK演示 ===")
    
    # 创建SDK实例
    sdk = BlitzkriegFlowSDK()
    
    # 创建规则
    rule = create_rule(
        rule_id="sdk_rule_001",
        name="SDK测试规则",
        description="通过SDK创建的测试规则",
        conditions=[
            {"field": "sdk_test", "operator": "eq", "value": "true", "weight": 1.0}
        ],
        actions=[
            {
                "action_type": "classify",
                "parameters": {"category": "sdk_test"},
                "priority": 1.0
            }
        ],
        priority=0.8,
        confidence=0.9,
        tags=["sdk", "test"]
    )
    
    # 添加规则
    add_success = sdk.add_rule(rule)
    print(f"SDK添加规则成功: {add_success}")
    
    # 异步执行规则
    test_data = {"sdk_test": "true", "data": "test_value"}
    result = await sdk.execute_rules(test_data, {"context": "sdk_demo"})
    print(f"SDK规则执行结果: {'成功' if result.success else '失败'}")
    if result.success:
        print(f"  执行时间: {result.execution_time:.3f}秒")
        print(f"  结果: {result.result}")
    
    # 知识提取
    llm_response = '{"features": [{"type": "test", "value": "sdk_test"}]}'
    knowledge_result = await sdk.extract_knowledge(llm_response, {"context": "sdk_demo"})
    print(f"SDK知识提取结果: {'成功' if knowledge_result.success else '失败'}")
    
    # 系统优化
    optimization_result = await sdk.optimize_system("cache", {"target_memory_mb": 100})
    print(f"SDK系统优化结果: {'成功' if optimization_result.success else '失败'}")
    
    # 提交反馈
    sdk.submit_feedback("sdk_rule_001", "accuracy", 0.9, "测试反馈")
    print("SDK反馈提交完成")
    
    # 获取统计信息
    stats = sdk.get_stats()
    print(f"SDK统计信息: {stats}")
    
    # 清理资源
    sdk.cleanup()


def demo_integration():
    """演示组件集成"""
    print("\n=== 组件集成演示 ===")
    
    # 创建所有组件
    knowledge_extractor = KnowledgeExtractor()
    adaptive_optimizer = AdaptiveOptimizer()
    rule_engine = RuleEngine()
    priority_manager = RulePriorityManager()
    cache_manager = RuleCacheManager()
    
    # 模拟完整流程
    print("1. 从LLM响应中提取知识...")
    llm_response = '{"features": [{"type": "integration", "value": "test"}]}'
    patterns, rules = knowledge_extractor.extract_from_llm_response(llm_response, {})
    
    print("2. 将提取的规则添加到规则引擎...")
    for rule in rules:
        # 转换为EngineRule格式
        engine_rule = EngineRule(
            rule_id=f"integration_{rule.rule_id}",
            name=f"集成规则 {rule.rule_id}",
            description="从LLM响应中提取的规则",
            conditions=[RuleCondition(field="integration", operator="eq", value="test")],
            actions=[RuleAction(action_type="integration_test", parameters={})],
            priority=rule.priority,
            confidence=rule.accuracy,
            created_at=time.time(),
            updated_at=time.time(),
            tags=["integration", "extracted"]
        )
        
        rule_engine.add_rule(engine_rule)
        cache_manager.cache_rule(engine_rule)
    
    print("3. 执行规则并记录统计...")
    test_data = {"integration": "test", "data": "integration_demo"}
    results = rule_engine.execute_rules(test_data, {"context": "integration"})
    
    for result in results:
        if result.success:
            priority_manager.record_rule_execution(
                rule_id=result.rule_id,
                success=True,
                execution_time=result.execution_time,
                context_keys=["integration"],
                input_size=len(str(test_data)),
                output_size=len(str(result.output))
            )
    
    print("4. 检查性能并进行优化...")
    metrics = adaptive_optimizer.metrics_collector.collect()
    bottlenecks = adaptive_optimizer.bottleneck_analyzer.analyze_bottlenecks(metrics)
    
    if bottlenecks:
        print(f"  检测到瓶颈: {bottlenecks}")
        strategies = adaptive_optimizer.strategy_generator.generate_optimization_strategies(bottlenecks, metrics)
        print(f"  生成优化策略: {len(strategies)} 个")
    
    print("5. 获取各组件统计信息...")
    print(f"  知识提取器: {knowledge_extractor.get_knowledge_stats()}")
    print(f"  规则引擎: {rule_engine.get_rule_stats()}")
    print(f"  缓存管理器: {cache_manager.get_cache_stats()}")
    print(f"  自适应优化器: {adaptive_optimizer.get_optimization_stats()}")


def main():
    """主函数"""
    print("规则引擎系统演示")
    print("=" * 50)
    
    try:
        # 演示各个组件
        demo_knowledge_extractor()
        demo_adaptive_optimizer()
        demo_rule_engine()
        demo_priority_manager()
        demo_cache_manager()
        
        # 演示SDK
        asyncio.run(demo_sdk())
        
        # 演示组件集成
        demo_integration()
        
        print("\n" + "=" * 50)
        print("演示完成！")
        
    except Exception as e:
        print(f"演示过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 