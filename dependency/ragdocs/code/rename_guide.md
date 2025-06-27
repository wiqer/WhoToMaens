# BugAgaric 项目重命名指南

## 📋 概述

本文档提供了 BugAgaric 项目重命名的详细指南，包括文件处理策略、重命名步骤、回滚计划和注意事项。

**当前状态**: 项目仍使用 BugAgaric 名称，重命名计划待执行

## 1. 文件处理策略

### 1.1 需要备份的文件
- 源代码文件（`bugagaric/` 目录）
- 配置文件（`config/` 目录）
- 文档文件（`docs/` 目录）
- 资源文件（`resources/` 目录）
- 测试文件（`tests/` 目录）

### 1.2 不需要备份的文件
- Python虚拟环境（`.venv/` 目录）
- 构建产物（`build/`、`dist/` 目录）
- 缓存文件（`__pycache__/`、`.pytest_cache/`）
- 日志文件（`logs/` 目录）
- 临时文件（`.tmp`、`.temp` 文件）
- 数据库文件（`*.sqlite3`、`*.db`）
- 下载的数据集和模型文件

### 1.3 备份命令
```powershell
# 创建备份目录
mkdir backup_$(Get-Date -Format "yyyyMMdd")

# 复制需要备份的文件（排除不需要的文件）
robocopy . backup_$(Get-Date -Format "yyyyMMdd") /E /XD .venv build dist logs __pycache__ .pytest_cache /XF *.sqlite3 *.db *.tmp *.temp
```

## 2. 重命名步骤

### 2.1 准备工作
1. 确保所有更改已提交到版本控制
2. 创建新的开发分支
```bash
git checkout -b rename-to-bugagaric
```

### 2.2 执行重命名
1. 重命名主目录
```bash
mv bugagaric bugagaric
```

2. 更新配置文件中的项目名称
```powershell
# 更新配置文件中的项目名称
Get-ChildItem -Recurse -Include *.py,*.yaml,*.yml,*.json,*.md | ForEach-Object {
    (Get-Content $_.FullName) -replace 'BugAgaric', 'BugAgaric' | Set-Content $_.FullName
    (Get-Content $_.FullName) -replace 'bugagaric', 'bugagaric' | Set-Content $_.FullName
}
```

3. 更新文档中的项目名称
```powershell
# 更新文档中的项目名称
Get-ChildItem -Recurse -Include *.md | ForEach-Object {
    (Get-Content $_.FullName) -replace 'BugAgaric', 'BugAgaric' | Set-Content $_.FullName
    (Get-Content $_.FullName) -replace 'bugagaric', 'bugagaric' | Set-Content $_.FullName
}
```

### 2.3 验证更改
1. 检查文件重命名
```powershell
# 检查是否还有遗漏的旧项目名称
Get-ChildItem -Recurse -File | Select-String -Pattern "BugAgaric|bugagaric"
```

2. 运行测试
```bash
# 运行单元测试
pytest tests/

# 运行集成测试
pytest tests/integration/
```

## 3. 回滚计划

### 3.1 回滚触发条件
- 发现严重bug
- 部署失败
- 数据异常

### 3.2 回滚步骤
1. 恢复代码
```bash
git checkout main
git reset --hard HEAD^
```

2. 恢复目录结构
```bash
mv bugagaric bugagaric
```

3. 恢复配置文件
```powershell
# 恢复配置文件中的项目名称
Get-ChildItem -Recurse -Include *.py,*.yaml,*.yml,*.json,*.md | ForEach-Object {
    (Get-Content $_.FullName) -replace 'BugAgaric', 'BugAgaric' | Set-Content $_.FullName
    (Get-Content $_.FullName) -replace 'bugagaric', 'bugagaric' | Set-Content $_.FullName
}
```

## 4. 注意事项

### 4.1 文件处理
- 不要备份虚拟环境，可以重新创建
- 不要备份构建产物，可以重新生成
- 不要备份缓存文件，可以重新生成
- 不要备份日志文件，可以重新生成
- 不要备份数据库文件，需要单独处理

### 4.2 数据库处理
- 在重命名之前备份数据库
- 在重命名之后更新数据库名称
- 准备数据库回滚脚本

### 4.3 环境处理
- 在重命名之后重新创建虚拟环境
- 重新安装项目依赖
- 更新环境变量

## 5. 后续工作

### 5.1 文档更新
- 更新API文档
- 更新用户指南
- 更新开发文档

### 5.2 通知相关方
- 通知开发团队
- 通知用户
- 发布变更公告

### 5.3 监控和反馈
- 监控系统运行状态
- 收集用户反馈
- 处理相关问题

## 6. 当前状态说明

### 6.1 项目现状
- **项目名称**: BugAgaric
- **代码状态**: 正常运行
- **文档状态**: 需要更新重命名相关文档
- **重命名状态**: 计划中，待执行

### 6.2 重命名状态
- **计划状态**: 待执行
- **目标名称**: BugAgaric
- **执行时间**: 待安排
- **风险评估**: 需要详细评估

### 6.3 建议
1. **准备重命名**: 当前项目运行稳定，可以开始准备重命名
2. **完善文档**: 更新现有文档，确保准确性
3. **评估影响**: 充分评估重命名对项目的影响
4. **制定计划**: 制定详细的重命名计划

### 6.4 优先级
- **高优先级**: 更新现有文档，确保准确性
- **中优先级**: 评估重命名影响
- **低优先级**: 执行重命名计划

## 7. 执行记录

### 7.1 文档更新记录
```powershell
# 文档更新操作
# 执行时间：2024年1月
# 执行结果：成功更新重命名相关文档
# 主要变更：
# - 将通用占位符改为具体的 "BugAgaric"
# - 添加当前状态说明
# - 更新建议和优先级
```

**执行时间**: 2024年1月
**执行结果**: 成功更新重命名相关文档
**注意事项**:
- 当前项目仍使用 BugAgaric 名称
- 重命名计划待执行，目标名称为 BugAgaric
- 建议准备重命名，优先完善文档 