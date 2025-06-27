# 文档命名规范指南

## 1. 文件命名规范

### 1.1 基本规则
- 使用小写字母
- 单词间使用连字符(-)分隔
- 使用有意义的描述性名称
- 文件扩展名使用小写（.md, .txt等）

### 1.2 命名模式
- 指南类文档：`{主题}-guide.md`
- 参考类文档：`{主题}-reference.md`
- 教程类文档：`{主题}-tutorial.md`
- 示例类文档：`{主题}-examples.md`

### 1.3 示例
✅ 正确示例：
- `quick-start-guide.md`
- `api-reference.md`
- `development-guidelines.md`
- `security-best-practices.md`

❌ 错误示例：
- `QuickStart.md`
- `api_reference.md`
- `development.md`
- `SECURITY.md`

## 2. 目录命名规范

### 2.1 基本规则
- 使用小写字母
- 单词间使用连字符(-)分隔
- 使用复数形式表示包含多个文件的目录
- 使用描述性名称

### 2.2 命名模式
- 功能模块：`{模块名}s/`
- 资源目录：`{资源类型}s/`
- 示例目录：`examples/`

### 2.3 示例
✅ 正确示例：
- `getting-started/`
- `user-guides/`
- `api-docs/`
- `code-examples/`

❌ 错误示例：
- `GettingStarted/`
- `user_guide/`
- `API/`
- `examples/`

## 3. 文档标题规范

### 3.1 基本规则
- 使用标题大小写（Title Case）
- 保持简洁明了
- 避免使用缩写（除非是广泛接受的缩写）

### 3.2 示例
✅ 正确示例：
- "Quick Start Guide"
- "API Reference"
- "Development Guidelines"
- "Security Best Practices"

❌ 错误示例：
- "quick start guide"
- "API REFERENCE"
- "development guidelines"
- "SECURITY BEST PRACTICES"

## 4. 需要重命名的文件

### 4.1 文件重命名
当前文件 -> 新文件名
```
project_knowledge.md -> project-knowledge.md
rename_guide.md -> rename-guide.md
project_learning_guide.md -> learning-guide.md
local_debug_guide.md -> debug-guide.md
test_coverage.md -> test-coverage.md
PERFORMANCE_RULES.md -> performance-rules.md
README_CN.md -> readme-cn.md
development_guidelines.md -> development-guidelines.md
CODE_OF_CONDUCT.md -> code-of-conduct.md
CONTRIBUTING.md -> contributing.md
SECURITY.md -> security.md
law_book_list.txt -> law-book-list.txt
```

### 4.2 目录重命名
当前目录 -> 新目录名
```
finetune/ -> finetuning/
words/ -> word-lists/
dockerfile/ -> docker-files/
rename/ -> rename-guides/
user_guide/ -> user-guides/
typical_implementation/ -> implementation-examples/
tutorial/ -> tutorials/
readme/ -> readmes/
evaluation_report/ -> evaluation-reports/
```

## 5. 实施建议

1. **分步实施**
   - 先重命名文件
   - 再重命名目录
   - 最后更新引用

2. **更新引用**
   - 更新所有文档中的交叉引用
   - 更新导航菜单
   - 更新索引文件

3. **验证检查**
   - 检查所有链接是否有效
   - 确保文档可以正常访问
   - 验证搜索功能

4. **文档更新**
   - 更新相关文档中的路径引用
   - 更新README文件
   - 更新贡献指南

## 6. 注意事项

1. **版本控制**
   - 使用git mv命令进行重命名
   - 保持文件历史记录
   - 提交清晰的提交信息

2. **兼容性**
   - 确保重命名不影响现有链接
   - 保持向后兼容性
   - 考虑URL兼容性

3. **文档维护**
   - 定期检查命名规范
   - 及时纠正不规范命名
   - 保持命名一致性 