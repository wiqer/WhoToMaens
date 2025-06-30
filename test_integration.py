#!/usr/bin/env python3
"""
WhoToMaens 集成测试脚本
验证所有核心模块的功能是否正常工作
"""

import sys
import os
import time
import json
import asyncio
from typing import Dict, Any

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_knowledge_extractor():
    """测试知识提取器"""
    print("🔍 测试知识提取器...")
    
    try:
        from src.core import KnowledgeExtractor
        
        extractor = KnowledgeExtractor()
        
        # 模拟LLM响应
        llm_response = {
            "features": [
                {"type": "color", "value": "red", "confidence": 0.9},
                {"type": "shape", "value": "circle", "confidence": 0.8}
            ],
            "classification": {
                "category": "geometric_shape",
                "confidence": 0.85
            },
            "rules": [
                {
                    "type": "classification",
                    "conditions": [{"field": "color", "operator": "eq", "value": "red"}],
                    "actions": [{"type": "classification", "target": "red_object"}],
                    "confidence": 0.8
                }
            ]
        }
        
        patterns, rules = extractor.extract_from_llm_response(
            json.dumps(llm_response),
            {"data_type": "image", "processing_stage": "analysis"}
        )
        
        print(f"✅ 知识提取器测试通过 - 提取到 {len(patterns)} 个模式，生成 {len(rules)} 条规则")
        return True
        
    except Exception as e:
        print(f"❌ 知识提取器测试失败: {e}")
        return False


def test_adaptive_optimizer():
    """测试自适应优化器"""
    print("⚡ 测试自适应优化器...")
    
    try:
        from src.core import AdaptiveOptimizer, ProcessingPipeline
        
        optimizer = AdaptiveOptimizer()
        
        # 创建处理流程
        pipeline = ProcessingPipeline(
            pipeline_id="test_pipeline",
            steps=[
                {"name": "feature_extraction", "method": "resnet"},
                {"name": "classification", "method": "svm"}
            ]
        )
        
        # 优化流程
        input_data = {"image_size": "large", "complexity": "high"}
        optimized_pipeline = optimizer.optimize_processing_pipeline(input_data, pipeline)
        
        print(f"✅ 自适应优化器测试通过 - 优化后流程步骤数: {len(optimized_pipeline.steps)}")
        return True
        
    except Exception as e:
        print(f"❌ 自适应优化器测试失败: {e}")
        return False


def test_rule_engine():
    """测试规则引擎"""
    print("🔧 测试规则引擎...")
    
    try:
        from src.core import RuleEngine, EngineRule, RuleCondition, RuleAction
        
        engine = RuleEngine()
        
        # 创建测试规则
        conditions = [
            RuleCondition(
                field="color",
                operator="eq",
                value="red",
                weight=1.0
            )
        ]
        
        actions = [
            RuleAction(
                action_type="classify",
                parameters={"field": "category", "target": "red_object"},
                priority=1.0
            )
        ]
        
        rule = EngineRule(
            rule_id="test_rule",
            name="Red Object Classifier",
            description="Classify red objects",
            conditions=conditions,
            actions=actions,
            priority=0.8,
            confidence=0.9,
            created_at=time.time(),
            updated_at=time.time()
        )
        
        # 添加规则
        engine.add_rule(rule)
        
        # 测试处理
        test_data = {"color": "red", "shape": "circle"}
        context = {"data_type": "image", "processing_stage": "analysis"}
        
        results = engine.execute_rules(test_data, context)
        
        print(f"✅ 规则引擎测试通过 - 执行了 {len(results)} 个规则")
        return True
        
    except Exception as e:
        print(f"❌ 规则引擎测试失败: {e}")
        return False


def test_priority_manager():
    """测试优先级管理器"""
    print("📊 测试优先级管理器...")
    
    try:
        from src.core import RulePriorityManager, EngineRule, RuleCondition, RuleAction
        
        priority_manager = RulePriorityManager()
        
        # 创建测试规则
        conditions = [
            RuleCondition(
                field="type",
                operator="eq",
                value="image",
                weight=1.0
            )
        ]
        
        actions = [
            RuleAction(
                action_type="classify",
                parameters={"field": "category", "target": "image_object"},
                priority=1.0
            )
        ]
        
        rule = EngineRule(
            rule_id="priority_test_rule",
            name="Image Classifier",
            description="Classify image objects",
            conditions=conditions,
            actions=actions,
            priority=0.6,
            confidence=0.8,
            created_at=time.time(),
            updated_at=time.time()
        )
        
        # 计算优先级
        context_keys = ["data_type", "processing_stage"]
        priority_score = priority_manager.calculate_priority(rule, context_keys)
        
        # 记录使用情况
        priority_manager.record_rule_execution(
            rule.rule_id,
            success=True,
            execution_time=0.1,
            context_keys=context_keys,
            input_size=10,
            output_size=5
        )
        
        print(f"✅ 优先级管理器测试通过 - 优先级分数: {priority_score:.3f}")
        return True
        
    except Exception as e:
        print(f"❌ 优先级管理器测试失败: {e}")
        return False


def test_cache_manager():
    """测试缓存管理器"""
    print("💾 测试缓存管理器...")
    
    try:
        from src.core import RuleCacheManager, EngineRule, RuleCondition, RuleAction
        
        cache_manager = RuleCacheManager()
        
        # 创建测试规则
        conditions = [
            RuleCondition(
                field="size",
                operator="gt",
                value=100,
                weight=1.0
            )
        ]
        
        actions = [
            RuleAction(
                action_type="transform",
                parameters={"source_field": "size", "target_field": "category", "transform_type": "classification"},
                priority=1.0
            )
        ]
        
        rule = EngineRule(
            rule_id="cache_test_rule",
            name="Size Classifier",
            description="Classify objects by size",
            conditions=conditions,
            actions=actions,
            priority=0.5,
            confidence=0.75,
            created_at=time.time(),
            updated_at=time.time()
        )
        
        # 缓存规则
        cache_manager.cache_rule(rule)
        
        # 缓存执行结果
        input_data = {"size": 150, "type": "image"}
        result = {"category": "large_image", "processed": True}
        cache_manager.cache_result(input_data, result)
        
        # 获取缓存
        cached_rule = cache_manager.get_rule(rule.rule_id)
        cached_result = cache_manager.get_result(input_data)
        
        print(f"✅ 缓存管理器测试通过 - 规则缓存: {cached_rule is not None}, 结果缓存: {cached_result is not None}")
        return True
        
    except Exception as e:
        print(f"❌ 缓存管理器测试失败: {e}")
        return False


async def test_sdk():
    """测试SDK"""
    print("🚀 测试SDK...")
    
    try:
        from src.sdk.blitzkrieg_flow_sdk import BlitzkriegFlowSDK
        from src.core import EngineRule, RuleCondition, RuleAction
        
        # 初始化SDK
        sdk = BlitzkriegFlowSDK()
        
        # 创建测试规则
        conditions = [
            RuleCondition(
                field="content_type",
                operator="eq",
                value="text",
                weight=1.0
            )
        ]
        
        actions = [
            RuleAction(
                action_type="classify",
                parameters={"field": "category", "target": "text_content"},
                priority=1.0
            )
        ]
        
        rule = EngineRule(
            rule_id="sdk_test_rule",
            name="Text Classifier",
            description="Classify text content",
            conditions=conditions,
            actions=actions,
            priority=0.7,
            confidence=0.85,
            created_at=time.time(),
            updated_at=time.time()
        )
        
        # 添加规则
        sdk.add_rule(rule)
        
        # 执行规则
        test_data = {"content_type": "text", "content": "Hello World"}
        context = {"user_type": "developer"}
        
        result = await sdk.execute_rules(test_data, context)
        
        print(f"✅ SDK测试通过 - 执行成功: {result.success}")
        return True
        
    except Exception as e:
        print(f"❌ SDK测试失败: {e}")
        return False


def test_api_models():
    """测试API模型"""
    print("🌐 测试API模型...")
    
    try:
        from src.api.rule_engine_api import (
            RuleCreateModel, RuleConditionModel, RuleActionModel,
            ExecutionRequestModel, ExecutionResponseModel, FeedbackModel
        )
        
        # 测试规则创建模型
        condition = RuleConditionModel(
            field="color",
            operator="eq",
            value="red",
            weight=1.0
        )
        
        action = RuleActionModel(
            action_type="classify",
            parameters={"field": "category", "target": "red_object"},
            priority=1.0
        )
        
        rule_create = RuleCreateModel(
            name="Red Object Classifier",
            description="Classify red objects",
            conditions=[condition],
            actions=[action],
            priority=0.8,
            confidence=0.9
        )
        
        # 测试执行请求模型
        execution_request = ExecutionRequestModel(
            data={"color": "red", "shape": "circle"},
            context={"data_type": "image"},
            max_rules=10
        )
        
        # 测试反馈模型
        feedback = FeedbackModel(
            rule_id="test_rule",
            feedback_type="accuracy",
            score=0.9,
            comment="Good classification"
        )
        
        print("✅ API模型测试通过")
        return True
        
    except Exception as e:
        print(f"❌ API模型测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 WhoToMaens 集成测试开始")
    print("=" * 50)
    
    test_results = []
    
    # 测试各个模块
    test_results.append(("知识提取器", test_knowledge_extractor()))
    test_results.append(("自适应优化器", test_adaptive_optimizer()))
    test_results.append(("规则引擎", test_rule_engine()))
    test_results.append(("优先级管理器", test_priority_manager()))
    test_results.append(("缓存管理器", test_cache_manager()))
    test_results.append(("API模型", test_api_models()))
    
    # 测试SDK（异步）
    sdk_result = asyncio.run(test_sdk())
    test_results.append(("SDK", sdk_result))
    
    # 输出测试结果
    print("\n" + "=" * 50)
    print("📋 测试结果汇总:")
    print("=" * 50)
    
    passed = 0
    total = len(test_results)
    
    for module_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{module_name:15} : {status}")
        if result:
            passed += 1
    
    print("=" * 50)
    print(f"总计: {passed}/{total} 个模块测试通过")
    
    if passed == total:
        print("🎉 所有模块测试通过！系统运行正常。")
        return 0
    else:
        print("⚠️  部分模块测试失败，请检查相关代码。")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 