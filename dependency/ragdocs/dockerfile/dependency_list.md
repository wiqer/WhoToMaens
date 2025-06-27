# BugAgaric Docker 依赖清单与构建效果

## 1. 基础环境配置

### 1.1 系统环境
- 基础镜像：`nvidia/cuda:12.8.0-base-ubuntu22.04`
- Python 版本：3.10
- CUDA 版本：12.8.0
- 操作系统：Ubuntu 22.04

### 1.2 环境变量
```bash
# Python 相关
PYTHONUNBUFFERED=1
PIP_NO_CACHE_DIR=1
PIP_DISABLE_PIP_VERSION_CHECK=1
PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 日志相关
LOG_LEVEL=INFO
LOG_DIR=/app/logs
LOG_MAX_SIZE=100MB
LOG_ROTATION="1 day"
LOG_RETENTION="30 days"
```

## 2. 依赖清单

### 2.1 Web 框架
- fastapi==0.115.0
- uvicorn==0.24.0
- python-multipart==0.0.6
- python-jose[cryptography]==3.5.0
- passlib[bcrypt]==1.7.4
- starlette==0.37.2

### 2.2 数据库
- sqlalchemy==2.0.23
- alembic==1.12.1
- psycopg2-binary==2.9.9
- redis==5.0.1

### 2.3 AI & ML
- langchain==0.0.350
- openai==1.3.5
- transformers==4.35.2
- torch==2.1.0
- torchvision==0.16.0
- torchaudio==2.1.0
- sentence-transformers==2.2.2

### 2.4 工具包
- python-dotenv==1.0.0
- pydantic==2.5.2
- pydantic-settings==2.1.0
- loguru==0.7.2
- tenacity==8.2.3
- tqdm==4.66.1

### 2.5 其他重要依赖
- protobuf==4.25.3
- grpcio==1.67.1
- grpcio-tools==1.60.1
- huggingface-hub==0.33.0
- tokenizers==0.21.1
- datasets==2.17.0
- evaluate==0.4.1
- wandb==0.16.2
- tensorboard==2.15.2
- jieba>=0.42.1

## 3. 日志配置

### 3.1 日志系统设置
- 日志级别：INFO
- 日志目录：/app/logs
- 最大日志大小：100MB
- 日志轮转：每天
- 日志保留：30天
- 日志格式：包含时间戳、日志级别、模块名、函数名、行号和消息

### 3.2 日志文件
- 应用日志：app.log
- 错误日志：error.log

## 4. Docker 构建配置

### 4.1 构建阶段
1. 基础工具安装
   - setuptools>=68.0.0
   - wheel>=0.42.0
   - pip>=23.0.0

2. PyTorch 相关依赖安装
   - torch==2.1.0
   - torchvision==0.16.0
   - torchaudio==2.1.0

3. 其他依赖安装
   - 从 requirements.txt 安装

### 4.2 健康检查
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

## 5. 构建效果

### 5.1 性能指标
- 构建时间：约 15-20 分钟（取决于网络状况）
- 最终镜像大小：约 4-5GB
- 内存使用：启动时约 2GB，运行时约 4-8GB

### 5.2 稳定性
- 依赖版本固定，避免冲突
- 日志系统完善，便于问题排查
- 健康检查机制确保服务可用性

### 5.3 可维护性
- 清晰的依赖管理
- 完善的日志记录
- 标准化的构建流程

## 6. 注意事项

1. 版本兼容性
   - CUDA 12.8.0 与 PyTorch 2.1.0 兼容
   - Python 3.10 与所有依赖包兼容

2. 构建建议
   - 使用清华镜像源加速依赖安装
   - 确保有足够的磁盘空间（建议 >20GB）
   - 建议使用 Docker BuildKit 进行构建

3. 运行建议
   - 定期检查日志文件大小
   - 监控系统资源使用情况
   - 定期清理旧的日志文件

## 7. 更新记录

### 2024-03-xx
- 初始版本
- 完成基础依赖配置
- 实现日志系统
- 优化 Docker 构建流程 