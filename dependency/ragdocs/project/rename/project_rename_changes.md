# BugAgaric 项目重命名完整方案 (BugAgaric → BugAgaric)

## 一、项目概述
本文档整合了项目重命名的详细修改内容、执行计划和验证清单，提供从代码到文档的全流程迁移指南，确保项目平稳过渡到新名称。

**当前状态**: 项目仍使用 BugAgaric 名称，重命名计划待执行

## 二、核心修改内容

### 2.1 代码文件修改

#### Python 文件
- **bugagaric/__init__.py**: 更新模块文档字符串
  ```python
  # 当前状态
  """BugAgaric: A powerful document management and search system."""
  # 重命名后
  """BugAgaric: A powerful document management and search system."""
  ```
- **bugagaric/modules/database/db_config.py**: 更新数据库配置
  ```python
  # 当前状态
  self.DB_NAME = os.getenv('DB_NAME', 'bugagaric')
  # 重命名后
  self.DB_NAME = os.getenv('DB_NAME', 'bugagaric')
  ```
- **bugagaric/webui/utils/exceptions.py**: 重命名异常类
  ```python
  # 当前状态
  class UltraRAGError(Exception):
  # 重命名后
  class BugAgaricError(Exception):
  ```
- **bugagaric/finetune/embedding/setup.py**: 更新包名称
- **所有包含 `from bugagaric.` 导入的文件**: 统一替换为 `from bugagaric.`

#### Go 文件
- **go-services/api/go.mod**: 更新模块路径
  ```go
  // 当前状态
  module github.com/bugagaric/api
  // 重命名后
  module github.com/bugagaric/api
  ```
- **所有 Go 源文件**: 更新导入路径

### 2.2 文档体系更新

#### 核心文档
- **README.md**: 更新项目标题、描述和徽章
- **LICENSE**: 更新版权声明中的项目名称
- **docs/project_learning_guide.md**: 全局替换项目名称引用

#### 技术文档
- **docs/architecture/overview.md**: 更新架构图和所有项目名称引用
- **docs/deployment/installation.md**: 修改安装命令
  ```bash
  # 当前状态
  git clone https://github.com/your-org/bugagaric.git
  cd bugagaric
  # 重命名后
  git clone https://github.com/your-org/bugagaric.git
  cd bugagaric
  ```
- **docs/development/guidelines.md**: 更新开发规范中的项目名称

### 2.3 配置与界面

#### 配置文件
- **bugagaric/webui/utils/config.py**: 更新 pipeline 名称
  ```python
  # 当前状态
  {"name": "BugAgaric-Embedding", ...}
  # 重命名后
  {"name": "BugAgaric-Embedding", ...}
  ```
- **config/local_debug/logging_config.yaml**: 更新日志路径

#### 界面显示
- **bugagaric/webui/webui.py**: 修改页面标题
  ```python
  # 当前状态
  page_title="BugAgaric",
  # 重命名后
  page_title="BugAgaric",
  ```
- **bugagaric/webui/utils/translations/en.json** 和 **zh.json**: 更新翻译内容

### 2.4 脚本与工作流
- **bugagaric/finetune/dpo_and_sft/train.sh**: 更新脚本路径
- **bugagaric/datasets/DDR/workflow.sh**: 修改工作流命令
- **所有 shell 脚本**: 更新 Python 命令中的模块路径

### 2.5 目录结构
1. 将根目录从 `BugAgaric-BUG` 重命名为 `BugAgaric`
2. 将 `bugagaric` 目录重命名为 `bugagaric`
3. 更新所有依赖此目录的引用路径

## 三、执行计划

### 3.1 准备阶段（1天）
1. 创建项目备份
2. 确保所有更改已提交到版本控制
3. 创建专用分支 `rename-to-bugagaric`

### 3.2 执行阶段（3-4天）
1. 使用批量替换工具执行全局替换
   ```bash
   # PowerShell 命令示例
   Get-ChildItem -Recurse -File | ForEach-Object {
     (Get-Content $_.FullName) -replace 'BugAgaric', 'BugAgaric' | Set-Content $_.FullName
     (Get-Content $_.FullName) -replace 'bugagaric', 'bugagaric' | Set-Content $_.FullName
   }
   ```
2. 重命名目录结构
3. 手动检查并修复复杂文件
4. 更新文档内容

### 3.3 测试验证（2-3天）
1. 运行单元测试和集成测试
2. 验证所有工作流和脚本
3. 检查文档链接和格式
4. 测试部署流程

### 3.4 部署阶段（1天）
1. 合并更改到主分支
2. 更新生产环境配置
3. 执行数据库迁移
4. 更新监控系统

## 四、验证清单

### 4.1 代码验证
- [ ] 所有 Python 导入路径正确
- [ ] 异常类名称已更新
- [ ] 数据库配置正确
- [ ] Go 模块路径已更新
- [ ] 单元测试通过

### 4.2 文档验证
- [ ] README.md 内容准确
- [ ] 安装文档命令正确
- [ ] 架构文档引用更新
- [ ] 所有文档链接有效

### 4.3 部署验证
- [ ] 应用启动正常
- [ ] Web UI 显示正确名称
- [ ] 所有工作流正常运行
- [ ] 数据库连接正常

## 五、风险与应对
- **导入错误**: 重命名目录后可能出现导入错误，需全面测试并修复
- **数据迁移**: 数据库名称变更需谨慎处理，建议先备份再迁移
- **第三方依赖**: 检查并更新所有外部服务引用
- **回滚计划**: 保留旧版本备份，准备快速回滚方案

## 六、后续工作
1. 更新 API 文档和用户手册
2. 通知相关团队和用户
3. 更新项目主页和社交媒体信息
4. 发布变更公告

## 七、当前状态总结

### 7.1 项目现状
- **项目名称**: BugAgaric
- **代码状态**: 正常运行
- **文档状态**: 需要更新重命名相关文档
- **重命名状态**: 计划中，待执行

### 7.2 建议
1. **准备重命名**: 当前项目运行稳定，可以开始准备重命名
2. **完善文档**: 更新现有文档，确保准确性
3. **评估影响**: 充分评估重命名对项目的影响
4. **制定计划**: 制定详细的重命名计划

### 7.3 优先级
- **高优先级**: 更新现有文档，确保准确性
- **中优先级**: 评估重命名影响
- **低优先级**: 执行重命名计划