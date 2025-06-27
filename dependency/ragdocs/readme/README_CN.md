# BugAgaric 文档中心

## 📚 文档结构

```
docs/
├── getting-started/           # 入门指南
│   ├── installation.md       # 安装指南
│   ├── quick-start.md        # 快速开始
│   └── basic-concepts.md     # 基本概念
│
├── user-guide/               # 用户指南
│   ├── features/            # 功能说明
│   │   ├── rag.md          # RAG功能
│   │   ├── evaluation.md    # 评估功能
│   │   └── deployment.md    # 部署功能
│   ├── tutorials/           # 教程
│   └── faq.md              # 常见问题
│
├── development/             # 开发文档
│   ├── architecture/        # 架构设计
│   │   ├── overview.md     # 架构概览
│   │   ├── modules.md      # 模块设计
│   │   └── api.md          # API设计
│   ├── testing/            # 测试指南
│   └── contributing.md     # 贡献指南
│
├── deployment/             # 部署文档
│   ├── docker/            # Docker部署
│   ├── kubernetes/        # K8s部署
│   └── performance/       # 性能优化
│
├── modules/               # 模块文档
│   ├── llm/              # LLM模块
│   ├── rag/              # RAG模块
│   └── prompt/           # Prompt工程
│
├── security/             # 安全文档
│   ├── security.md       # 安全指南
│   └── code-of-conduct.md # 行为准则
│
└── assets/              # 文档资源
    ├── images/          # 图片资源
    └── diagrams/        # 架构图
```

## 🎯 核心功能

### 1. 智能检索增强
- 多模态检索支持
- 混合检索策略
- 知识对齐技术
- 上下文理解能力

### 2. 模型微调与优化
- 嵌入模型微调
- 模型合并
- 性能优化

### 3. 工作流系统
- 智能代理工作流
- 知识对齐工作流
- 重标注工作流
- 可视化RAG工作流

### 4. 评估与优化
- 多维度评估
- 关键点评估
- 持续优化机制

## 🚀 快速开始

### 环境要求
- Python 3.10+
- CUDA 12.2+
- Docker (可选)

### 安装步骤
1. 克隆仓库
```bash
git clone https://github.com/your-org/bugagaric.git
cd bugagaric
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 下载模型
```bash
python scripts/download_model.py
```

4. 启动服务
```bash
streamlit run bugagaric/webui/webui.py
```

## 🔧 开发指南

### 本地开发环境
1. 启动基础服务
```bash
docker-compose up -d
```

2. 初始化环境
```bash
python config/local_debug/init_local_env.py
```

3. 启动调试
```bash
python config/local_debug/start_local_debug.py
```

### 代码规范
- 遵循PEP 8规范
- 使用类型注解
- 编写单元测试
- 保持文档更新

## 📊 性能评估

### 检索性能
| 方法 | ROUGE-L |
|------|---------|
| VanillaRAG | 40.75 |
| BugAgaric-DDR | 53.14 |
| BugAgaric-KBAlign | 48.72 |

### 问答性能
| 方法 | ROUGE-L |
|------|---------|
| VanillaRAG | 23.65 |
| BugAgaric-Adaptive-Note | 24.62 |
| VanillaRAG-finetune | 25.85 |

## 🤝 贡献指南

我们欢迎各种形式的贡献：
- 代码贡献
- 文档改进
- 问题报告
- 功能建议

请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 📄 许可证

本项目采用 [Apache-2.0](LICENSE) 许可证。

## 📝 引用

如果您使用了本项目，请引用以下论文：

```bib
@article{li2024rag,
  title={RAG-DDR: Optimizing Retrieval-Augmented Generation Using Differentiable Data Rewards},
  author={Li, Xinze and Mei, Sen and Liu, Zhenghao and Yan, Yukun and Wang, Shuo and Yu, Shi and Zeng, Zheni and Chen, Hao and Yu, Ge and Liu, Zhiyuan and others},
  journal={arXiv preprint arXiv:2410.13509},
  year={2024}
}
```

## 🔗 相关链接

- [GitHub仓库](https://github.com/your-org/bugagaric)
- [问题反馈](https://github.com/your-org/bugagaric/issues)
- [讨论区](https://github.com/your-org/bugagaric/discussions)
- [更新日志](CHANGELOG.md) 