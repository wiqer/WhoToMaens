# 文档重构实施指南

## 1. 分步实施计划

### 1.1 准备阶段
1. **备份当前文档**
   ```bash
   # 创建文档备份
   cp -r docs docs_backup_$(date +%Y%m%d)
   ```

2. **创建新目录结构**
   ```bash
   # 创建主要目录
   mkdir -p docs/{getting-started,user-guides,development,deployment,modules,security,assets}
   
   # 创建子目录
   mkdir -p docs/getting-started/{installation,quick-start,concepts}
   mkdir -p docs/user-guides/{features,tutorials,reference}
   mkdir -p docs/development/{architecture,api,testing,contributing}
   mkdir -p docs/deployment/{docker,kubernetes,performance}
   mkdir -p docs/modules/{llm,rag,prompt}
   mkdir -p docs/security/compliance
   mkdir -p docs/assets/{images,examples}
   ```

### 1.2 文件重命名阶段
1. **重命名文件**
   ```bash
   # 使用git mv命令重命名文件
   git mv docs/project_knowledge.md docs/project-knowledge.md
   git mv docs/rename_guide.md docs/rename-guide.md
   git mv docs/project_learning_guide.md docs/learning-guide.md
   git mv docs/local_debug_guide.md docs/debug-guide.md
   git mv docs/test_coverage.md docs/test-coverage.md
   git mv docs/PERFORMANCE_RULES.md docs/performance-rules.md
   git mv docs/README_CN.md docs/readme-cn.md
   git mv docs/development_guidelines.md docs/development-guidelines.md
   git mv docs/CODE_OF_CONDUCT.md docs/code-of-conduct.md
   git mv docs/CONTRIBUTING.md docs/contributing.md
   git mv docs/SECURITY.md docs/security.md
   git mv docs/law_book_list.txt docs/law-book-list.txt
   ```

2. **重命名目录**
   ```bash
   # 使用git mv命令重命名目录
   git mv docs/finetune docs/finetuning
   git mv docs/words docs/word-lists
   git mv docs/dockerfile docs/docker-files
   git mv docs/rename docs/rename-guides
   git mv docs/user_guide docs/user-guides
   git mv docs/typical_implementation docs/implementation-examples
   git mv docs/tutorial docs/tutorials
   git mv docs/readme docs/readmes
   git mv docs/evaluation_report docs/evaluation-reports
   ```

### 1.3 文件迁移阶段
1. **迁移入门指南文档**
   ```bash
   # 移动入门相关文档
   mv docs/learning-guide.md docs/getting-started/
   mv docs/debug-guide.md docs/getting-started/
   mv docs/readme-cn.md docs/getting-started/
   ```

2. **迁移开发文档**
   ```bash
   # 移动开发相关文档
   mv docs/development docs/development/guide.md
   mv docs/development-guidelines.md docs/development/
   mv docs/test-coverage.md docs/development/testing/
   mv docs/testing docs/development/testing/guide.md
   ```

3. **迁移部署文档**
   ```bash
   # 移动部署相关文档
   mv docs/deployment docs/deployment/guide.md
   mv docs/performance-rules.md docs/deployment/performance/
   mv docs/docker-files/* docs/deployment/docker/
   ```

## 2. 更新引用

### 2.1 更新文档内部链接
1. **创建链接更新脚本**
   ```python
   # update_links.py
   import os
   import re
   
   def update_links(file_path):
       with open(file_path, 'r', encoding='utf-8') as f:
           content = f.read()
       
       # 更新文件链接
       content = re.sub(r'\[(.*?)\]\((.*?)\)', update_link, content)
       
       with open(file_path, 'w', encoding='utf-8') as f:
           f.write(content)
   
   def update_link(match):
       text, link = match.groups()
       # 更新链接规则
       new_link = link.replace('_', '-').lower()
       return f'[{text}]({new_link})'
   ```

2. **执行链接更新**
   ```bash
   # 更新所有markdown文件中的链接
   find docs -name "*.md" -exec python update_links.py {} \;
   ```

### 2.2 更新导航菜单
1. **更新README.md**
   ```markdown
   # 更新目录结构
   - [Getting Started](getting-started/)
   - [User Guides](user-guides/)
   - [Development](development/)
   - [Deployment](deployment/)
   - [Modules](modules/)
   - [Security](security/)
   ```

2. **更新各模块索引**
   ```markdown
   # 在每个主要目录下创建index.md
   touch docs/getting-started/index.md
   touch docs/user-guides/index.md
   touch docs/development/index.md
   touch docs/deployment/index.md
   touch docs/modules/index.md
   touch docs/security/index.md
   ```

## 3. 验证检查

### 3.1 链接验证
1. **创建链接检查脚本**
   ```python
   # check_links.py
   import os
   import re
   from pathlib import Path
   
   def check_links(file_path):
       with open(file_path, 'r', encoding='utf-8') as f:
           content = f.read()
       
       # 提取所有链接
       links = re.findall(r'\[(.*?)\]\((.*?)\)', content)
       
       # 验证链接
       for text, link in links:
           if not os.path.exists(link):
               print(f"Broken link in {file_path}: {link}")
   ```

2. **执行链接检查**
   ```bash
   # 检查所有markdown文件中的链接
   find docs -name "*.md" -exec python check_links.py {} \;
   ```

### 3.2 内容验证
1. **检查文件完整性**
   ```bash
   # 检查所有必要的文件是否存在
   find docs -type f -name "*.md" | sort
   ```

2. **验证目录结构**
   ```bash
   # 检查目录结构是否符合规范
   tree docs
   ```

## 4. 文档更新

### 4.1 更新文档内容
1. **更新文档标题**
   ```python
   # update_titles.py
   def update_title(file_path):
       with open(file_path, 'r', encoding='utf-8') as f:
           content = f.read()
       
       # 更新标题格式
       content = re.sub(r'^# (.*?)$', lambda m: f'# {m.group(1).title()}', content)
       
       with open(file_path, 'w', encoding='utf-8') as f:
           f.write(content)
   ```

2. **更新文档格式**
   ```python
   # update_format.py
   def update_format(file_path):
       with open(file_path, 'r', encoding='utf-8') as f:
           content = f.read()
       
       # 更新格式
       content = re.sub(r'```(.*?)```', update_code_block, content)
       
       with open(file_path, 'w', encoding='utf-8') as f:
           f.write(content)
   ```

### 4.2 更新索引文件
1. **创建模块索引**
   ```markdown
   # docs/modules/index.md
   # Modules Documentation
   
   ## LLM Module
   - [Overview](llm/overview.md)
   - [Configuration](llm/configuration.md)
   - [Optimization](llm/optimization.md)
   
   ## RAG Module
   - [Overview](rag/overview.md)
   - [Configuration](rag/configuration.md)
   - [Optimization](rag/optimization.md)
   ```

2. **更新主索引**
   ```markdown
   # docs/README.md
   # BugAgaric Documentation
   
   ## Getting Started
   - [Installation Guide](getting-started/installation/)
   - [Quick Start](getting-started/quick-start/)
   - [Basic Concepts](getting-started/concepts/)
   
   ## User Guides
   - [Features](user-guides/features/)
   - [Tutorials](user-guides/tutorials/)
   - [Reference](user-guides/reference/)
   ```

## 5. 提交更改

### 5.1 创建提交
```bash
# 添加所有更改
git add docs/

# 创建提交
git commit -m "docs: restructure documentation according to new naming conventions

- Rename files and directories according to naming conventions
- Update internal links and references
- Create new directory structure
- Update documentation format and style"
```

### 5.2 验证提交
```bash
# 检查更改
git diff --cached

# 确保没有遗漏的文件
git status
```

## 6. 后续维护

### 6.1 定期检查
1. **检查命名规范**
   ```bash
   # 检查文件命名
   find docs -type f -not -path "*/\.*" -exec basename {} \; | grep -v "^[a-z0-9-]*\.[a-z0-9]*$"
   ```

2. **检查目录结构**
   ```bash
   # 检查目录命名
   find docs -type d -not -path "*/\.*" -exec basename {} \; | grep -v "^[a-z0-9-]*$"
   ```

### 6.2 更新流程
1. **新文档添加流程**
   - 检查命名是否符合规范
   - 确保放在正确的目录
   - 更新相关索引文件

2. **文档修改流程**
   - 保持命名规范
   - 更新相关引用
   - 验证链接有效性 