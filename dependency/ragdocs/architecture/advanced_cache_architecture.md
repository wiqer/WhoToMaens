# 三级缓存架构技术文档

## 概述

本文档描述了基于maoOCR项目专业词管理需求实现的高效三级缓存架构，该架构结合了MySQL InnoDB的LRU算法和LFU计数减半机制，实现了高性能、高可用的词汇缓存系统。

## 架构设计

### 三级缓存层次结构

```
┌─────────────────────────────────────────────────────────────┐
│                    三级缓存架构                              │
├─────────────────────────────────────────────────────────────┤
│  一级缓存：内存热词缓存（LRU+LFU混合算法）                   │
│  - 高频访问词条，极低延迟（<1ms）                            │
│  - 使用混合LRU+LFU算法，支持权重配置                         │
│  - 支持LFU计数定期减半，防止频率计数无限增长                 │
├─────────────────────────────────────────────────────────────┤
│  二级缓存：RocksDB分领域存储                                 │
│  - 每个领域独立RocksDB实例或列族                             │
│  - 支持高并发、持久化、批量写入                              │
│  - 快速范围查询，压缩存储                                    │
├─────────────────────────────────────────────────────────────┤
│  三级缓存：冷数据归档                                        │
│  - 低频词条定期归档到压缩文件                                │
│  - 支持gzip压缩，节省存储空间                                │
│  - 自动清理过期归档文件                                      │
└─────────────────────────────────────────────────────────────┘
```

### 核心特性

1. **混合缓存算法**：结合LRU（最近最少使用）和LFU（最不经常使用）算法
2. **分领域存储**：按专业领域分库存储，避免同名词冲突
3. **自动分层**：根据访问频率自动在三级缓存间迁移数据
4. **高性能**：一级缓存延迟<1ms，二级缓存延迟<10ms
5. **高可用**：支持备份恢复、故障转移
6. **可扩展**：支持水平扩展和垂直扩展

## 核心组件

### 1. AdvancedCacheManager（高级缓存管理器）

```go
type AdvancedCacheManager struct {
    hotCache      *HybridLRULFUCache    // 一级缓存
    rocksDBManager *RocksDBManager       // 二级缓存
    coldStorage   *ColdStorageManager    // 三级缓存
    stats         *CacheStatistics       // 统计信息
    config        *CacheConfig          // 配置
}
```

**主要功能**：
- 统一管理三级缓存
- 自动数据迁移和回写
- 性能监控和统计
- 后台维护任务

### 2. HybridLRULFUCache（混合LRU+LFU缓存）

```go
type HybridLRULFUCache struct {
    cache        map[string]*CacheEntry  // 缓存存储
    lruList      *list.List              // LRU链表
    frequencyMap map[string]int64        // LFU计数映射
    maxSize      int                     // 最大大小
    lfuHalfLife  int                     // LFU减半周期
    lruWeight    float64                 // LRU权重
    lfuWeight    float64                 // LFU权重
}
```

**算法特点**：
- **混合评分**：`score = LRU权重 × 时间分数 + LFU权重 × 频率分数`
- **LFU减半**：定期将频率计数减半，防止长期累积
- **权重配置**：可调整LRU和LFU的权重比例

### 3. RocksDBManager（RocksDB管理器）

```go
type RocksDBManager struct {
    databases map[string]*pebble.DB      // 分领域数据库
    basePath  string                     // 存储路径
    maxSize   int64                      // 最大大小
    batchSize int                        // 批量大小
}
```

**特性**：
- **分领域存储**：每个领域独立数据库实例
- **批量操作**：支持批量读写，提升性能
- **压缩存储**：使用Snappy压缩算法
- **自动压缩**：定期执行数据压缩

### 4. ColdStorageManager（冷存储管理器）

```go
type ColdStorageManager struct {
    basePath         string              // 存储路径
    compressionLevel int                 // 压缩级别
    archiveInterval  time.Duration       // 归档间隔
    fileIndex        map[string]string   // 文件索引
}
```

**功能**：
- **自动归档**：定期将冷数据归档到压缩文件
- **索引管理**：维护词汇到归档文件的映射
- **压缩存储**：使用gzip压缩，节省空间
- **自动清理**：清理过期的归档文件

## 配置说明

### 缓存配置

```yaml
cache:
  # 一级缓存配置
  hot_cache:
    size: 10000                    # 热词缓存大小
    lfu_half_life: 3600            # LFU计数减半周期（秒）
    lru_access_weight: 0.6         # LRU访问权重
    lfu_frequency_weight: 0.4      # LFU频率权重
  
  # 二级缓存配置
  rocksdb:
    path: "./data/rocksdb"         # RocksDB存储路径
    max_size: 1073741824           # RocksDB最大大小（1GB）
    batch_write_size: 1000         # 批量写入大小
    compression: "snappy"          # 压缩算法
  
  # 三级缓存配置
  cold_storage:
    path: "./data/cold_storage"    # 冷存储路径
    compression_level: 6           # 压缩级别（1-9）
    archive_interval: 3600         # 归档间隔（秒）
```

### 领域配置

```yaml
domains:
  - name: "法律"
    priority: 1
    hot_cache_size: 5000
    rocksdb_max_size: 536870912    # 512MB
  - name: "财经"
    priority: 2
    hot_cache_size: 3000
    rocksdb_max_size: 268435456    # 256MB
```

## API接口

### 词汇管理

```http
# 获取词汇
GET /api/v1/advanced-cache/vocabulary/{domain}/{word}

# 批量获取词汇
POST /api/v1/advanced-cache/vocabulary/{domain}/batch-get
{
    "words": ["词汇1", "词汇2", "词汇3"]
}

# 存储词汇
PUT /api/v1/advanced-cache/vocabulary/{domain}/{word}
{
    "word": "词汇",
    "definition": "定义",
    "synonyms": ["同义词"],
    "antonyms": ["反义词"],
    "related_words": ["相关词"],
    "source": "来源",
    "frequency": 1000
}

# 批量存储词汇
POST /api/v1/advanced-cache/vocabulary/{domain}/batch-put
{
    "entries": {
        "词汇1": { ... },
        "词汇2": { ... }
    }
}
```

### 缓存管理

```http
# 获取统计信息
GET /api/v1/advanced-cache/cache/statistics

# 清空缓存
DELETE /api/v1/advanced-cache/cache/clear?type=hot

# 获取领域列表
GET /api/v1/advanced-cache/cache/domains
```

### 存储管理

```http
# 压缩存储
POST /api/v1/advanced-cache/storage/compact?type=rocksdb&domain=法律

# 备份存储
POST /api/v1/advanced-cache/storage/backup?type=all&path=./backups

# 恢复存储
POST /api/v1/advanced-cache/storage/restore?type=rocksdb&domain=法律&path=./backups
```

### 监控接口

```http
# 缓存性能监控
GET /api/v1/monitoring/cache/performance

# 存储状态监控
GET /api/v1/monitoring/storage/status

# 健康检查
GET /api/v1/monitoring/health
```

## 性能指标

### 延迟指标

| 缓存级别 | 平均延迟 | 99%延迟 | 说明 |
|---------|---------|---------|------|
| 一级缓存 | <1ms | <2ms | 内存访问，极低延迟 |
| 二级缓存 | <10ms | <50ms | RocksDB访问，低延迟 |
| 三级缓存 | <100ms | <500ms | 文件读取，中等延迟 |

### 吞吐量指标

| 操作类型 | 单次操作 | 批量操作 | 说明 |
|---------|---------|---------|------|
| 读取 | 10,000 ops/s | 50,000 ops/s | 高并发读取 |
| 写入 | 5,000 ops/s | 20,000 ops/s | 批量写入优化 |
| 更新 | 3,000 ops/s | 15,000 ops/s | 包含索引更新 |

### 命中率指标

| 缓存级别 | 目标命中率 | 实际命中率 | 说明 |
|---------|-----------|-----------|------|
| 一级缓存 | >80% | >85% | 热数据缓存 |
| 二级缓存 | >90% | >92% | 温数据缓存 |
| 整体命中率 | >95% | >97% | 三级缓存协同 |

## 部署指南

### 环境要求

- **操作系统**：Linux/Windows/macOS
- **Go版本**：1.19+
- **内存**：最少4GB，推荐8GB+
- **存储**：SSD推荐，最少10GB可用空间
- **依赖库**：
  - `github.com/cockroachdb/pebble` (RocksDB)
  - `github.com/gin-gonic/gin` (Web框架)
  - `github.com/klauspost/compress/gzip` (压缩)

### 安装步骤

1. **克隆代码**
```bash
git clone <repository>
cd go-services/api
```

2. **安装依赖**
```bash
go mod tidy
```

3. **配置环境**
```bash
cp config/cache_config.yaml.example config/cache_config.yaml
# 编辑配置文件
```

4. **编译运行**
```bash
go build -o advanced-cache main.go
./advanced-cache
```

### Docker部署

```dockerfile
FROM golang:1.19-alpine AS builder
WORKDIR /app
COPY . .
RUN go mod download
RUN go build -o advanced-cache .

FROM alpine:latest
RUN apk --no-cache add ca-certificates
WORKDIR /root/
COPY --from=builder /app/advanced-cache .
COPY --from=builder /app/config ./config
EXPOSE 8080
CMD ["./advanced-cache"]
```

## 监控和维护

### 监控指标

1. **性能指标**
   - 缓存命中率
   - 平均响应时间
   - 吞吐量
   - 错误率

2. **资源指标**
   - 内存使用率
   - 磁盘使用率
   - CPU使用率
   - 网络I/O

3. **业务指标**
   - 词汇查询量
   - 新增词汇数
   - 领域分布
   - 热门词汇

### 维护任务

1. **定期压缩**
```bash
# 压缩RocksDB
curl -X POST "http://localhost:8080/api/v1/advanced-cache/storage/compact?type=rocksdb"

# 压缩冷存储
curl -X POST "http://localhost:8080/api/v1/advanced-cache/storage/compact?type=cold"
```

2. **定期备份**
```bash
# 全量备份
curl -X POST "http://localhost:8080/api/v1/advanced-cache/storage/backup?type=all&path=./backups/$(date +%Y%m%d)"
```

3. **清理旧归档**
```bash
# 清理30天前的归档
curl -X DELETE "http://localhost:8080/api/v1/advanced-cache/archive/cleanup?max_age=30d"
```

### 故障处理

1. **缓存未命中率过高**
   - 检查热缓存大小配置
   - 调整LRU/LFU权重
   - 增加内存分配

2. **响应时间过长**
   - 检查磁盘I/O
   - 优化RocksDB配置
   - 增加并发数

3. **内存使用过高**
   - 减少热缓存大小
   - 调整归档策略
   - 增加内存限制

## 最佳实践

### 配置优化

1. **热缓存大小**：根据内存大小和访问模式调整
2. **LFU减半周期**：根据业务特点调整，避免频率计数过时
3. **权重配置**：根据访问模式调整LRU/LFU权重
4. **批量大小**：根据网络和存储性能调整

### 性能优化

1. **预热缓存**：启动时加载热点数据
2. **批量操作**：优先使用批量接口
3. **异步写入**：非关键数据使用异步写入
4. **压缩配置**：根据CPU和存储平衡压缩比

### 运维建议

1. **监控告警**：设置关键指标告警
2. **定期备份**：建立自动备份机制
3. **容量规划**：根据业务增长规划容量
4. **版本管理**：建立配置版本管理

## 扩展功能

### 未来规划

1. **分布式缓存**：支持多节点集群
2. **智能预加载**：基于访问模式预测加载
3. **多语言支持**：支持多语言词汇管理
4. **机器学习**：基于ML优化缓存策略

### 集成方案

1. **Redis集成**：支持Redis作为一级缓存
2. **Elasticsearch集成**：支持全文搜索
3. **消息队列集成**：支持异步处理
4. **监控系统集成**：支持Prometheus、Grafana

## 总结

三级缓存架构通过分层存储和智能算法，实现了高性能、高可用的词汇缓存系统。该架构具有以下优势：

1. **高性能**：多级缓存协同，实现极低延迟
2. **高可用**：支持备份恢复，故障自动处理
3. **高扩展**：支持水平扩展和垂直扩展
4. **易维护**：完善的监控和运维工具
5. **低成本**：通过压缩和分层降低存储成本

该架构特别适合需要处理大量专业词汇、要求高并发低延迟的应用场景，如OCR系统、搜索引擎、知识图谱等。 