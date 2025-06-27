# MaoOCR 前后端优化分级与执行方案

## 一、三色优先级标记

### 红色（高优先级，立即优化）
- **API调用日志与性能趋势可视化**（前端/后端）
  - 前端：ExternalAPIPage、PerformanceOptimizerPage、首页仪表盘
  - 后端：APIManager日志、性能监控、/api/monitoring、/api/logs
- **健康检查与自动切换机制**（后端）
  - 健康状态API、APIManager健康检查、自动降级/切换
- **统一主题与响应式体验**（前端）
  - 全局样式、移动端适配、交互动画
- **PP-OCRv5 + OpenVINO 性能优化**（后端/前端）
  - 后端：OpenVINO引擎优化、动态批处理、设备管理
  - 前端：PP-OCRv5专用界面、设备状态监控、性能对比展示
  - 引擎性能监控、设备切换、推理速度优化

### 黄色（中优先级，近期优化）
- **批量/流式处理接口与前端进度展示**
  - 后端：/api/ocr/batch-recognize-async、WebSocket流式接口
  - 前端：BatchProgressWidget、OCRProgressWidget、批量任务页
- **API适配模板与配置导入导出工具**
  - 后端：APIManager模板、配置导入导出API
  - 前端：ConfigManagerPage、ExternalAPIPage导入导出
- **日志与监控前后端联动展示**
  - 日志聚合、错误趋势、告警、导出
- **PP-OCRv5 引擎集成优化**
  - 后端：多引擎动态权重调整、引擎性能对比API
  - 前端：引擎选择界面、性能对比图表、权重调整控制
  - 智能引擎选择、性能预测、自动优化

### 绿色（低优先级，持续优化）
- **细节美化与用户体验提升**
  - 表单校验、空状态、帮助入口、通知、骨架屏
- **更多图表与可视化增强**
  - 性能趋势、API调用、健康历史等多维度图表
- **移动端深度适配与性能优化**
  - 懒加载、图片压缩、前端性能监控

### 4. PDF文本直提+结构识别方案（建议优先于OCR）

#### 4.1 方案描述
- 对于可复制文本的PDF，优先采用文本解析+版面结构识别（如LayoutLM/Donut等layout LLM），跳过OCR，极大提升效率与准确率。
- 处理流程：PDF解析库提取每页文本及布局 → layout LLM识别结构 → 结构化生成Markdown。
- 针对不可复制文本的PDF，自动切换回OCR识别。

#### 4.2 跨页结构衔接
- 设计"结构状态缓存"，记录每页结尾的段落、表格、列表等未闭合结构。
- 新页开始时，智能判断并合并跨页结构，防止Markdown断裂和布局"断崖"。

#### 4.3 技术实现建议
- 文本与布局提取：PyMuPDF、pdfplumber等
- 结构识别：LayoutLM、Donut、LiLT等
- 跨页结构合并：自定义结构状态缓存与合并逻辑
- Markdown生成：结构树递归生成

#### 4.4 伪代码示例
```python
for page in pdf_pages:
    text_blocks, layout_info = extract_text_and_layout(page)
    structure = layout_llm_infer(text_blocks, layout_info)
    structure = merge_with_previous_page(structure, prev_structure)
    md_content += structure_to_markdown(structure)
    prev_structure = get_page_end_structure(structure)
```

#### 4.5 适用场景
- 可复制文本的PDF（如电子书、报告等），优先走此方案
- 扫描件等不可复制文本PDF，自动切换OCR

#### 4.6 适用场景
- 可复制文本的PDF（如电子书、报告等），优先走此方案
- 扫描件等不可复制文本PDF，自动切换OCR

### 5. EPUB处理方案（扩展支持）

#### 5.1 方案描述
- EPUB作为电子书标准格式，内容本质是HTML+CSS，可通过转换工具转为PDF
- 技术路线：EPUB → PDF转换 → 文本提取 → 结构识别 → Markdown
- 优势：转换后的PDF通常保持较好的文本可提取性，避免OCR的准确性损失

#### 5.2 技术实现建议
- **EPUB转PDF工具**：calibre、pandoc、ebook-convert
- **转换流程**：EPUB文件 → 转换工具 → 临时PDF → 文本提取 → 删除临时文件
- **格式保持**：转换时保持章节结构、目录、样式等

#### 5.3 伪代码示例
```python
def process_epub(epub_path):
    # 1. EPUB转PDF
    pdf_path = convert_epub_to_pdf(epub_path)
    
    # 2. 按PDF流程处理
    if is_text_pdf(pdf_path):
        all_pages_blocks = extract_pdf_layout_blocks(pdf_path)
        md_content = structure_to_markdown(all_pages_blocks)
    else:
        # 转换失败，走OCR流程
        md_content = process_with_ocr(epub_path)
    
    # 3. 清理临时文件
    cleanup_temp_pdf(pdf_path)
    return md_content
```

#### 5.4 依赖管理
```bash
# 安装EPUB转换工具
pip install calibre-python-utils
# 或使用系统calibre
brew install calibre  # macOS
```

#### 5.5 适用场景
- EPUB电子书文件
- 需要保持原格式结构的文档
- 避免OCR准确率损失的场景

### 6. DOCX处理方案（多格式支持）

#### 6.1 方案描述
- DOCX作为Word文档标准格式，支持多级标题、段落、表格、列表等结构化内容
- 技术路线：DOCX解析 → 结构识别 → 跨页衔接 → Markdown生成
- 支持复杂结构：多级目录、题录型结构、思维导图型、编号列表等

#### 6.2 技术实现建议
- **DOCX解析工具**：python-docx（轻量级，性能好）
- **结构识别**：样式识别 + 正则表达式 + 启发式规则
- **特殊结构处理**：
  - 题录型：正则识别题号（1.、A.、1.1等）
  - 思维导图：缩进 + 编号 + 样式推断层级
  - 编号列表：自动编号 + 自定义编号识别

#### 6.3 伪代码示例
```python
def process_docx(docx_path):
    # 1. 解析DOCX结构
    all_pages_blocks = extract_docx_structure_with_cache(docx_path)
    
    # 2. 生成Markdown（支持跨页衔接）
    md_content = structure_to_markdown_with_continuity(all_pages_blocks)
    
    # 3. 保存Markdown文件
    save_markdown(md_content, output_path)
    return output_path
```

#### 6.4 依赖管理
```bash
# 安装DOCX处理工具
pip install python-docx
```

#### 6.5 适用场景
- Word文档（报告、论文、教材、题库等）
- 多级目录结构文档
- 题录型文档（试卷、题库、目录等）
- 思维导图型文档（通过缩进、编号表达层级）

#### 6.6 结构类型支持
- **多级标题**：Heading1/2/3... → #/##/###/...
- **题录型**：1. 题目、A. 子题 → ### 题目、#### 子题
- **编号列表**：1.1、1.2 → **1.1** 内容
- **普通结构**：段落、表格、列表、图片

---

## 二、优化建议与分步计划

### 1. 红色（高优先级）
#### 1.1 API调用日志与性能趋势可视化
- 后端完善APIManager日志记录、性能统计接口（如/api/logs/statistics、/api/monitoring/realtime）。
- 前端ExternalAPIPage、PerformanceOptimizerPage、首页仪表盘增加API调用趋势、成功率、响应时间等折线/柱状/饼图。
- 首页仪表盘增加核心指标卡片（API调用、性能、健康等）。

#### 1.2 健康检查与自动切换机制
- 后端APIManager增加异步健康检查、自动切换、降级处理。
- 健康状态接口（/api/health）完善多维度状态，前端可视化展示。

#### 1.3 统一主题与响应式体验
- 全局主色、字体、按钮、卡片、表格等样式统一。
- 响应式布局、动画、移动端适配优化。

### 2. 黄色（中优先级）
#### 2.1 批量/流式处理接口与前端进度展示
- 后端完善批量/流式API，支持大规模并发、进度查询、结果导出。
- 前端BatchProgressWidget、OCRProgressWidget优化，支持批量任务进度、流式结果展示。

#### 2.2 API适配模板与配置导入导出
- 后端APIManager提供适配模板、配置导入导出API。
- 前端ConfigManagerPage、ExternalAPIPage支持导入导出、批量管理。

#### 2.3 日志与监控前后端联动展示
- 日志聚合、错误趋势、告警、导出API完善。
- 前端日志、告警、趋势图表展示。

#### 2.4 PP-OCRv5 引擎集成优化
- 后端：多引擎动态权重调整、引擎性能对比API
- 前端：引擎选择界面、性能对比图表、权重调整控制
- 智能引擎选择、性能预测、自动优化

### 3. 绿色（低优先级）
#### 3.1 细节美化与用户体验提升
- 表单校验、空状态、帮助入口、通知、骨架屏等细节优化。

#### 3.2 更多图表与可视化增强
- 性能趋势、API调用、健康历史等多维度图表。

#### 3.3 移动端深度适配与性能优化
- 懒加载、图片压缩、前端性能监控、移动端交互优化。

### 4. PDF文本直提+结构识别方案（建议优先于OCR）

#### 4.1 方案描述
- 对于可复制文本的PDF，优先采用文本解析+版面结构识别（如LayoutLM/Donut等layout LLM），跳过OCR，极大提升效率与准确率。
- 处理流程：PDF解析库提取每页文本及布局 → layout LLM识别结构 → 结构化生成Markdown。
- 针对不可复制文本的PDF，自动切换回OCR识别。

#### 4.2 跨页结构衔接
- 设计"结构状态缓存"，记录每页结尾的段落、表格、列表等未闭合结构。
- 新页开始时，智能判断并合并跨页结构，防止Markdown断裂和布局"断崖"。

#### 4.3 技术实现建议
- 文本与布局提取：PyMuPDF、pdfplumber等
- 结构识别：LayoutLM、Donut、LiLT等
- 跨页结构合并：自定义结构状态缓存与合并逻辑
- Markdown生成：结构树递归生成

#### 4.4 伪代码示例
```python
for page in pdf_pages:
    text_blocks, layout_info = extract_text_and_layout(page)
    structure = layout_llm_infer(text_blocks, layout_info)
    structure = merge_with_previous_page(structure, prev_structure)
    md_content += structure_to_markdown(structure)
    prev_structure = get_page_end_structure(structure)
```

#### 4.5 适用场景
- 可复制文本的PDF（如电子书、报告等），优先走此方案
- 扫描件等不可复制文本PDF，自动切换OCR

#### 4.6 适用场景
- 可复制文本的PDF（如电子书、报告等），优先走此方案
- 扫描件等不可复制文本PDF，自动切换OCR

### 5. EPUB处理方案（扩展支持）

#### 5.1 方案描述
- EPUB作为电子书标准格式，内容本质是HTML+CSS，可通过转换工具转为PDF
- 技术路线：EPUB → PDF转换 → 文本提取 → 结构识别 → Markdown
- 优势：转换后的PDF通常保持较好的文本可提取性，避免OCR的准确性损失

#### 5.2 技术实现建议
- **EPUB转PDF工具**：calibre、pandoc、ebook-convert
- **转换流程**：EPUB文件 → 转换工具 → 临时PDF → 文本提取 → 删除临时文件
- **格式保持**：转换时保持章节结构、目录、样式等

#### 5.3 伪代码示例
```python
def process_epub(epub_path):
    # 1. EPUB转PDF
    pdf_path = convert_epub_to_pdf(epub_path)
    
    # 2. 按PDF流程处理
    if is_text_pdf(pdf_path):
        all_pages_blocks = extract_pdf_layout_blocks(pdf_path)
        md_content = structure_to_markdown(all_pages_blocks)
    else:
        # 转换失败，走OCR流程
        md_content = process_with_ocr(epub_path)
    
    # 3. 清理临时文件
    cleanup_temp_pdf(pdf_path)
    return md_content
```

#### 5.4 依赖管理
```bash
# 安装EPUB转换工具
pip install calibre-python-utils
# 或使用系统calibre
brew install calibre  # macOS
```

#### 5.5 适用场景
- EPUB电子书文件
- 需要保持原格式结构的文档
- 避免OCR准确率损失的场景

### 6. DOCX处理方案（多格式支持）

#### 6.1 方案描述
- DOCX作为Word文档标准格式，支持多级标题、段落、表格、列表等结构化内容
- 技术路线：DOCX解析 → 结构识别 → 跨页衔接 → Markdown生成
- 支持复杂结构：多级目录、题录型结构、思维导图型、编号列表等

#### 6.2 技术实现建议
- **DOCX解析工具**：python-docx（轻量级，性能好）
- **结构识别**：样式识别 + 正则表达式 + 启发式规则
- **特殊结构处理**：
  - 题录型：正则识别题号（1.、A.、1.1等）
  - 思维导图：缩进 + 编号 + 样式推断层级
  - 编号列表：自动编号 + 自定义编号识别

#### 6.3 伪代码示例
```python
def process_docx(docx_path):
    # 1. 解析DOCX结构
    all_pages_blocks = extract_docx_structure_with_cache(docx_path)
    
    # 2. 生成Markdown（支持跨页衔接）
    md_content = structure_to_markdown_with_continuity(all_pages_blocks)
    
    # 3. 保存Markdown文件
    save_markdown(md_content, output_path)
    return output_path
```

#### 6.4 依赖管理
```bash
# 安装DOCX处理工具
pip install python-docx
```

#### 6.5 适用场景
- Word文档（报告、论文、教材、题库等）
- 多级目录结构文档
- 题录型文档（试卷、题库、目录等）
- 思维导图型文档（通过缩进、编号表达层级）

#### 6.6 结构类型支持
- **多级标题**：Heading1/2/3... → #/##/###/...
- **题录型**：1. 题目、A. 子题 → ### 题目、#### 子题
- **编号列表**：1.1、1.2 → **1.1** 内容
- **普通结构**：段落、表格、列表、图片

---

## 三、分步执行计划

1. **第一步（红色）**
   - 优化API调用日志与性能趋势可视化（前后端联动）。
   - 健康检查与自动切换机制完善。
   - 统一主题与响应式体验。
2. **第二步（黄色）**
   - 批量/流式处理接口与前端进度展示。
   - API适配模板与配置导入导出。
   - 日志与监控前后端联动展示。
3. **第三步（绿色）**
   - 细节美化与用户体验提升。
   - 更多图表与可视化增强。
   - 移动端深度适配与性能优化。

---

> 本文档为MaoOCR系统前后端优化分级与执行路线图，建议团队严格按照优先级分步推进，确保核心体验与系统健壮性优先达标。