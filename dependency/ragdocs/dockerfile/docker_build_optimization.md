# Docker 构建优化指南

## 问题背景

在构建 Docker 镜像时遇到了以下问题：
1. 依赖版本冲突，特别是 PyTorch 和 transformers 相关包
2. 构建过程超时
3. 镜像体积过大
4. 构建缓存利用不充分

## 优化方案

### 1. 依赖管理优化

#### 1.1 版本约束策略
- 使用更灵活的版本约束格式：`>=x.y.z,<x.y+1.0`
- 避免使用固定版本（`==`），改用范围约束
- 示例：
  ```python
  # 优化前
  torch==2.7.1
  transformers==4.36.2
  
  # 优化后
  torch>=2.0.0,<2.1.0
  transformers>=4.35.0,<4.36.0
  ```

#### 1.2 依赖分组
- 按功能模块分组依赖
- 明确标注版本兼容性说明
- 指定安装顺序

### 2. Dockerfile 优化

#### 2.1 多阶段构建
```dockerfile
# 构建阶段
FROM nvidia/cuda:12.8.0-base-ubuntu22.04 as builder
# ... 构建依赖 ...

# 最终阶段
FROM nvidia/cuda:12.8.0-base-ubuntu22.04
# ... 复制必要文件 ...
```

#### 2.2 分层安装依赖
```dockerfile
# 基础依赖
RUN pip install --no-cache-dir \
    setuptools>=68.0.0 \
    wheel>=0.42.0 \
    pip>=23.0.0

# PyTorch 相关依赖
RUN pip install --no-cache-dir \
    torch>=2.0.0,<2.1.0 \
    torchvision>=0.15.0,<0.16.0 \
    torchaudio>=2.0.0,<2.1.0

# 其他依赖
RUN pip install --no-cache-dir -r /tmp/requirements.txt
```

#### 2.3 健康检查
```dockerfile
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
```

### 3. Docker Compose 优化

#### 3.1 构建参数
```yaml
build:
  args:
    BUILDKIT_INLINE_CACHE: 1
    DOCKER_BUILDKIT: 1
    COMPOSE_DOCKER_CLI_BUILD: 1
```

#### 3.2 资源限制
```yaml
deploy:
  resources:
    limits:
      cpus: '4'
      memory: 8G
```

#### 3.3 日志配置
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "100m"
    max-file: "3"
```

#### 3.4 持久化缓存
```yaml
volumes:
  - bugagaric_cache:/root/.cache
```

## 构建命令

### 清理缓存
```bash
docker system prune -a
```

### 使用 BuildKit 构建
```bash
DOCKER_BUILDKIT=1 docker-compose build --no-cache
```

### 启动服务
```bash
docker-compose up -d
```

## 优化效果

1. **构建速度提升**
   - 利用多阶段构建减少最终镜像大小
   - 通过分层安装依赖优化缓存利用

2. **稳定性提升**
   - 解决依赖版本冲突
   - 添加健康检查机制
   - 配置资源限制避免资源耗尽

3. **可维护性提升**
   - 清晰的依赖管理策略
   - 完善的日志配置
   - 标准化的构建流程

## 注意事项

1. 确保 Docker 版本支持 BuildKit（Docker 18.09+）
2. 检查 CUDA 版本与 PyTorch 版本的兼容性
3. 根据实际需求调整资源限制
4. 定期清理 Docker 缓存以释放磁盘空间

## 后续优化方向

1. 考虑使用 Docker BuildKit 的缓存导出功能
2. 实现自动化构建和测试流程
3. 添加镜像扫描和安全检查
4. 优化多环境部署配置 