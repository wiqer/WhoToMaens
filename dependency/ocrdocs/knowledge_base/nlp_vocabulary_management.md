# MaoOCR NLP词库管理系统设计

## 📋 概述

本文档描述了MaoOCR项目中NLP词库管理系统的设计方案，包括词库存储、热词缓存、更新机制等核心功能。

## 🎯 系统目标

### 1. **词库管理目标**
- 高效存储和管理大规模NLP词库
- 支持多领域专业词汇的快速检索
- 实现热词缓存机制提升查询性能
- 建立自动化的词库更新机制

### 2. **技术目标**
- 使用RocksDB作为底层存储引擎
- 实现多重哈希技术构建热词缓存
- 优化CPU开销，使用位运算扩展哈希算法
- 支持每周/每月频度的词库更新

## 🔧 系统架构

### 整体架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    NLP词库管理系统                           │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  词库更新器  │  │  词库管理器  │  │  热词缓存器  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  RocksDB    │  │  多重哈希    │  │  位运算优化  │         │
│  │   存储层     │  │   索引层     │  │   算法层     │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

## 📊 数据模型设计

### 1. **词库数据结构**
```python
class VocabularyEntry:
    """词库条目"""
    def __init__(self):
        self.word: str = ""                    # 词汇
        self.domain: str = ""                  # 领域分类
        self.frequency: int = 0                # 使用频率
        self.confidence: float = 0.0           # 置信度
        self.synonyms: List[str] = []          # 同义词
        self.antonyms: List[str] = []          # 反义词
        self.related_words: List[str] = []     # 相关词
        self.update_time: datetime = None      # 更新时间
        self.source: str = ""                  # 数据源
        self.metadata: Dict[str, Any] = {}     # 元数据
```

### 2. **RocksDB存储设计**
```python
class RocksDBVocabularyStore:
    """RocksDB词库存储"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.db = None
        self.cf_handles = {}
        
        # 列族设计
        self.column_families = {
            'words': '词汇主表',
            'domains': '领域索引',
            'frequency': '频率索引',
            'synonyms': '同义词索引',
            'entities': '实体索引',
            'metadata': '元数据表'
        }
    
    def initialize_db(self):
        """初始化数据库"""
        # 创建列族
        for cf_name in self.column_families.keys():
            self.cf_handles[cf_name] = self.db.create_column_family(cf_name)
        
        # 设置优化选项
        self.db.set_options({
            'max_background_jobs': 4,
            'write_buffer_size': 64 * 1024 * 1024,  # 64MB
            'max_write_buffer_number': 3,
            'target_file_size_base': 64 * 1024 * 1024,  # 64MB
            'compression': 'lz4'
        })
```

## 🔍 多重哈希索引设计

### 1. **哈希算法优化**
```python
class OptimizedHashIndex:
    """优化的哈希索引"""
    
    def __init__(self):
        self.base_hash = hashlib.md5
        self.hash_cache = {}
    
    def compute_hash(self, word: str) -> int:
        """计算词汇哈希值"""
        if word in self.hash_cache:
            return self.hash_cache[word]
        
        # 基础哈希
        base_hash = self.base_hash(word.encode('utf-8')).hexdigest()
        hash_int = int(base_hash[:8], 16)
        
        # 缓存结果
        self.hash_cache[word] = hash_int
        return hash_int
    
    def compute_variant_hashes(self, word: str) -> List[int]:
        """计算变体哈希值（使用位运算）"""
        base_hash = self.compute_hash(word)
        variants = []
        
        # 通过位运算生成变体哈希
        variants.append(base_hash)                    # 原始哈希
        variants.append(base_hash << 1)               # 左移1位
        variants.append(base_hash >> 1)               # 右移1位
        variants.append(base_hash ^ 0xFFFFFFFF)       # 按位取反
        variants.append(base_hash + 0x12345678)       # 加法运算
        variants.append(base_hash * 0x87654321)       # 乘法运算
        
        return variants
```

### 2. **热词缓存机制**
```python
class HotWordCache:
    """热词缓存"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache = {}
        self.access_count = {}
        self.hash_index = OptimizedHashIndex()
    
    def get(self, word: str) -> Optional[VocabularyEntry]:
        """获取词汇（优先从缓存）"""
        # 1. 检查缓存
        if word in self.cache:
            self.access_count[word] += 1
            return self.cache[word]
        
        # 2. 计算哈希变体
        hash_variants = self.hash_index.compute_variant_hashes(word)
        
        # 3. 从RocksDB查询
        entry = self._query_from_db(hash_variants, word)
        
        # 4. 更新缓存
        if entry:
            self._update_cache(word, entry)
        
        return entry
    
    def _update_cache(self, word: str, entry: VocabularyEntry):
        """更新缓存"""
        if len(self.cache) >= self.max_size:
            # LRU淘汰策略
            self._evict_least_used()
        
        self.cache[word] = entry
        self.access_count[word] = 1
    
    def _evict_least_used(self):
        """淘汰最少使用的词汇"""
        if not self.access_count:
            return
        
        # 找到访问次数最少的词汇
        min_word = min(self.access_count.keys(), 
                      key=lambda k: self.access_count[k])
        
        # 从缓存中移除
        del self.cache[min_word]
        del self.access_count[min_word]
```

## 🔄 词库更新机制

### 1. **自动更新调度器**
```python
class VocabularyUpdateScheduler:
    """词库更新调度器"""
    
    def __init__(self):
        self.update_sources = {
            'funNLP': {
                'url': 'https://github.com/wiqer/funNLP',
                'frequency': 'weekly',
                'last_update': None,
                'enabled': True
            },
            'other_sources': {
                'url': 'https://github.com/other/nlp-resources',
                'frequency': 'monthly',
                'last_update': None,
                'enabled': True
            }
        }
        self.scheduler = None
    
    def start_scheduler(self):
        """启动更新调度器"""
        self.scheduler = BackgroundScheduler()
        
        # 添加定时任务
        for source_name, config in self.update_sources.items():
            if config['enabled']:
                if config['frequency'] == 'weekly':
                    self.scheduler.add_job(
                        self._update_vocabulary,
                        'interval',
                        weeks=1,
                        args=[source_name],
                        id=f'update_{source_name}'
                    )
                elif config['frequency'] == 'monthly':
                    self.scheduler.add_job(
                        self._update_vocabulary,
                        'interval',
                        months=1,
                        args=[source_name],
                        id=f'update_{source_name}'
                    )
        
        self.scheduler.start()
    
    def _update_vocabulary(self, source_name: str):
        """更新词库"""
        try:
            logger.info(f"开始更新词库: {source_name}")
            
            # 1. 获取最新数据
            new_data = self._fetch_latest_data(source_name)
            
            # 2. 数据预处理
            processed_data = self._preprocess_data(new_data)
            
            # 3. 更新存储
            self._update_storage(processed_data)
            
            # 4. 更新缓存
            self._update_cache(processed_data)
            
            # 5. 记录更新时间
            self.update_sources[source_name]['last_update'] = datetime.now()
            
            logger.info(f"词库更新完成: {source_name}")
            
        except Exception as e:
            logger.error(f"词库更新失败: {source_name}, 错误: {e}")
```

### 2. **数据源集成**
```python
class NLPDataSource:
    """NLP数据源管理器"""
    
    def __init__(self):
        self.sources = {
            'funNLP': FunNLPSource(),
            'THUDM': THUDMSource(),
            'HIT': HITSource(),
            'PKU': PKUSource()
        }
    
    def fetch_funNLP_data(self) -> Dict[str, Any]:
        """获取funNLP数据"""
        source = self.sources['funNLP']
        return source.fetch_data()
    
    def fetch_all_sources(self) -> Dict[str, Any]:
        """获取所有数据源"""
        all_data = {}
        for source_name, source in self.sources.items():
            try:
                data = source.fetch_data()
                all_data[source_name] = data
            except Exception as e:
                logger.error(f"获取数据源失败: {source_name}, 错误: {e}")
        
        return all_data

class FunNLPSource:
    """funNLP数据源"""
    
    def __init__(self):
        self.base_url = "https://github.com/wiqer/funNLP"
        self.data_paths = {
            'financial': '/data/financial',
            'medical': '/data/medical', 
            'legal': '/data/legal',
            'education': '/data/education',
            'technology': '/data/technology'
        }
    
    def fetch_data(self) -> Dict[str, Any]:
        """获取funNLP数据"""
        data = {}
        
        for domain, path in self.data_paths.items():
            try:
                # 这里需要实现具体的GitHub API调用
                domain_data = self._fetch_domain_data(domain, path)
                data[domain] = domain_data
            except Exception as e:
                logger.error(f"获取{domain}数据失败: {e}")
        
        return data
    
    def _fetch_domain_data(self, domain: str, path: str) -> List[str]:
        """获取特定领域数据"""
        # 实现GitHub API调用逻辑
        # 这里需要根据实际的funNLP项目结构来实现
        pass
```

## 🎯 集成到纠错系统

### 1. **词库增强的纠错器**
```python
class VocabularyEnhancedCorrector:
    """词库增强的纠错器"""
    
    def __init__(self):
        self.vocabulary_store = RocksDBVocabularyStore("vocabulary.db")
        self.hot_cache = HotWordCache()
        self.domain_classifier = DomainClassifier()
    
    def correct_with_vocabulary(self, text: str, document_type: str = 'auto') -> Dict[str, Any]:
        """基于词库的纠错"""
        corrections = []
        
        # 1. 领域分类
        if document_type == 'auto':
            document_type = self.domain_classifier.classify(text)
        
        # 2. 分词处理
        words = self._tokenize(text)
        
        # 3. 词汇纠错
        for word in words:
            correction = self._correct_word(word, document_type)
            if correction:
                corrections.append(correction)
        
        # 4. 同义词替换
        synonym_corrections = self._apply_synonym_corrections(text, document_type)
        corrections.extend(synonym_corrections)
        
        # 5. 实体纠错
        entity_corrections = self._correct_entities(text, document_type)
        corrections.extend(entity_corrections)
        
        return {
            'corrected_text': self._apply_corrections(text, corrections),
            'corrections_applied': corrections,
            'domain': document_type
        }
    
    def _correct_word(self, word: str, domain: str) -> Optional[Dict[str, Any]]:
        """词汇纠错"""
        # 1. 检查热词缓存
        cached_entry = self.hot_cache.get(word)
        if cached_entry and cached_entry.domain == domain:
            return None  # 词汇正确
        
        # 2. 查询词库
        entry = self.vocabulary_store.get_word(word, domain)
        if entry:
            return None  # 词汇存在
        
        # 3. 查找相似词汇
        similar_words = self.vocabulary_store.find_similar_words(word, domain)
        if similar_words:
            best_match = max(similar_words, key=lambda x: x.confidence)
            return {
                'type': 'vocabulary_correction',
                'original': word,
                'corrected': best_match.word,
                'confidence': best_match.confidence,
                'domain': domain
            }
        
        return None
```

### 2. **性能优化策略**
```python
class VocabularyPerformanceOptimizer:
    """词库性能优化器"""
    
    def __init__(self):
        self.hash_optimizer = OptimizedHashIndex()
        self.cache_manager = CacheManager()
        self.query_optimizer = QueryOptimizer()
    
    def optimize_query(self, query: str) -> str:
        """查询优化"""
        return self.query_optimizer.optimize(query)
    
    def preload_hot_words(self, domain: str):
        """预加载热词"""
        hot_words = self._get_hot_words(domain)
        for word in hot_words:
            self.cache_manager.preload(word)
    
    def _get_hot_words(self, domain: str) -> List[str]:
        """获取领域热词"""
        # 基于使用频率获取热词
        return self.vocabulary_store.get_hot_words(domain, limit=1000)
```

## 📊 监控和统计

### 1. **性能监控**
```python
class VocabularyMonitor:
    """词库监控器"""
    
    def __init__(self):
        self.metrics = {
            'query_count': 0,
            'cache_hit_rate': 0.0,
            'update_frequency': {},
            'error_rate': 0.0
        }
    
    def record_query(self, cache_hit: bool):
        """记录查询"""
        self.metrics['query_count'] += 1
        if cache_hit:
            self.metrics['cache_hit_rate'] = (
                self.metrics['cache_hit_rate'] * 0.9 + 0.1
            )
        else:
            self.metrics['cache_hit_rate'] = (
                self.metrics['cache_hit_rate'] * 0.9
            )
    
    def get_performance_report(self) -> Dict[str, Any]:
        """获取性能报告"""
        return {
            'total_queries': self.metrics['query_count'],
            'cache_hit_rate': self.metrics['cache_hit_rate'],
            'average_query_time': self._calculate_avg_query_time(),
            'vocabulary_size': self._get_vocabulary_size(),
            'last_update': self._get_last_update_time()
        }
```

## 🚀 实施计划

### **阶段一：基础架构（1-2周）**
- [ ] 实现RocksDB存储层
- [ ] 实现多重哈希索引
- [ ] 实现热词缓存机制
- [ ] 基础性能测试

### **阶段二：数据源集成（2-3周）**
- [ ] 集成funNLP数据源
- [ ] 实现数据预处理
- [ ] 建立更新调度器
- [ ] 数据质量验证

### **阶段三：纠错集成（1-2周）**
- [ ] 集成到纠错系统
- [ ] 实现领域分类
- [ ] 优化查询性能
- [ ] 完善错误处理

### **阶段四：优化完善（持续）**
- [ ] 性能优化
- [ ] 监控系统
- [ ] 扩展数据源
- [ ] 用户界面

## 📋 总结

通过集成funNLP等中文NLP资源库，MaoOCR的词库管理系统将具备：

1. **高效存储**: RocksDB + 多重哈希索引
2. **智能缓存**: 热词缓存 + LRU淘汰策略
3. **自动更新**: 定时更新 + 多数据源支持
4. **性能优化**: 位运算优化 + 查询优化
5. **领域适应**: 多领域词汇 + 专业术语支持

这将显著提升OCR纠错的准确性和效率，特别是在处理专业文档时。

## 🛠️ funNLP资源适配与自动化导入

### 1. 资源结构说明
- funNLP资源位于 `dependency/funNLP/data/` 目录下，按领域分为多个子目录（如医学词库、法律词库、IT词库等）。
- 每个领域下为若干 `.txt` 文件，内容格式通常为：
  ```
  词语<tab/空格>频次
  ```

### 2. 自动化导入脚本
- 脚本位置：`src/maoocr/utils/vocabulary_importer.py`
- 功能：自动遍历 funNLP 所有领域词库，批量导入到MaoOCR的内存结构（可扩展为RocksDB/缓存等）。
- 支持领域名自动映射、属性扩展。

#### 用法示例
```bash
python src/maoocr/utils/vocabulary_importer.py
```
- 可在脚本内自定义领域映射表（如：'医学词库' -> 'medical'）。
- 导入后可获得所有词条的标准化结构（`VocabularyEntry`）。

#### 主要代码片段
```python
class VocabularyImporter:
    def __init__(self, funnlp_data_dir: str, domain_mapping: Optional[Dict[str, str]] = None):
        ...
    def import_all(self):
        ... # 自动遍历所有领域和词库文件
    def _import_file(self, file_path: str, domain: str):
        ... # 解析每一行，支持tab/空格分隔
```

### 3. 领域映射机制
- 支持自定义 funNLP 领域名与MaoOCR内部领域名的映射。
- 只需在 `domain_mapping` 字典中配置，如：
  ```python
  domain_mapping = {
      '医学词库': 'medical',
      '法律词库': 'legal',
      'IT词库': 'it',
      '财经词库': 'financial',
      '教育词库': 'education',
      '职业词库': 'occupation',
      '地名词库': 'geography',
      '历史名人词库': 'history',
      '公司名字词库': 'company',
      '中英日文名字库': 'name',
  }
  ```
- 未配置的领域将自动使用原目录名。

### 4. 属性扩展机制
- 默认支持"词语、领域、频次、更新时间、来源"等属性。
- 可在 `_import_file` 方法中扩展解析更多字段（如同义词、实体类型等）。
- 支持后续与RocksDB、热词缓存等结构集成。

### 5. 适配建议
- funNLP结构与MaoOCR词库管理高度兼容，建议统一采用`VocabularyEntry`抽象。
- 可灵活扩展新领域和属性，主系统无需改动。
- 支持定期自动同步和批量导入。

### 6. 领域映射机制（详细说明）
- 领域映射机制允许将funNLP的目录名（如"医学词库"）自动映射为MaoOCR内部标准领域名（如"medical"）。
- 只需在导入脚本的`domain_mapping`字典中配置映射关系。
- 支持灵活扩展和自定义，未配置的领域将自动使用原目录名。

#### 代码示例：
```python
# 领域映射表
DOMAIN_MAPPING = {
    '医学词库': 'medical',
    '法律词库': 'legal',
    'IT词库': 'it',
    '财经词库': 'financial',
    '教育词库': 'education',
    '职业词库': 'occupation',
    '地名词库': 'geography',
    '历史名人词库': 'history',
    '公司名字词库': 'company',
    '中英日文名字库': 'name',
}

importer = VocabularyImporter(funnlp_data_dir, DOMAIN_MAPPING)
```

### 7. 属性扩展机制（详细说明）
- funNLP词库文件通常为"词语+频次"格式，部分领域可能包含更多属性。
- 可在`VocabularyEntry`中扩展如"同义词、实体类型、来源、更新时间"等属性。
- 在`VocabularyImporter._import_file`方法中可根据实际文件格式解析更多字段。

#### 代码示例：
```python
class VocabularyEntry:
    def __init__(self, word, domain, frequency=0, confidence=0.0, synonyms=None, entity_type=None, source="funNLP"):
        self.word = word
        self.domain = domain
        self.frequency = frequency
        self.confidence = confidence
        self.synonyms = synonyms or []
        self.entity_type = entity_type
        self.source = source
        self.update_time = datetime.now()
```

- 若某些词库文件包含同义词、实体类型等，可在`_import_file`中解析并赋值。
- 例如：
```python
if len(parts) >= 3:
    word, freq, entity_type = parts[:3]
    entry = VocabularyEntry(word=word, domain=domain, frequency=int(freq), entity_type=entity_type)
```

---

如需将词库导入RocksDB或缓存，只需在导入后遍历`entries`，调用相应的存储/缓存API即可。 