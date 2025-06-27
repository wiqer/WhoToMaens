# BugAgaric项目知识文档

## 一、项目概述
BugAgaric是一个基于RAG技术的智能提示词生成系统，提供高质量、个性化的提示词生成服务。核心功能包括智能提示词生成、模板管理系统、记忆增强机制、RAG技术集成、多语言支持和高性能设计。

主要应用场景：
- 企业智能客服与知识库管理
- 开发者快速构建RAG应用
- 研究人员进行检索算法与模型优化研究

## 二、系统架构
### 2.1 分层架构
BugAgaric采用分层微服务架构，包含以下核心层次：

#### 前端交互层
- 对话界面模块：提供自然语言交互界面
- 提示词编辑器：支持生成结果的实时编辑
- 用户偏好设置：配置常用领域和模型偏好

#### 业务逻辑层
- 需求解析引擎：意图识别和实体提取
- 提示词生成引擎：模板匹配和术语增强
- RAG增强模块：知识库检索和上下文融合
- 记忆管理模块：短期和长期记忆维护

#### 数据层
- 模板库：存储结构化提示词模板
- 术语库：分类存储专业领域词汇
- 用户记忆库：存储用户对话历史和偏好
- 知识库：存储辅助生成的参考文档

#### 集成层
- LLM模型接口：支持本地和云端模型
- 外部系统接口：文件存储和监控集成

### 2.2 核心数据流程
#### 提示词生成流程
1. 用户输入自然语言需求
2. 需求解析和意图识别
3. 资源检索和模板匹配
4. 提示词组装和优化
5. LLM调用和结果生成
6. 反馈收集和优化

#### 记忆管理流程
1. 生成结果记录
2. 用户反馈提取
3. 偏好模型更新
4. 模板优化调整

## 三、技术栈
### 3.1 前端技术
- React + TypeScript
- Material-UI 组件库
- WebSocket 实时通信

### 3.2 后端技术
- FastAPI (Python)
- Go 微服务
- PostgreSQL 数据库
- Milvus 向量数据库
- Redis 缓存

### 3.3 AI集成
- LangChain 框架
- vLLM 推理引擎
- OpenAI/Anthropic API

## 四、环境搭建与部署
### 4.1 环境要求
- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis 6+

### 4.2 安装步骤
```bash
# 克隆仓库
git clone https://github.com/your-username/bugagaric.git
cd bugagaric

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件，设置必要的配置项

# 初始化数据库
python manage.py migrate

# 启动服务
python manage.py runserver
```

### 4.3 必要服务启动
```bash
# 清理环境（可选）
docker-compose down --remove-orphans

docker-compose -f docker-compose.db.yml down --remove-orphans
# 启动基础服务
docker-compose up -d
# 启动数据库服务
docker-compose -f docker-compose.db.yml up -d
# 启动搜索引擎服务
docker-compose -f docker-compose.es.yml up -d
# 启动向量数据库服务
docker-compose -f docker-compose.milvus.yml up -d
# 启动对象存储服务
docker-compose -f docker-compose.minio.yml up -d
```

### 4.4 本地调试启动
```bash
# 初始化本地环境
python config/local_debug/init_local_env.py

# 启动本地调试
python config/local_debug/start_local_debug.py
```

## 五、核心功能模块
### 5.1 智能检索增强
- 多模态检索：支持文本、图像等多种模态
- 混合检索策略：结合稠密检索、稀疏检索和ColBERT
- 知识对齐：提升检索准确性的关键技术

### 5.2 模型微调与优化
- 嵌入模型微调：支持LoRA高效微调、自蒸馏优化
- 模型合并：基础模型与LoRA参数合并，支持多种精度

### 5.3 工作流系统
- 智能代理工作流：自动化任务处理
- 知识对齐工作流：优化知识库结构
- 可视化RAG工作流：直观展示检索过程

### 5.4 评估系统
支持检索指标（MRR、NDCG、Recall）和生成指标（Rouge、EM、Accuracy等）评估。

## 六、API接口文档
### 6.1 基础信息
- **Base URL**: /api
- **版本**: 1.0
- **认证方式**: JWT Token

### 6.2 核心接口

#### 认证接口
- **登录**: POST /auth/login
  请求体: `{"username": string, "password": string}`
  响应: `{"token": string, "expires_at": number}`

- **注册**: POST /auth/register
  请求体: `{"username": string, "password": string, "email": string}`
  响应: `{"message": string, "user_id": string}`

#### 文档管理接口
- **上传文档**: POST /documents/upload
- **获取文档列表**: GET /documents
- **获取文档详情**: GET /documents/{id}
- **删除文档**: DELETE /documents/{id}

#### 搜索接口
- **搜索文档**: POST /search
- **获取搜索历史**: GET /search/history

#### 对话接口
- **创建对话会话**: POST /chat/sessions
- **获取对话会话列表**: GET /chat/sessions
- **删除对话会话**: DELETE /chat/sessions
- **发送消息**: POST /chat/messages
- **获取对话历史**: GET /chat/history

#### 提示词生成接口
- **生成提示词**: POST /prompts/generate
  参数: 
  ```json
  {
    "context": {
      "domain": "string",
      "task_type": "string",
      "requirements": ["string"]
    },
    "parameters": {
      "style": "string",
      "tone": "string"
    }
  }
  ```

- **优化提示词**: POST /prompts/optimize

## 七、典型实现
### 7.1 Vanilla RAG
BugAgaric在该模块中新增了意图识别功能，针对无需检索的问题，可直接生成回复，从而提升响应效率。对于需要检索的问题，系统将执行单次检索与重排序，并根据检索内容生成精准回答。

### 7.2 DPO & SFT训练
#### DPO训练输入数据格式
```JSON
{"query": "xxx", "retrieval_result": ["xxx", "xxx", "xxx", "xxx", "xxx"], 
"chosen": {"text": "xxx"}, 
"rejected": {"text": "xxx"}}
```

#### SFT训练输入数据格式
```JSON
{"messages": [{"role": "system", "content": "You are helpful"}, {"role": "user", "content": "What's the capital of France?"}, {"role": "assistant", "content": "..."}]}
```

### 7.3 LoRA合并
如果训练过程中采用LoRA微调，则在训练完成后需要将LoRA微调参数与原始模型参数进行合并，以生成完整的模型权重。

## 八、开发指南
### 8.1 分支命名规则
- `feature/<功能名称>` # 新功能开发分支
- `hotfix/<问题编号>-<描述>` # 紧急修复分支
- `release/v1.x` # 版本发布分支

### 8.2 PR审查要点
1. 测试覆盖率≥90%
2. 需提供性能对比报告（如响应时间/资源消耗）
3. 文档更新需包含版本变更说明

## 九、评估指标
### 9.1 检索指标
- **MRR (Mean Reciprocal Rank)**: 衡量检索结果排序质量，计算相关文档排名倒数的平均值
- **NDCG (Normalized Discounted Cumulative Gain)**: 评估排序结果的相关性和位置准确性
- **Recall@k**: 衡量前k个检索结果中相关文档的比例

### 9.2 生成指标
- **Rouge**: 评估生成文本与参考文本的重叠度（基于n-gram、词干和词序列）
- **EM (Exact Match)**: 判断生成结果是否与参考答案完全匹配
- **Accuracy**: 分类任务中的准确率指标
- **F1 Score**: 平衡精确率和召回率的综合指标
- **BLEU/Meteor**: 机器翻译领域常用的评估指标

## 十、用户指南
### 10.1 WebUI操作流程
1. **模型管理**: 选择并加载LLM、Embedding或Reranker模型（支持本地和API加载）
2. **知识管理**: 上传文档（PDF/TXT）→ 配置参数 → 构建知识库（包含Index、Org_Files和Chunk_Files）
3. **对话交互**: 进入Chat/Inference页面，选择工作流（如Vanilla RAG）进行问答

### 10.2 常见问题解决
#### 服务连接超时
- 检查相关服务是否已启动（PostgreSQL、Redis、Milvus等）
- 确认服务端口配置正确
- 检查防火墙设置

#### 依赖安装问题
```bash
# 使用本地镜像源
pip install -r requirements.txt -i http://localhost:3141/root/pypi/+simple/

# 使用清华镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 十一、高级功能
### 11.1 VisRAG部署
```bash
# 下载模型
modelscope download --model tcy006/VisRAG-Ret --local_dir ./resource/models/VisRAG-Ret
modelscope download --model OpenBMB/MiniCPM-V-2_6 --local_dir ./resource/models/MiniCPM-V-2_6
```

### 11.2 性能优化建议
- 根据硬件配置调整batch size
- 使用BF16精度加速训练
- 合理设置检索top_k值平衡效果与效率

## 十二、学习资源
- **API文档**: <mcfile name="api_docs.md" path="d:\BugAgaric-BUG\docs\api\魔苟\api_docs.md"></mcfile>
- **评估报告**: <mcfile name="evaluation_report.md" path="d:\BugAgaric-BUG\docs\evaluation_report\evaluation_report.md"></mcfile>
- **典型实现**: <mcfile name="typical_implementation.md" path="d:\BugAgaric-BUG\docs\typical_implementation\typical_implementation.md"></mcfile>