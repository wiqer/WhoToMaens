# BugAgaric 微调功能集成指南

## 概述

本文档介绍了BugAgaric项目中微调功能的完整实现，包括后端API、前端界面和系统集成。

## 功能特性

### 🎯 支持的微调类型
- **SFT (监督微调)**: 基于标注数据的监督学习
- **DPO (直接偏好优化)**: 基于人类偏好的强化学习
- **Embedding (嵌入模型)**: 文本嵌入模型微调
- **KBAlign (知识库对齐)**: 知识库对齐微调

### 🔧 核心功能
- 可视化配置界面
- 实时训练监控
- 任务状态管理
- 训练日志查看
- 配置模板管理

## 系统架构

### 后端架构
```
go-services/api/
├── services/finetune.go      # 微调服务核心逻辑
├── handlers/finetune.go      # API处理器
└── main.go                   # 主程序（已集成微调路由）
```

### 前端架构
```
frontend/src/
├── pages/Finetune.jsx        # 主微调页面
├── components/
│   ├── FinetuneConfig.jsx    # 配置组件
│   └── TaskMonitor.jsx       # 监控组件
├── services/finetune.js      # 前端API服务
└── config/api.js             # API配置
```

## 快速开始

### 1. 启动系统
```bash
# 给启动脚本添加执行权限
chmod +x start_finetune_system.sh

# 启动整个系统
./start_finetune_system.sh
```

### 2. 访问系统
- 前端界面: http://localhost:3000
- 后端API: http://localhost:18080
- 微调页面: http://localhost:3000/finetune

### 3. 开始微调
1. 登录系统
2. 点击侧边栏"模型微调"
3. 选择微调类型
4. 配置训练参数
5. 点击"开始训练"
6. 在监控页面查看进度

## API接口文档

### 启动微调任务
```http
POST /api/finetune/start
Content-Type: application/json

{
  "type": "sft",
  "config": {
    "model_name_or_path": "microsoft/DialoGPT-medium",
    "train_data_path": "data/train.jsonl",
    "output_dir": "output/sft",
    "use_lora": true,
    "learning_rate": 5e-5,
    "num_train_epochs": 3,
    "per_device_train_batch_size": 4
  }
}
```

### 获取任务状态
```http
GET /api/finetune/tasks/{task_id}
```

### 获取任务日志
```http
GET /api/finetune/tasks/{task_id}/logs?limit=100
```

### 停止任务
```http
DELETE /api/finetune/tasks/{task_id}
```

### 删除任务
```http
DELETE /api/finetune/tasks/{task_id}/delete
```

### 获取任务列表
```http
GET /api/finetune/tasks
```

### 获取配置模板
```http
GET /api/finetune/templates
```

## 配置说明

### SFT/DPO配置
```json
{
  "model_name_or_path": "模型路径或HuggingFace标识符",
  "train_data_path": "训练数据文件路径",
  "output_dir": "模型输出目录",
  "config_file": "配置文件路径",
  "use_lora": true,
  "learning_rate": 5e-5,
  "num_train_epochs": 3,
  "per_device_train_batch_size": 4
}
```

### Embedding配置
```json
{
  "model_name_or_path": "嵌入模型路径",
  "train_data": "训练数据路径",
  "output_dir": "输出目录",
  "learning_rate": 2e-5,
  "num_train_epochs": 3,
  "per_device_train_batch_size": 16
}
```

### KBAlign配置
```json
{
  "model_name_or_path": "模型路径",
  "input_path": "输入数据路径",
  "output_dir": "输出目录",
  "gpu_vis": "0,1,2,3",
  "use_lora": true
}
```

## 数据格式

### SFT/DPO训练数据格式
```json
{
  "query": "用户查询",
  "retrieval_result": "检索结果",
  "chosen": {
    "text": "优选回答"
  },
  "rejected": {
    "text": "被拒绝的回答"
  }
}
```

### Embedding训练数据格式
```json
{
  "query": "查询文本",
  "pos": ["正例1", "正例2"],
  "neg": ["负例1", "负例2"]
}
```

## 测试

### 运行API测试
```bash
python3 test_finetune_api.py
```

### 测试覆盖范围
- ✅ 健康检查
- ✅ 配置模板获取
- ✅ 任务启动
- ✅ 状态查询
- ✅ 日志获取
- ✅ 任务列表
- ✅ 任务停止
- ✅ 任务删除

## 故障排除

### 常见问题

#### 1. 后端服务启动失败
```bash
# 检查Go环境
go version

# 检查依赖
cd go-services/api
go mod tidy

# 重新编译
go build -o bugagaric-api main.go
```

#### 2. 前端服务启动失败
```bash
# 检查Node.js环境
node --version
npm --version

# 安装依赖
cd frontend
npm install

# 启动服务
npm start
```

#### 3. 微调任务启动失败
- 检查模型路径是否正确
- 检查训练数据文件是否存在
- 检查输出目录权限
- 查看后端日志获取详细错误信息

#### 4. 训练过程中断
- 检查GPU显存是否充足
- 检查磁盘空间是否足够
- 检查网络连接是否稳定

### 日志查看
```bash
# 查看后端日志
tail -f go-services/api/logs/api.log

# 查看训练日志
tail -f output/logs/finetune.log
```

## 性能优化

### 后端优化
- 使用连接池管理数据库连接
- 实现任务队列避免阻塞
- 添加缓存减少重复计算

### 前端优化
- 使用React.memo优化组件渲染
- 实现虚拟滚动处理大量数据
- 添加防抖处理频繁请求

### 训练优化
- 使用LoRA减少显存占用
- 启用梯度检查点
- 使用混合精度训练

## 扩展开发

### 添加新的微调类型
1. 在`finetune.go`中添加新的命令构建函数
2. 在`handlers/finetune.go`中注册新的类型
3. 在前端配置组件中添加对应的表单
4. 更新API文档和测试用例

### 添加新的监控指标
1. 在微调脚本中添加指标收集
2. 在API中暴露指标接口
3. 在前端添加可视化组件

## 贡献指南

### 代码规范
- 遵循Go和JavaScript的编码规范
- 添加适当的注释和文档
- 编写单元测试和集成测试

### 提交规范
- 使用清晰的提交信息
- 一个提交只包含一个功能
- 提交前运行测试确保通过

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 发送邮件: your-email@example.com 