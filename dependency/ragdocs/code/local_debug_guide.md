# BugAgaric 本地调试指南

## 1. 环境准备

### 1.1 必要服务
项目依赖以下服务，需要按顺序启动：

1. **清理环境（可选但推荐）**
```bash
# 清理所有容器（包括孤儿容器）
docker-compose down --remove-orphans
docker-compose -f docker-compose.db.yml down --remove-orphans
docker-compose -f docker-compose.es.yml down --remove-orphans
docker-compose -f docker-compose.milvus.yml down --remove-orphans
docker-compose -f docker-compose.minio.yml down --remove-orphans
```

2. **基础服务**
```bash
# 启动基础服务（包含devpi和webui）
docker-compose up -d
```

3. **数据库服务**
```bash
# 启动PostgreSQL数据库
docker-compose -f docker-compose.db.yml up -d
```

4. **搜索引擎服务**
```bash
# 启动Elasticsearch
docker-compose -f docker-compose.es.yml up -d
```

5. **向量数据库服务**
```bash
# 启动Milvus向量数据库
docker-compose -f docker-compose.milvus.yml up -d
```

6. **对象存储服务**
```bash
# 启动MinIO对象存储
docker-compose -f docker-compose.minio.yml up -d
```

### 1.2 环境变量配置
确保以下环境变量已正确设置：
- `JWT_SECRET_KEY`
- `FERNET_KEY`

这些变量可以在`.env`文件中配置，或者在启动时通过环境变量传入。

## 2. 启动步骤

### 2.1 初始化本地环境
```bash
# 初始化本地开发环境
python config/local_debug/init_local_env.py
```

### 2.2 启动本地调试
有两种启动方式：

1. **基础启动**
```bash
# 启动本地调试环境
python config/local_debug/start_local_debug.py
```

2. **带浏览器启动**
```bash
# 启动本地调试环境并自动打开浏览器
python config/local_debug/start_debug_with_browser.py
```

## 3. 服务检查

启动后，系统会自动检查以下服务的可用性：
- streamlit
- hf_llm
- embedding
- reranker
- vllm
- visrag_embedding
- qdrant

如果服务检查失败，请确保所有必要的服务都已正确启动。

## 4. 常见问题

### 4.1 服务连接超时
如果遇到服务连接超时，请检查：
1. 相关服务是否已启动
2. 服务端口是否正确
3. 防火墙设置是否允许相关端口访问

### 4.2 依赖安装问题
如果遇到依赖安装问题，可以：
1. 使用devpi本地镜像源：
```bash
pip install -r requirements.txt -i http://localhost:3141/root/pypi/+simple/
```

2. 使用清华镜像源：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 4.3 孤儿容器问题
如果看到类似以下警告：
```
Found orphan containers ([bugagaric-bug-devpi-1 goproxy bugagaric-bug-webui-1 ...]) for this project
```

这表明有一些容器不在当前docker-compose文件中定义。解决方法：

1. **使用--remove-orphans标志**
```bash
docker-compose up -d --remove-orphans
```

2. **手动清理**
```bash
# 查看所有容器
docker ps -a

# 停止并删除不需要的容器
docker stop <container_id>
docker rm <container_id>
```

## 5. 开发提示

1. 本地调试时，修改代码后会自动重新加载
2. 日志文件位于`logs`目录
3. 配置文件位于`config`目录
4. 本地资源文件位于`data`目录

## 6. 停止服务

要停止所有服务，可以运行：
```bash
# 停止所有服务（包括孤儿容器）
docker-compose down --remove-orphans
docker-compose -f docker-compose.db.yml down --remove-orphans
docker-compose -f docker-compose.es.yml down --remove-orphans
docker-compose -f docker-compose.milvus.yml down --remove-orphans
docker-compose -f docker-compose.minio.yml down --remove-orphans
```

## 7. 目录结构说明

```
config/local_debug/
├── init_local_env.py      # 初始化本地环境
├── start_local_debug.py   # 启动本地调试
├── start_debug_with_browser.py  # 带浏览器启动
├── service_checker.py     # 服务检查
└── local_config.yaml      # 本地配置文件
```

## 8. 注意事项

1. 确保Docker服务已启动
2. 确保所有必要的端口未被占用
3. 首次启动时，某些服务可能需要较长时间初始化
4. 建议使用虚拟环境进行开发
5. 定期检查日志文件，及时发现问题
6. 如果遇到容器问题，优先使用`--remove-orphans`标志清理环境 