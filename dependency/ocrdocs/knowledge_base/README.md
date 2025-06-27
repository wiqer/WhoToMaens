# MaoOCR 知识库索引

## 📚 文档概览

本知识库包含MaoOCR项目的核心技术知识、处理流程、最佳实践和经验总结。

## 📋 核心文档

### 1. 过程知识存储
- **[process_knowledge.md](./process_knowledge.md)**: 项目开发过程中的技术决策、经验教训和最佳实践
  - 架构设计决策
  - 技术实现经验
  - 性能测试经验
  - 部署经验
  - 未来规划经验

### 2. OCR处理流程
- **[ocr_processing_flow.md](./ocr_processing_flow.md)**: 智能OCR处理流程详细说明
  - 核心处理流程图
  - 置信度/语义检测机制
  - Layout LLM增强处理
  - 智能决策引擎
  - 性能优化策略
  - 配置参数说明
  - 监控指标
  - 最佳实践

### 3. OCR准确度增强方案
- **[ocr_accuracy_enhancement.md](./ocr_accuracy_enhancement.md)**: OCR准确度提升技术方案
  - 多引擎融合增强方案
  - 图像预处理增强
  - 深度学习增强
  - 后处理增强
  - 自适应学习增强
  - 性能监控与优化
  - 实施优先级和集成方案
  - **OCR纠错知识补充**: 预处理优化、多维度纠错策略、领域定制化方案

### 4. OCR纠错策略
- **[ocr_correction_strategies.md](./ocr_correction_strategies.md)**: OCR纠错策略详细文档
  - 渐进式纠错设计原则
  - 智能纠错选择器
  - 默认纠错器（低风险）
  - 高级纠错器（高精度）
  - 工程化纠错框架
  - 性能监控系统
  - 用户界面集成
  - 实施计划和预期效果
- **[ocr_correction_implementation_summary.md](./ocr_correction_implementation_summary.md)**: OCR纠错功能实现总结
  - 核心系统架构实现
  - 纠错策略实现详情
  - 词库系统集成
  - 技术实现和演示效果
  - 使用方式和性能指标
  - 工程化特点和核心价值

### 5. 词库工程能力
- **[vocabulary_engineering_summary.md](./vocabulary_engineering_summary.md)**: MaoOCR词库工程能力总结
  - 整体架构设计
  - 核心组件实现
  - 关键功能特性
  - OCR纠错集成
  - 性能优化特性
  - 自动化运维
  - 实际应用场景
  - 技术优势和性能指标
  - 未来发展方向

### 6. PP-OCRv5 OpenVINO集成方案
- **[pp_ocrv5_openvino_integration.md](./pp_ocrv5_openvino_integration.md)**: PP-OCRv5 + OpenVINO™ + LabVIEW 集成方案
  - PP-OCRv5技术优势分析
  - OpenVINO™优化优势
  - 对MaoOCR项目的潜在影响评估
  - 最小代价集成方案设计
  - 性能优化和批处理支持
  - LabVIEW平台集成方案
  - 实施计划和风险评估
  - 预期效果和成本分析

## 🔗 相关文档

### 技术架构
- **[技术架构文档](../technical-architecture.md)**: 系统整体架构设计
- **[性能优化文档](../performance-optimization.md)**: 性能优化策略和最佳实践
- **[监控系统文档](../MONITORING_SYSTEM.md)**: 系统监控和告警机制

### 技术分析
- **[OCR技术栈分析](../technical-analysis/ocr_technology_stack.md)**: OCR技术栈详细分析
- **[vLLM集成分析](../technical-analysis/vllm_integration.md)**: vLLM集成技术分析
- **[混合工程计划](../technical-analysis/hybrid_engineering_plan.md)**: 混合工程实施方案

### 前端后端集成
- **[前端后端集成文档](../frontend_backend_integration.md)**: 前后端集成方案
- **[前端后端优化计划](../FRONTEND_BACKEND_OPTIMIZATION_PLAN.md)**: 前后端优化策略
- **[WebSocket协议文档](../websocket_protocol.md)**: 实时通信协议

### 部署和配置
- **[配置管理文档](../configuration.md)**: 系统配置管理
- **[多平台部署文档](../deployment/multi_platform_deployment.md)**: 多平台部署方案

## 🎯 快速导航

### 新用户入门
1. 阅读 [技术架构文档](../technical-architecture.md) 了解系统整体架构
2. 查看 [OCR处理流程文档](./ocr_processing_flow.md) 理解核心处理逻辑
3. 参考 [过程知识存储](./process_knowledge.md) 了解开发经验

### 开发者参考
1. 查看 [技术分析文档](../technical-analysis/) 了解技术选型
2. 参考 [性能优化文档](../performance-optimization.md) 进行性能调优
3. 阅读 [监控系统文档](../MONITORING_SYSTEM.md) 了解监控机制
4. 学习 [OCR纠错策略](./ocr_correction_strategies.md) 实现纠错功能
5. 参考 [OCR纠错实现总结](./ocr_correction_implementation_summary.md) 了解具体实现
6. 研究 [词库工程能力总结](./vocabulary_engineering_summary.md) 了解词库系统架构
7. 研究 [PP-OCRv5 OpenVINO集成方案](./pp_ocrv5_openvino_integration.md) 了解新引擎集成

### 运维人员
1. 查看 [配置管理文档](../configuration.md) 进行系统配置
2. 参考 [部署文档](../deployment/) 进行系统部署
3. 阅读 [监控系统文档](../MONITORING_SYSTEM.md) 进行系统监控

## 📝 文档维护

### 更新原则
- 保持文档的时效性和准确性
- 及时记录技术决策和经验教训
- 定期更新最佳实践和配置参数
- 维护文档间的相互引用关系

### 贡献指南
- 新增技术决策时，请在 [process_knowledge.md](./process_knowledge.md) 中记录
- 更新处理流程时，请同步更新 [ocr_processing_flow.md](./ocr_processing_flow.md)
- 修改架构设计时，请更新相关技术文档
- 保持文档格式的一致性

## 🔍 搜索建议

### 按功能搜索
- **OCR处理**: 查看 [ocr_processing_flow.md](./ocr_processing_flow.md)
- **OCR准确度增强**: 查看 [ocr_accuracy_enhancement.md](./ocr_accuracy_enhancement.md)
- **OCR纠错策略**: 查看 [ocr_correction_strategies.md](./ocr_correction_strategies.md)
- **OCR纠错实现**: 查看 [ocr_correction_implementation_summary.md](./ocr_correction_implementation_summary.md)
- **词库工程能力**: 查看 [vocabulary_engineering_summary.md](./vocabulary_engineering_summary.md)
- **PP-OCRv5集成**: 查看 [pp_ocrv5_openvino_integration.md](./pp_ocrv5_openvino_integration.md)
- **性能优化**: 查看 [performance-optimization.md](../performance-optimization.md)
- **系统监控**: 查看 [MONITORING_SYSTEM.md](../MONITORING_SYSTEM.md)
- **部署配置**: 查看 [configuration.md](../configuration.md)

### 按技术搜索
- **Layout LLM**: 查看 [ocr_processing_flow.md](./ocr_processing_flow.md) 和 [FRONTEND_BACKEND_OPTIMIZATION_PLAN.md](../FRONTEND_BACKEND_OPTIMIZATION_PLAN.md)
- **多引擎融合**: 查看 [ocr_accuracy_enhancement.md](./ocr_accuracy_enhancement.md)
- **图像预处理**: 查看 [ocr_accuracy_enhancement.md](./ocr_accuracy_enhancement.md)
- **置信度融合**: 查看 [ocr_accuracy_enhancement.md](./ocr_accuracy_enhancement.md)
- **OCR纠错**: 查看 [ocr_correction_strategies.md](./ocr_correction_strategies.md)
- **语言模型纠错**: 查看 [ocr_correction_strategies.md](./ocr_correction_strategies.md)
- **规则基纠错**: 查看 [ocr_correction_strategies.md](./ocr_correction_strategies.md)
- **词库管理**: 查看 [vocabulary_engineering_summary.md](./vocabulary_engineering_summary.md)
- **funNLP集成**: 查看 [vocabulary_engineering_summary.md](./vocabulary_engineering_summary.md)
- **RocksDB存储**: 查看 [vocabulary_engineering_summary.md](./vocabulary_engineering_summary.md)
- **热词缓存**: 查看 [vocabulary_engineering_summary.md](./vocabulary_engineering_summary.md)
- **词库同步**: 查看 [vocabulary_engineering_summary.md](./vocabulary_engineering_summary.md)
- **PP-OCRv5**: 查看 [pp_ocrv5_openvino_integration.md](./pp_ocrv5_openvino_integration.md)
- **OpenVINO**: 查看 [pp_ocrv5_openvino_integration.md](./pp_ocrv5_openvino_integration.md)
- **LabVIEW**: 查看 [pp_ocrv5_openvino_integration.md](./pp_ocrv5_openvino_integration.md)
- **vLLM**: 查看 [vllm_integration.md](../technical-analysis/vllm_integration.md)
- **WebSocket**: 查看 [websocket_protocol.md](../websocket_protocol.md)
- **前端集成**: 查看 [frontend_backend_integration.md](../frontend_backend_integration.md)

---

*最后更新时间: 2024年12月* 