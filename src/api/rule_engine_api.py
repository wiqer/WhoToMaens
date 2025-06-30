"""
规则引擎RESTful API接口模块
提供规则管理、查询、执行、反馈、统计、缓存清理和优化触发等接口
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import logging
import time
from datetime import datetime

from ..core.rule_engine import RuleEngine, EngineRule, RuleCondition, RuleAction
from ..core.rule_priority_manager import RulePriorityManager
from ..core.rule_cache_manager import RuleCacheManager

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="规则引擎API",
    description="嵌入式规则引擎RESTful API接口",
    version="1.0.0"
)

# 全局实例
rule_engine = RuleEngine()
priority_manager = RulePriorityManager()
cache_manager = RuleCacheManager()


# Pydantic模型
class RuleConditionModel(BaseModel):
    field: str
    operator: str
    value: Any
    weight: float = 1.0


class RuleActionModel(BaseModel):
    action_type: str
    parameters: Dict[str, Any]
    priority: float = 1.0


class RuleModel(BaseModel):
    rule_id: str
    name: str
    description: str
    conditions: List[RuleConditionModel]
    actions: List[RuleActionModel]
    priority: float = 0.5
    confidence: float = 0.8
    tags: List[str] = Field(default_factory=list)
    enabled: bool = True


class RuleCreateModel(BaseModel):
    name: str
    description: str
    conditions: List[RuleConditionModel]
    actions: List[RuleActionModel]
    priority: float = 0.5
    confidence: float = 0.8
    tags: List[str] = Field(default_factory=list)
    enabled: bool = True


class RuleUpdateModel(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    conditions: Optional[List[RuleConditionModel]] = None
    actions: Optional[List[RuleActionModel]] = None
    priority: Optional[float] = None
    confidence: Optional[float] = None
    tags: Optional[List[str]] = None
    enabled: Optional[bool] = None


class ExecutionRequestModel(BaseModel):
    data: Dict[str, Any]
    context: Dict[str, Any] = Field(default_factory=dict)
    max_rules: int = 10


class ExecutionResponseModel(BaseModel):
    success: bool
    results: List[Dict[str, Any]]
    execution_time: float
    rules_executed: int
    timestamp: datetime


class FeedbackModel(BaseModel):
    rule_id: str
    feedback_type: str  # 'accuracy', 'performance', 'usefulness'
    score: float  # 0-1
    comment: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class CacheStatsModel(BaseModel):
    rule_cache: Dict[str, Any]
    result_cache: Dict[str, Any]
    total_memory_mb: float


class OptimizationRequestModel(BaseModel):
    target_memory_mb: int = 150
    optimize_ttl: bool = False
    preload_rules: bool = False


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


# 规则管理接口
@app.post("/rules", response_model=Dict[str, Any])
async def create_rule(rule_data: RuleCreateModel):
    """创建新规则"""
    try:
        # 生成规则ID
        rule_id = f"rule_{int(time.time() * 1000)}"
        
        # 转换条件
        conditions = [
            RuleCondition(
                field=c.field,
                operator=c.operator,
                value=c.value,
                weight=c.weight
            ) for c in rule_data.conditions
        ]
        
        # 转换动作
        actions = [
            RuleAction(
                action_type=a.action_type,
                parameters=a.parameters,
                priority=a.priority
            ) for a in rule_data.actions
        ]
        
        # 创建规则
        rule = EngineRule(
            rule_id=rule_id,
            name=rule_data.name,
            description=rule_data.description,
            conditions=conditions,
            actions=actions,
            priority=rule_data.priority,
            confidence=rule_data.confidence,
            created_at=time.time(),
            updated_at=time.time(),
            tags=rule_data.tags,
            enabled=rule_data.enabled
        )
        
        # 添加到规则引擎
        success = rule_engine.add_rule(rule)
        
        if success:
            # 缓存规则
            cache_manager.cache_rule(rule)
            
            return {
                "success": True,
                "rule_id": rule_id,
                "message": "规则创建成功"
            }
        else:
            raise HTTPException(status_code=400, detail="规则创建失败")
            
    except Exception as e:
        logger.error(f"创建规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建规则失败: {str(e)}")


@app.get("/rules", response_model=List[Dict[str, Any]])
async def list_rules(
    tag: Optional[str] = Query(None, description="按标签过滤"),
    enabled: Optional[bool] = Query(None, description="按启用状态过滤"),
    search: Optional[str] = Query(None, description="搜索关键词")
):
    """获取规则列表"""
    try:
        rules = []
        
        if tag:
            rules = rule_engine.rule_library.get_rules_by_tag(tag)
        elif search:
            rules = rule_engine.rule_library.search_rules(search)
        elif enabled is not None:
            if enabled:
                rules = rule_engine.rule_library.get_enabled_rules()
            else:
                all_rules = rule_engine.rule_library.get_all_rules()
                rules = [r for r in all_rules if not r.enabled]
        else:
            rules = rule_engine.rule_library.get_all_rules()
        
        # 转换为字典格式
        rule_list = []
        for rule in rules:
            rule_dict = {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "description": rule.description,
                "priority": rule.priority,
                "confidence": rule.confidence,
                "enabled": rule.enabled,
                "tags": rule.tags,
                "usage_count": rule.usage_count,
                "success_count": rule.success_count,
                "created_at": datetime.fromtimestamp(rule.created_at).isoformat(),
                "updated_at": datetime.fromtimestamp(rule.updated_at).isoformat()
            }
            rule_list.append(rule_dict)
        
        return rule_list
        
    except Exception as e:
        logger.error(f"获取规则列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取规则列表失败: {str(e)}")


@app.get("/rules/{rule_id}", response_model=Dict[str, Any])
async def get_rule(rule_id: str):
    """获取单个规则详情"""
    try:
        rule = rule_engine.rule_library.get_rule(rule_id)
        
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        
        # 获取优先级分析
        priority_analysis = priority_manager.get_priority_analysis(rule)
        
        rule_dict = {
            "rule_id": rule.rule_id,
            "name": rule.name,
            "description": rule.description,
            "conditions": [
                {
                    "field": c.field,
                    "operator": c.operator,
                    "value": c.value,
                    "weight": c.weight
                } for c in rule.conditions
            ],
            "actions": [
                {
                    "action_type": a.action_type,
                    "parameters": a.parameters,
                    "priority": a.priority
                } for a in rule.actions
            ],
            "priority": rule.priority,
            "confidence": rule.confidence,
            "enabled": rule.enabled,
            "tags": rule.tags,
            "usage_count": rule.usage_count,
            "success_count": rule.success_count,
            "created_at": datetime.fromtimestamp(rule.created_at).isoformat(),
            "updated_at": datetime.fromtimestamp(rule.updated_at).isoformat(),
            "priority_analysis": priority_analysis
        }
        
        return rule_dict
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取规则详情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取规则详情失败: {str(e)}")


@app.put("/rules/{rule_id}", response_model=Dict[str, Any])
async def update_rule(rule_id: str, rule_data: RuleUpdateModel):
    """更新规则"""
    try:
        existing_rule = rule_engine.rule_library.get_rule(rule_id)
        
        if not existing_rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        
        # 更新字段
        if rule_data.name is not None:
            existing_rule.name = rule_data.name
        if rule_data.description is not None:
            existing_rule.description = rule_data.description
        if rule_data.conditions is not None:
            existing_rule.conditions = [
                RuleCondition(
                    field=c.field,
                    operator=c.operator,
                    value=c.value,
                    weight=c.weight
                ) for c in rule_data.conditions
            ]
        if rule_data.actions is not None:
            existing_rule.actions = [
                RuleAction(
                    action_type=a.action_type,
                    parameters=a.parameters,
                    priority=a.priority
                ) for a in rule_data.actions
            ]
        if rule_data.priority is not None:
            existing_rule.priority = rule_data.priority
        if rule_data.confidence is not None:
            existing_rule.confidence = rule_data.confidence
        if rule_data.tags is not None:
            existing_rule.tags = rule_data.tags
        if rule_data.enabled is not None:
            existing_rule.enabled = rule_data.enabled
        
        existing_rule.updated_at = time.time()
        
        # 更新规则
        success = rule_engine.update_rule(existing_rule)
        
        if success:
            # 更新缓存
            cache_manager.invalidate_rule(rule_id)
            cache_manager.cache_rule(existing_rule)
            
            return {
                "success": True,
                "message": "规则更新成功"
            }
        else:
            raise HTTPException(status_code=400, detail="规则更新失败")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新规则失败: {str(e)}")


@app.delete("/rules/{rule_id}", response_model=Dict[str, Any])
async def delete_rule(rule_id: str):
    """删除规则"""
    try:
        success = rule_engine.remove_rule(rule_id)
        
        if success:
            # 清理缓存
            cache_manager.invalidate_rule(rule_id)
            
            return {
                "success": True,
                "message": "规则删除成功"
            }
        else:
            raise HTTPException(status_code=404, detail="规则不存在")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除规则失败: {str(e)}")


# 规则执行接口
@app.post("/execute", response_model=ExecutionResponseModel)
async def execute_rules(request: ExecutionRequestModel):
    """执行规则"""
    try:
        start_time = time.time()
        
        # 执行规则
        results = rule_engine.execute_rules(
            data=request.data,
            context=request.context,
            max_rules=request.max_rules
        )
        
        execution_time = time.time() - start_time
        
        # 记录执行统计
        for result in results:
            if result.success:
                priority_manager.record_rule_execution(
                    rule_id=result.rule_id,
                    success=True,
                    execution_time=result.execution_time,
                    context_keys=list(request.context.keys()),
                    input_size=len(str(request.data)),
                    output_size=len(str(result.output))
                )
        
        # 缓存结果
        cache_manager.cache_result(request.data, results)
        
        # 转换结果格式
        result_list = []
        for result in results:
            result_dict = {
                "rule_id": result.rule_id,
                "success": result.success,
                "output": result.output,
                "execution_time": result.execution_time,
                "error_message": result.error_message
            }
            result_list.append(result_dict)
        
        return ExecutionResponseModel(
            success=True,
            results=result_list,
            execution_time=execution_time,
            rules_executed=len(results),
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"规则执行失败: {e}")
        raise HTTPException(status_code=500, detail=f"规则执行失败: {str(e)}")


# 反馈接口
@app.post("/feedback", response_model=Dict[str, Any])
async def submit_feedback(feedback: FeedbackModel):
    """提交反馈"""
    try:
        # 更新用户反馈
        priority_manager.update_user_feedback(feedback.rule_id, feedback.score)
        
        # 记录反馈
        logger.info(f"收到反馈 - 规则: {feedback.rule_id}, 类型: {feedback.feedback_type}, 分数: {feedback.score}")
        
        return {
            "success": True,
            "message": "反馈提交成功"
        }
        
    except Exception as e:
        logger.error(f"提交反馈失败: {e}")
        raise HTTPException(status_code=500, detail=f"提交反馈失败: {str(e)}")


# 统计接口
@app.get("/stats", response_model=Dict[str, Any])
async def get_stats():
    """获取系统统计信息"""
    try:
        rule_stats = rule_engine.get_rule_stats()
        cache_stats = cache_manager.get_cache_stats()
        priority_stats = priority_manager.get_manager_stats()
        
        return {
            "rule_engine": rule_stats,
            "cache": cache_stats,
            "priority_manager": priority_stats,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")


@app.get("/stats/rules/{rule_id}", response_model=Dict[str, Any])
async def get_rule_stats(rule_id: str):
    """获取单个规则的统计信息"""
    try:
        rule = rule_engine.rule_library.get_rule(rule_id)
        
        if not rule:
            raise HTTPException(status_code=404, detail="规则不存在")
        
        priority_analysis = priority_manager.get_priority_analysis(rule)
        
        return {
            "rule_id": rule_id,
            "usage_stats": priority_analysis.get("usage_stats", {}),
            "priority_analysis": priority_analysis,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取规则统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取规则统计失败: {str(e)}")


# 缓存管理接口
@app.get("/cache/stats", response_model=CacheStatsModel)
async def get_cache_stats():
    """获取缓存统计信息"""
    try:
        stats = cache_manager.get_cache_stats()
        return CacheStatsModel(**stats)
        
    except Exception as e:
        logger.error(f"获取缓存统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")


@app.delete("/cache", response_model=Dict[str, Any])
async def clear_cache():
    """清空缓存"""
    try:
        cache_manager.clear_all()
        
        return {
            "success": True,
            "message": "缓存已清空"
        }
        
    except Exception as e:
        logger.error(f"清空缓存失败: {e}")
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")


@app.delete("/cache/rules/{rule_id}", response_model=Dict[str, Any])
async def invalidate_rule_cache(rule_id: str):
    """使规则缓存失效"""
    try:
        success = cache_manager.invalidate_rule(rule_id)
        
        if success:
            return {
                "success": True,
                "message": "规则缓存已失效"
            }
        else:
            return {
                "success": False,
                "message": "规则缓存不存在"
            }
            
    except Exception as e:
        logger.error(f"使规则缓存失效失败: {e}")
        raise HTTPException(status_code=500, detail=f"使规则缓存失效失败: {str(e)}")


# 优化接口
@app.post("/optimize", response_model=Dict[str, Any])
async def trigger_optimization(request: OptimizationRequestModel):
    """触发系统优化"""
    try:
        optimization_results = {}
        
        # 缓存优化
        if request.target_memory_mb:
            cache_manager.optimize_caches(request.target_memory_mb)
            optimization_results["cache_optimization"] = "completed"
        
        # 规则优先级优化
        enabled_rules = rule_engine.rule_library.get_enabled_rules()
        optimized_rules = priority_manager.optimize_rule_order(enabled_rules)
        optimization_results["priority_optimization"] = f"optimized {len(optimized_rules)} rules"
        
        # 获取优化建议
        suggestions = cache_manager.get_optimization_suggestions()
        optimization_results["suggestions"] = suggestions
        
        return {
            "success": True,
            "optimization_results": optimization_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"触发优化失败: {e}")
        raise HTTPException(status_code=500, detail=f"触发优化失败: {str(e)}")


@app.get("/optimize/suggestions", response_model=List[Dict[str, Any]])
async def get_optimization_suggestions():
    """获取优化建议"""
    try:
        suggestions = cache_manager.get_optimization_suggestions()
        return suggestions
        
    except Exception as e:
        logger.error(f"获取优化建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取优化建议失败: {str(e)}")


# 导入导出接口
@app.post("/rules/import", response_model=Dict[str, Any])
async def import_rules(rules_data: str = Body(..., media_type="application/json")):
    """导入规则"""
    try:
        imported_count = rule_engine.import_rules(rules_data, "json")
        
        return {
            "success": True,
            "imported_count": imported_count,
            "message": f"成功导入 {imported_count} 个规则"
        }
        
    except Exception as e:
        logger.error(f"导入规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"导入规则失败: {str(e)}")


@app.get("/rules/export")
async def export_rules(format: str = Query("json", description="导出格式")):
    """导出规则"""
    try:
        rules_data = rule_engine.export_rules(format)
        
        return JSONResponse(
            content={"rules": rules_data},
            media_type="application/json"
        )
        
    except Exception as e:
        logger.error(f"导出规则失败: {e}")
        raise HTTPException(status_code=500, detail=f"导出规则失败: {str(e)}")


# 上下文建议接口
@app.get("/context/suggestions", response_model=List[Dict[str, Any]])
async def get_context_suggestions(
    context_keys: List[str] = Query(..., description="上下文键列表"),
    top_k: int = Query(5, description="返回建议数量")
):
    """获取上下文建议"""
    try:
        suggestions = priority_manager.get_context_suggestions(context_keys, top_k)
        
        return [
            {
                "rule_id": rule_id,
                "relevance_score": score
            } for rule_id, score in suggestions
        ]
        
    except Exception as e:
        logger.error(f"获取上下文建议失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取上下文建议失败: {str(e)}")


# 错误处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "内部服务器错误"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 