# MaoOCR API 变更日志

## 📋 概述

本文档记录了MaoOCR项目API的版本变更历史，包括新增功能、修改接口、废弃功能等信息。

## 🔄 版本历史

### v1.0.0 (2024-12-XX)

#### 🎉 新功能
- **基础OCR识别API**
  - `POST /api/ocr/recognize` - 基础文本识别
  - `POST /api/ocr/recognize-with-requirements` - 带需求的文本识别
  - `POST /api/ocr/batch-recognize` - 批量识别
  - `POST /api/ocr/batch-recognize-async` - 异步批量识别

- **文档处理API**
  - `POST /api/upload` - 文件上传
  - `POST /api/upload/init` - 分片上传初始化
  - `POST /api/upload/chunk` - 分片上传
  - `POST /api/upload/complete` - 完成分片上传
  - `GET /api/files/{file_id}` - 获取文件
  - `POST /api/process-document` - 处理文档
  - `GET /api/download/{result_id}` - 下载处理结果

- **监控系统API**
  - `GET /api/monitoring/dashboard` - 获取监控面板数据
  - `GET /api/monitoring/realtime` - 获取实时指标
  - `GET /api/monitoring/export` - 导出监控数据

- **日志管理API**
  - `GET /api/logs` - 获取日志
  - `GET /api/logs/statistics` - 获取日志统计
  - `GET /api/logs/errors` - 获取错误分析
  - `GET /api/logs/search` - 搜索日志
  - `GET /api/logs/export` - 导出日志

- **告警系统API**
  - `GET /api/alerts` - 获取活跃告警
  - `GET /api/alerts/history` - 获取告警历史
  - `GET /api/alerts/statistics` - 获取告警统计
  - `POST /api/alerts/{rule_name}/acknowledge` - 确认告警
  - `POST /api/alerts/{rule_name}/resolve` - 解决告警

- **健康检查API**
  - `GET /api/health` - 获取健康状态
  - `GET /api/health/{check_name}` - 获取特定检查结果
  - `POST /api/health/{check_name}/run` - 立即运行检查

- **WebSocket API**
  - `WebSocket /ws/ocr` - OCR WebSocket接口

- **外部API集成**
  - `GET /api/external/stats` - 获取API统计
  - `GET /api/external/apis` - 列出API配置

- **PP-OCRv5 + OpenVINO API**
  - `POST /api/ocr/pp-ocrv5-recognize` - PP-OCRv5专用识别
  - `POST /api/ocr/pp-ocrv5-batch-recognize` - PP-OCRv5批量识别
  - `GET /api/ocr/pp-ocrv5-status` - 获取PP-OCRv5引擎状态
  - `GET /api/ocr/openvino-devices` - 获取OpenVINO设备信息
  - `POST /api/ocr/openvino-switch-device` - 切换OpenVINO设备
  - `GET /api/ocr/engine-comparison` - 获取引擎性能对比

#### 🔧 基础服务
- `GET /` - 根路径
- `GET /health` - 健康检查
- `GET /api/status` - 服务状态
- `GET /api/ocr/models` - 获取可用模型
- `GET /api/ocr/performance` - 获取性能统计

#### 📊 批量处理
- `GET /api/ocr/batch-status/{batch_id}` - 获取批量处理状态
- `GET /api/ocr/batch-results/{batch_id}` - 获取批量处理结果

#### 🎯 特性
- 支持多种文档格式：PDF、EPUB、DOCX、MD
- 支持分片上传大文件
- 支持异步批量处理
- 实时监控和告警
- WebSocket实时通信
- 完整的日志管理
- 健康检查系统

## 🔮 未来版本规划

### v1.1.0 (计划中)

#### 🎉 计划新功能
- **OCR纠错API**
  - `POST /api/ocr/correct` - 文本纠错
  - `POST /api/ocr/correct-batch` - 批量纠错
  - `GET /api/ocr/correction-models` - 获取纠错模型

- **高级文档处理**
  - `POST /api/document/analyze` - 文档结构分析
  - `POST /api/document/extract-tables` - 表格提取
  - `POST /api/document/extract-images` - 图片提取

- **用户管理API**
  - `POST /api/auth/login` - 用户登录
  - `POST /api/auth/register` - 用户注册
  - `GET /api/users/profile` - 获取用户信息
  - `PUT /api/users/profile` - 更新用户信息

- **任务管理API**
  - `GET /api/tasks` - 获取任务列表
  - `GET /api/tasks/{task_id}` - 获取任务详情
  - `POST /api/tasks/{task_id}/cancel` - 取消任务
  - `DELETE /api/tasks/{task_id}` - 删除任务

#### 🔧 计划改进
- 添加API认证和授权
- 支持更多文档格式
- 优化批量处理性能
- 增强监控和告警功能
- 改进错误处理和日志记录

### v1.2.0 (计划中)

#### 🎉 计划新功能
- **AI增强功能**
  - `POST /api/ai/summarize` - 文档摘要
  - `POST /api/ai/translate` - 文档翻译
  - `POST /api/ai/classify` - 文档分类

- **协作功能**
  - `POST /api/collaboration/share` - 分享文档
  - `GET /api/collaboration/shared` - 获取分享列表
  - `POST /api/collaboration/comment` - 添加评论

- **工作流API**
  - `POST /api/workflow/create` - 创建工作流
  - `GET /api/workflow/list` - 获取工作流列表
  - `POST /api/workflow/execute` - 执行工作流

#### 🔧 计划改进
- 支持分布式部署
- 添加缓存层
- 优化数据库查询
- 增强安全性

## 📝 变更类型说明

### 🎉 新功能 (New Features)
- 新增的API端点
- 新增的功能特性
- 新增的配置选项

### 🔧 改进 (Improvements)
- 性能优化
- 功能增强
- 用户体验改进

### 🐛 修复 (Bug Fixes)
- 错误修复
- 兼容性问题解决
- 稳定性改进

### ⚠️ 废弃 (Deprecated)
- 即将移除的功能
- 建议迁移的API
- 不再维护的特性

### 🗑️ 移除 (Removed)
- 已移除的功能
- 不再支持的API
- 清理的代码

## 🔄 迁移指南

### 从 v0.x 迁移到 v1.0.0

#### 主要变更
1. **API路径变更**
   - 所有API路径添加了 `/api` 前缀
   - OCR相关API统一使用 `/api/ocr` 路径

2. **响应格式统一**
   - 所有API响应都采用统一的JSON格式
   - 添加了 `success` 字段标识请求状态

3. **错误处理改进**
   - 统一的错误响应格式
   - 详细的错误码和消息

#### 迁移步骤
1. 更新API调用路径
2. 适配新的响应格式
3. 更新错误处理逻辑
4. 测试所有功能

## 📚 相关文档

- [API参考文档](API_REFERENCE.md) - 完整的API文档
- [API端点汇总表](API_ENDPOINTS_SUMMARY.md) - 快速参考
- [技术架构文档](technical-architecture.md) - 系统架构
- [配置说明文档](configuration.md) - 配置指南

## 🤝 贡献指南

### 提交变更
1. 创建功能分支
2. 实现新功能或修复
3. 更新相关文档
4. 提交Pull Request

### 变更记录格式
```markdown
### v1.x.x (YYYY-MM-DD)

#### 🎉 新功能
- 描述新功能

#### 🔧 改进
- 描述改进内容

#### 🐛 修复
- 描述修复内容

#### ⚠️ 废弃
- 描述废弃内容

#### 🗑️ 移除
- 描述移除内容
```

---

*最后更新时间: 2024年12月* 