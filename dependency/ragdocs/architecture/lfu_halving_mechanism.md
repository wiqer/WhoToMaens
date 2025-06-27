# LFU减半机制设计与实现

## 概述

LFU（Least Frequently Used）减半机制是混合LRU+LFU缓存算法的核心组件，用于防止频率分数爆炸，确保缓存算法的稳定性和有效性。

## 问题背景

### 传统LFU算法的问题

1. **频率分数爆炸**：随着时间推移，高频访问的词汇频率计数会无限增长
2. **数值溢出风险**：频率计数可能超过int64的最大值
3. **算法失效**：频率差异过大导致LFU算法失去区分能力
4. **内存占用**：大数值占用更多内存空间

### 解决方案

通过定期减半所有词汇的频率计数，保持频率分数的相对关系，同时防止数值爆炸。

## 设计原理

### 减半触发条件

```go
// 检查是否达到减半条件
timeCondition := time.Since(hlc.lastHalfTime).Seconds() >= float64(hlc.lfuHalfLife)
frequencyCondition := hlc.maxFrequency > 10000 // 频率阈值

if timeCondition || frequencyCondition {
    hlc.halveLFUCounts()
}
```

**双重触发机制**：
1. **时间触发**：每隔配置的时间周期（默认3600秒）自动减半
2. **频率触发**：当最大频率值超过阈值（默认10000）时立即减半

### 减半算法

```go
func (hlc *HybridLRULFUCache) halveLFUCounts() {
    // 执行减半操作
    for key, count := range hlc.frequencyMap {
        hlc.frequencyMap[key] = count / 2
    }
    
    // 重新计算最大频率值
    hlc.maxFrequency = 0
    for _, count := range hlc.frequencyMap {
        if count > hlc.maxFrequency {
            hlc.maxFrequency = count
        }
    }
}
```

### 频率归一化

为了防止频率分数过大影响混合算法，使用归一化处理：

```go
// LFU分数：基于访问频率（频率越低分数越高）
var lfuScore float64
if hlc.maxFrequency > 0 {
    // 归一化到0-1范围，然后取反（频率越高分数越低）
    normalizedFreq := float64(hlc.frequencyMap[key]) / float64(hlc.maxFrequency)
    lfuScore = 1.0 - normalizedFreq
} else {
    lfuScore = 0.0
}
```

## 实现细节

### 数据结构

```go
type HybridLRULFUCache struct {
    // LFU减半相关
    lastHalfTime  time.Time    // 上次减半时间
    halfLifeCount int64        // 减半次数统计
    maxFrequency  int64        // 最大频率值，用于归一化
    
    // 其他字段...
}
```

### 核心方法

#### 1. 检查减半条件

```go
func (hlc *HybridLRULFUCache) checkAndHalveCounts() {
    timeCondition := time.Since(hlc.lastHalfTime).Seconds() >= float64(hlc.lfuHalfLife)
    frequencyCondition := hlc.maxFrequency > 10000
    
    if timeCondition || frequencyCondition {
        hlc.halveLFUCounts()
    }
}
```

#### 2. 执行减半操作

```go
func (hlc *HybridLRULFUCache) halveLFUCounts() {
    // 记录减半前的统计信息
    beforeMaxFreq := hlc.maxFrequency
    beforeTotalFreq := int64(0)
    for _, count := range hlc.frequencyMap {
        beforeTotalFreq += count
    }
    
    // 执行减半操作
    for key, count := range hlc.frequencyMap {
        hlc.frequencyMap[key] = count / 2
    }
    
    // 重新计算最大频率值
    hlc.maxFrequency = 0
    for _, count := range hlc.frequencyMap {
        if count > hlc.maxFrequency {
            hlc.maxFrequency = count
        }
    }
    
    // 更新统计信息
    hlc.halfLifeCount++
    hlc.lastHalfTime = time.Now()
}
```

#### 3. 获取LFU统计信息

```go
func (hlc *HybridLRULFUCache) GetLFUStats() map[string]interface{} {
    // 计算频率分布
    freqDistribution := make(map[string]int)
    for _, freq := range hlc.frequencyMap {
        switch {
        case freq <= 1:
            freqDistribution["1"]++
        case freq <= 5:
            freqDistribution["2-5"]++
        // ... 其他区间
        }
    }
    
    return map[string]interface{}{
        "max_frequency":     hlc.maxFrequency,
        "average_frequency": avgFreq,
        "total_entries":     totalEntries,
        "half_life_count":   hlc.halfLifeCount,
        "last_half_time":    hlc.lastHalfTime,
        "frequency_distribution": freqDistribution,
    }
}
```

## 配置参数

### 配置文件示例

```yaml
cache:
  hot_cache:
    lfu_half_life: 3600            # LFU计数减半周期（秒）
    max_frequency_threshold: 10000 # 最大频率阈值
  
  monitoring:
    frequency_alert_threshold: 50000  # 频率告警阈值
    average_frequency_alert: 1000     # 平均频率告警阈值
    half_life_alert_minutes: 60       # 减半告警时间（分钟）

algorithm:
  lfu_halving:
    time_based: true           # 基于时间的减半
    frequency_based: true      # 基于频率的减半
    adaptive_threshold: true   # 自适应阈值
```

### 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `lfu_half_life` | 3600 | LFU计数减半周期（秒） |
| `max_frequency_threshold` | 10000 | 最大频率阈值 |
| `frequency_alert_threshold` | 50000 | 频率告警阈值 |
| `average_frequency_alert` | 1000 | 平均频率告警阈值 |

## 监控与告警

### 监控指标

1. **最大频率值**：当前缓存中词汇的最大访问频率
2. **平均频率值**：所有词汇的平均访问频率
3. **减半次数**：累计执行减半操作的次数
4. **频率分布**：不同频率区间的词汇数量分布
5. **减半间隔**：距离上次减半的时间

### 告警条件

```go
// 检查是否需要告警
if maxFreq > 50000 {
    fmt.Printf("⚠️ 警告: 最大频率值过高 (%d), 可能需要调整减半策略\n", maxFreq)
}

if avgFreq > 1000 {
    fmt.Printf("⚠️ 警告: 平均频率值过高 (%.2f), 缓存可能过于集中\n", avgFreq)
}

if timeSinceLastHalf > 60 { // 超过1小时没有减半
    fmt.Printf("⚠️ 警告: 距离上次减半已过去 %.1f 分钟\n", timeSinceLastHalf)
}
```

## 性能优化

### 1. 批量减半操作

减半操作在单个锁保护下批量执行，减少锁竞争：

```go
func (hlc *HybridLRULFUCache) halveLFUCounts() {
    // 在Get/Put方法中已经持有锁，无需额外加锁
    for key, count := range hlc.frequencyMap {
        hlc.frequencyMap[key] = count / 2
    }
}
```

### 2. 延迟计算最大频率

最大频率值在需要时重新计算，避免每次访问都更新：

```go
// 只在减半时重新计算最大频率
hlc.maxFrequency = 0
for _, count := range hlc.frequencyMap {
    if count > hlc.maxFrequency {
        hlc.maxFrequency = count
    }
}
```

### 3. 统计信息缓存

LFU统计信息按需计算，避免频繁计算：

```go
func (hlc *HybridLRULFUCache) GetLFUStats() map[string]interface{} {
    hlc.mutex.RLock()
    defer hlc.mutex.RUnlock()
    
    // 按需计算统计信息
    // ...
}
```

## 测试验证

### 测试用例

1. **基本减半测试**：验证减半机制正常工作
2. **频率爆炸防护测试**：验证极端高频访问下的防护效果
3. **混合算法效果测试**：验证减半对混合算法的影响
4. **性能监控测试**：验证监控和告警功能

### 测试示例

```go
func testBasicLFUHalving(cacheManager *services.AdvancedCacheManager) {
    // 模拟高频访问
    for i := 0; i < 50; i++ {
        cacheManager.Get("测试", "测试词1")
    }
    
    // 获取减半前统计
    lfuStats := cacheManager.hotCache.GetLFUStats()
    fmt.Printf("减半前: 最大频率=%d\n", lfuStats["max_frequency"])
    
    // 等待减半触发
    time.Sleep(12 * time.Second)
    
    // 获取减半后统计
    lfuStats = cacheManager.hotCache.GetLFUStats()
    fmt.Printf("减半后: 最大频率=%d, 减半次数=%d\n", 
        lfuStats["max_frequency"], lfuStats["half_life_count"])
}
```

## API接口

### 获取LFU统计信息

```http
GET /api/v1/cache/lfu-statistics
```

响应示例：
```json
{
  "lfu_statistics": {
    "max_frequency": 5000,
    "average_frequency": 250.5,
    "total_entries": 1000,
    "half_life_count": 3,
    "last_half_time": "2024-01-01T12:00:00Z",
    "frequency_distribution": {
      "1": 500,
      "2-5": 300,
      "6-10": 150,
      "11-50": 40,
      "51-100": 8,
      "100+": 2
    }
  },
  "algorithm_info": {
    "lru_weight": 0.6,
    "lfu_weight": 0.4,
    "lfu_half_life": 3600,
    "max_frequency_threshold": 10000
  }
}
```

### 获取算法详细信息

```http
GET /api/v1/cache/algorithm-info
```

响应示例：
```json
{
  "algorithm": "Hybrid LRU+LFU with Frequency Halving",
  "description": "结合LRU（最近最少使用）和LFU（最不经常使用）的混合算法，支持频率计数自动减半防止分数爆炸",
  "current_state": {
    "hot_cache_size": 1000,
    "lfu_statistics": { ... }
  },
  "efficiency_metrics": {
    "frequency_health": 0.8,
    "max_frequency_ratio": 20.0,
    "half_life_efficiency": 3,
    "frequency_stability": true
  },
  "algorithm_features": [
    "自动频率减半防止分数爆炸",
    "归一化频率分数避免数值过大",
    "权重可配置的混合评分",
    "实时监控和告警机制",
    "详细的淘汰原因记录"
  ]
}
```

## 最佳实践

### 1. 配置调优

- **减半周期**：根据访问模式调整，高频访问场景可缩短周期
- **频率阈值**：根据内存限制和性能要求调整
- **权重配置**：根据业务特点调整LRU和LFU权重

### 2. 监控建议

- 定期检查频率分布，确保算法效果
- 监控减半频率，避免过于频繁的减半操作
- 关注告警信息，及时调整配置参数

### 3. 性能优化

- 合理设置缓存大小，避免频繁淘汰
- 监控内存使用，及时调整配置
- 定期清理冷数据，释放存储空间

## 总结

LFU减半机制通过双重触发条件和归一化处理，有效解决了传统LFU算法的频率爆炸问题。该机制具有以下特点：

1. **自动触发**：基于时间和频率双重条件自动减半
2. **保持相对关系**：减半操作保持词汇间的频率相对关系
3. **防止数值爆炸**：有效控制频率数值范围
4. **性能优化**：批量操作和延迟计算提升性能
5. **监控完善**：提供详细的统计信息和告警机制

该机制为混合LRU+LFU缓存算法提供了稳定可靠的基础，确保在高并发场景下的良好表现。 