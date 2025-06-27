# BugAgaric

<div align="center">
    <img src="docs/assets/logo.png" alt="BugAgaric Logo" width="450">
</div>
<p align="center">
    【English | <a href="docs/readme/README-Chinese.md">Chinese</a>】
</p>

## 📖 Overview

The **BugAgaric framework** was jointly proposed by the THUNLP group from Tsinghua University, the NEUIR group from Northeastern University, Modelbest.Inc, and the 9#AISoft team. It is based on agile deployment and modular construction, introducing an automated "data construction-model fine-tuning-inference evaluation" knowledge adaptation technology system. This provides a one-stop, researcher and developer-friendly RAG system solution. BugAgaric significantly simplifies the entire process from data construction to model fine-tuning in domain adaptation for RAG systems, assisting researchers and developers in efficiently tackling complex tasks.

<div align="center">
  <img src='docs/assets/en/feature.jpg' width=600>
</div>

- **No-Code Programming WebUI Support:** Users with no programming experience can easily operate the full link setup and optimization process, including the **multimodal RAG solution VisRAG**;
- **One-Click Solution for Synthesis and Fine-Tuning:** Centered around proprietary methods such as **KBAlign, RAG-DDR**, the system allows for one-click systematic data construction + retrieval, and supports performance optimization with diverse model fine-tuning strategies;
- **Multidimensional, Multi-Stage Robust Evaluation:** Using the proprietary **RAGEval** method at its core, it incorporates multi-stage assessment methods focused on effective/key information, significantly enhancing the robustness of "model evaluation";
- **Research-Friendly Exploration Work Integration:** It includes **THUNLP-RAG group's proprietary methods** and other cutting-edge RAG methods, supporting continuous module-level exploration and development;
- **Advanced Professional Vocabulary Management:** Built-in intelligent terminology extraction and management system with three-level cache architecture for high-performance domain-specific vocabulary processing;
- **React Frontend Optimization:** Modern React frontend with performance optimizations, component memoization, and advanced state management.

**All of the above features can be quickly implemented directly through the web frontend.**

<div align="center">
  <img src='docs/assets/en/image2.png' width=600>
</div>

## ⚡️ Quick Start

### Environmental Dependencies

**CUDA** version should be **12.2** or above.

**Python** version should be **3.10** or above.

### Quick Deployment

You can deploy BugAgaric and run the front-end page using the following methods:

1. **Deploy via Docker**

Run the following command, then visit "[http://localhost:8843](http://localhost:8843/)" in your browser.

```Bash
docker-compose up --build -d
```

2. **Deploy via Conda**

Run the following commands, then visit "[http://localhost:8843](http://localhost:8843/)" in your browser.

```Bash
# Create a conda environment
conda create -n bugagaric python=3.10

# Activate the conda environment
conda activate bugagaric

# Install relevant dependencies
pip install -r requirements.txt

# Run the following script to download models, by default they will be downloaded to the resources/models directory
# The list of downloaded models is in config/models_download_list.yaml
python scripts/download_model.py

# Run the demo page
streamlit run bugagaric/webui/webui.py --server.fileWatcherType none
```

3. **Local Development Setup**

For local development and debugging, follow these steps:

1. **Clean up environment (optional but recommended)**
```bash
# Clean up all containers (including orphaned containers)
docker-compose down --remove-orphans
docker-compose -f docker-compose.db.yml down --remove-orphans
docker-compose -f docker-compose.es.yml down --remove-orphans
docker-compose -f docker-compose.milvus.yml down --remove-orphans
docker-compose -f docker-compose.minio.yml down --remove-orphans
```

2. **Start required services**
```bash
# Start base services (including devpi and webui)
docker-compose up -d

# Start PostgreSQL database
docker-compose -f docker-compose.db.yml up -d

# Start Elasticsearch
docker-compose -f docker-compose.es.yml up -d

# Start Milvus vector database
docker-compose -f docker-compose.milvus.yml up -d

# Start MinIO object storage
docker-compose -f docker-compose.minio.yml up -d
```

3. **Initialize local environment**
```bash
# Initialize local development environment
python config/local_debug/init_local_env.py
```

4. **Start local debugging**
```bash
# Start local debugging environment
python config/local_debug/start_local_debug.py

# Or start with browser automatically
python config/local_debug/start_debug_with_browser.py
```

**Note:** Make sure to set the following environment variables:
- `JWT_SECRET_KEY`
- `FERNET_KEY`

These can be set in a `.env` file or passed as environment variables during startup.

For more detailed information about local development, please refer to the [Local Debug Guide](docs/local_debug_guide.md).

### Easy to Get Started

https://github.com/user-attachments/assets/b07d20d9-4121-404a-9cba-e89590bd4f4e

The above video provides a simple demonstration of the getting started experience. To facilitate your use of BugAgaric, we offer a detailed guide to help you get started with BugAgaric, complete the experience, and optimize the model [User Guide](docs/user_guide/user_guide_en.md).

If you are interested in the technical solutions involved, you can gain a more comprehensive understanding through the [BugAgaric Series](docs/typical_implementation/typical_implementation_en.md).

## 🔧 Overall Architecture

The architecture of BugAgaric is composed of three parts: **Frontend**, **Service**, and **Backend**. The specifics are as follows:

* **Backend**
  * **Modules (Module Layer):** Defines the key components in the RAG system, such as the knowledge base, retrieval model, and generation model, supporting users to customize flexibly based on standard classes.
  * **Workflow (Process Layer):** Standardizes the composition patterns of the RAG system, provides a standardized basic RAG implementation, and integrates team-developed typical methods like Adaptive-Note and VisRAG. It supports users in building and adjusting flexibly and will continue to be supplemented and optimized.
  * **Function (Function Layer):** Responsible for key operations in the optimization process of the RAG system, including data synthesis, system evaluation, and model fine-tuning, contributing to the comprehensive improvement of system performance.
* **Service:** Apart from supporting instance-based RAG system construction, BugAgaric also provides a microservice deployment mode to optimize user experience during application, supporting flexible deployment of key services like Embedding Model, LLM, and vector databases.
* **Frontend:** The frontend is divided into Resource Management and Function Pages. Resource Management includes **Model Management** and **Knowledge Base Management**, while the Function Pages cover **Data Construction, Model Training, Effect Evaluation**, and **Inference Experience**, providing users with convenient interactive support.

<div align="center">
    <img src='docs/assets/en/image3.png' width=600>
</div>

## 🚀 New Features

### 1. Advanced Three-Level Cache Architecture
- **Hot Cache (Level 1):** Hybrid LRU+LFU algorithm with frequency halving mechanism
- **RocksDB Storage (Level 2):** Domain-specific storage with high concurrency support
- **Cold Storage (Level 3):** Compressed archival storage for infrequently accessed data
- **Performance:** <1ms latency for hot cache, <10ms for RocksDB storage

### 2. Professional Vocabulary Management
- **Intelligent Term Extraction:** TF-IDF based extraction with domain-specific features
- **Multi-domain Support:** Medical, Legal, IT, Finance, Education domains
- **Auto-sync Mechanism:** Automatic vocabulary synchronization and updates
- **funNLP Integration:** Comprehensive Chinese NLP resource integration

### 3. React Frontend Optimization
- **Performance Optimizations:** React.memo, useCallback, useMemo implementations
- **Component Architecture:** Modular design with error boundaries
- **State Management:** Context API and custom hooks for centralized state
- **Code Quality:** ESLint + Prettier + Husky integration

### 4. Enhanced Model Fine-tuning
- **Embedding Model Optimization:** Dense/sparse/ColBERT multimodal embeddings
- **LoRA Model Merging:** Efficient model parameter merging
- **Training Enhancements:** Sentence-Transformers format support
- **Performance Monitoring:** Real-time training metrics and optimization

## 💫 Performance Evaluation

To verify the application effectiveness of BugAgaric in vertical domains, we took the legal field as an example, collected various professional books, and built a knowledge base containing **880,000 slices**. We then performed a systematic evaluation on BugAgaric based on a relatively comprehensive evaluation dataset. The following are our evaluation results. For more detailed evaluation content, please refer to the relevant document. [Evaluation Report](docs/evaluation_report/evaluation_report_en.md).

| **End-to-End Performance** | **Statute Prediction (3-2) ROUGE-L** |
| -------------------------------- | ------------------------------------------ |
| **VanillaRAG**             | 40.75                                      |
| **BugAgaric-DDR**           | 53.14                                      |
| **BugAgaric-KBAlign**       | 48.72                                      |

| **End-to-End Performance** | **Consultation (3-8) ROUGE-L** |
| -------------------------------- | ------------------------------------ |
| **VanillaRAG**             | 23.65                                |
| **BugAgaric-Adaptive-Note** | 24.62                                |
| **VanillaRAG-finetune**    | 25.85                                |

## 📚 Documentation

### Core Documentation
- [Advanced Cache Architecture](docs/advanced_cache_architecture.md) - Three-level cache system design
- [Vocabulary Engineering Implementation](docs/vocabulary_engineering_implementation.md) - Professional vocabulary management
- [React Development Best Practices](docs/React_Development_Best_Practices_Summary.md) - Frontend optimization guidelines
- [React Optimization Implementation Plan](docs/React_Optimization_Implementation_Plan.md) - Performance optimization roadmap

### Technical Guides
- [Local Debug Guide](docs/local_debug_guide.md) - Development environment setup
- [Performance Rules](docs/PERFORMANCE_RULES.md) - Go language performance optimization
- [Update Checklist](docs/update-checklist.md) - Documentation maintenance guidelines

## ‍🤝 Acknowledgments

Thanks to the following contributors for code submissions and testing. New members are welcome to join us in striving to build a complete ecosystem!

<a href="https://github.com/OpenBMB/BugAgaric/contributors">
  <img src="https://contrib.rocks/image?repo=OpenBMB/BugAgaric" />
</a>

## 🌟 Trends

<a href="https://star-history.com/#OpenBMB/BugAgaric&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=OpenBMB/BugAgaric&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=OpenBMB/BugAgaric&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=OpenBMB/BugAgaric&type=Date" />
 </picture>
</a>

## ⚖️ License

- The source code is licensed under the [Apache-2.0](https://github.com/OpenBMB/MiniCPM/blob/main/LICENSE) license.

## 📑 Citation

If you find this repository useful, please consider giving it a star ⭐ and citing it to show your support.

```bib
@article{li2024rag,
  title={RAG-DDR: Optimizing Retrieval-Augmented Generation Using Differentiable Data Rewards},
  author={Li, Xinze and Mei, Sen and Liu, Zhenghao and Yan, Yukun and Wang, Shuo and Yu, Shi and Zeng, Zheni and Chen, Hao and Yu, Ge and Liu, Zhiyuan and others},
  journal={arXiv preprint arXiv:2410.13509},
  year={2024}
}

@article{yu2024visrag,
  title={Visrag: Vision-based retrieval-augmented generation on multi-modality documents},
  author={Yu, Shi and Tang, Chaoyue and Xu, Bokai and Cui, Junbo and Ran, Junhao and Yan, Yukun and Liu, Zhenghao and Wang, Shuo and Han, Xu and Liu, Zhiyuan and others},
  journal={arXiv preprint arXiv:2410.10594},
  year={2024}
}

@article{wang2024retriever,
  title={Retriever-and-Memory: Towards Adaptive Note-Enhanced Retrieval-Augmented Generation},
  author={Wang, Ruobing and Zha, Daren and Yu, Shi and Zhao, Qingfei and Chen, Yuxuan and Wang, Yixuan and Wang, Shuo and Yan, Yukun and Liu, Zhenghao and Han, Xu and others},
  journal={arXiv preprint arXiv:2410.08821},
  year={2024}
}

@article{zeng2024kbalign,
  title={KBAlign: KBAlign: Efficient Self Adaptation on Specific Knowledge Bases},
  author={Zeng, Zheni and Chen, Yuxuan and Yu, Shi and Yan, Yukun and Liu, Zhenghao and Wang, Shuo and Han, Xu and Liu, Zhiyuan and Sun, Maosong},
  journal={arXiv preprint arXiv:2411.14790},
  year={2024}
}

@article{zhu2024rageval,
  title={Rageval: Scenario specific rag evaluation dataset generation framework},
  author={Zhu, Kunlun and Luo, Yifan and Xu, Dingling and Wang, Ruobing and Yu, Shi and Wang, Shuo and Yan, Yukun and Liu, Zhenghao and Han, Xu and Liu, Zhiyuan and others},
  journal={arXiv preprint arXiv:2408.01262},
  year={2024}
}
```

# BugAgaric WebUI

A modern web interface for BugAgaric, built with Streamlit.

## Features

- User authentication and authorization
- Database integration with PostgreSQL
- File management and caching
- Internationalization support
- Comprehensive logging
- Configuration management
- Security features

## Prerequisites

- Python 3.9 or higher
- Docker and Docker Compose
- PostgreSQL (if running without Docker)

## Installation

### Using Docker (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bugagaric-webui.git
cd bugagaric-webui
```

2. Create necessary directories:
```bash
mkdir -p data logs config
```

3. Start the application:
```bash
docker-compose up -d
```

The application will be available at http://localhost:8501

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/bugagaric-webui.git
cd bugagaric-webui
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Initialize the database:
```bash
python scripts/init_db.py
```

5. Start the application:
```bash
python scripts/start.py
```

## Configuration

The application can be configured through environment variables or the config.yaml file:

- `DATABASE_URL`: PostgreSQL connection URL
- `JWT_SECRET_KEY`: Secret key for JWT token generation
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Development

1. Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Run tests:
```bash
pytest
```

3. Run linting:
```bash
flake8
```

## Project Structure

```
bugagaric-webui/
├── config/             # Configuration files
├── data/              # Data storage
├── logs/              # Log files
├── scripts/           # Utility scripts
├── bugagaric/
│   └── webui/
│       ├── components/  # Reusable UI components
│       ├── pages/      # Streamlit pages
│       └── utils/      # Utility modules
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

# BugAgaric Documentation Structure

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
