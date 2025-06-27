# BugAgaric 项目重命名指南

## 目录
- [1. 项目概述](#1-项目概述)
- [2. 重命名范围](#2-重命名范围)
- [3. 执行计划](#3-执行计划)
- [4. 具体修改](#4-具体修改)
- [5. 验证方案](#5-验证方案)
- [6. 回滚计划](#6-回滚计划)
- [7. 后续工作](#7-后续工作)

## 1. 项目概述

### 1.1 重命名说明
- **当前项目名**: BugAgaric
- **目标项目名**: BugAgaric
- **变更原因**: 项目定位调整，更好地反映项目特性

### 1.2 影响范围
- 代码库
- 文档系统
- 配置系统
- 部署环境
- 第三方集成

## 2. 重命名范围

### 2.1 代码文件
| 文件类型 | 修改内容 | 示例 |
|---------|---------|------|
| Python文件 | 包名、导入路径、类名 | `bugagaric` → `bugagaric` |
| Go文件 | 模块路径、导入路径 | `github.com/bugagaric` → `github.com/bugagaric` |
| 配置文件 | 项目名称、路径引用 | `APP_NAME=BugAgaric` → `APP_NAME=BugAgaric` |

### 2.2 文档文件
| 文档类型 | 修改内容 | 示例 |
|---------|---------|------|
| README.md | 项目名称、描述 | 更新项目标题和描述 |
| 技术文档 | 项目引用、示例代码 | 更新所有文档中的项目名称 |
| API文档 | 接口说明、示例 | 更新API文档中的项目名称 |

### 2.3 配置系统
| 配置类型 | 修改内容 | 示例 |
|---------|---------|------|
| 环境变量 | 项目名称、路径 | 更新所有环境变量 |
| 日志配置 | 日志路径、格式 | 更新日志配置 |
| 数据库配置 | 数据库名称 | 更新数据库配置 |

## 3. 执行计划

### 3.1 准备阶段（1天）
1. 创建项目备份
   ```bash
   # 创建备份
   tar -czf bugagaric_backup_$(date +%Y%m%d).tar.gz .
   ```

2. 创建新分支
   ```bash
   git checkout -b rename-to-bugagaric
   ```

3. 准备测试环境
   - 克隆项目到测试环境
   - 配置测试数据库
   - 准备测试数据

### 3.2 执行阶段（3-4天）

#### 3.2.1 代码修改
1. 执行全局替换
   ```powershell
   # PowerShell 命令
   Get-ChildItem -Recurse -File | ForEach-Object {
     (Get-Content $_.FullName) -replace 'BugAgaric', 'BugAgaric' | Set-Content $_.FullName
     (Get-Content $_.FullName) -replace 'bugagaric', 'bugagaric' | Set-Content $_.FullName
   }
   ```

2. 重命名目录
   ```bash
   # 重命名主目录
   mv bugagaric bugagaric
   ```

#### 3.2.2 数据库迁移
```sql
-- 重命名数据库
ALTER DATABASE bugagaric RENAME TO bugagaric;

-- 更新表名中的项目名称
ALTER TABLE bugagaric_config RENAME TO bugagaric_config;
```

### 3.3 测试阶段（2-3天）
1. 单元测试
   ```bash
   pytest tests/
   ```

2. 集成测试
   ```bash
   python -m pytest tests/integration/
   ```

3. 部署测试
   ```bash
   # 测试部署
   docker-compose up --build
   ```

## 4. 具体修改

### 4.1 代码修改示例

#### Python文件
```python
# 修改前
from bugagaric.core import UltraRAGCore

class UltraRAGError(Exception):
    pass

# 修改后
from bugagaric.core import BugAgaricCore

class BugAgaricError(Exception):
    pass
```

#### 配置文件
```yaml
# 修改前
app:
  name: BugAgaric
  version: 1.0.0

# 修改后
app:
  name: BugAgaric
  version: 1.0.0
```

### 4.2 文档修改示例

#### README.md
```markdown
# 修改前
# BugAgaric
BugAgaric is a powerful document management system.

# 修改后
# BugAgaric
BugAgaric is a powerful document management system.
```

## 5. 验证方案

### 5.1 代码验证
- [ ] 所有导入语句正确
- [ ] 类名和函数名已更新
- [ ] 配置文件正确
- [ ] 测试用例通过

### 5.2 文档验证
- [ ] 所有文档链接有效
- [ ] 示例代码可运行
- [ ] 格式正确

### 5.3 部署验证
- [ ] 应用正常启动
- [ ] 数据库连接正常
- [ ] 所有功能正常

## 6. 回滚计划

### 6.1 回滚触发条件
- 发现严重bug
- 部署失败
- 数据异常

### 6.2 回滚步骤
1. 停止服务
   ```bash
   docker-compose down
   ```

2. 恢复数据库
   ```sql
   -- 恢复数据库名称
   ALTER DATABASE bugagaric RENAME TO bugagaric;
   ```

3. 恢复代码
   ```bash
   git checkout main
   git reset --hard HEAD^
   ```

4. 重启服务
   ```bash
   docker-compose up -d
   ```

## 7. 后续工作

### 7.1 文档更新
- 更新API文档
- 更新用户指南
- 更新开发文档

### 7.2 通知相关方
- 通知开发团队
- 通知用户
- 发布变更公告

### 7.3 监控和反馈
- 监控系统运行状态
- 收集用户反馈
- 处理相关问题

## 8. 当前状态说明

### 8.1 项目现状
- **项目名称**: BugAgaric
- **目录结构**: 保持原有结构
- **代码状态**: 正常运行
- **文档状态**: 需要更新重命名相关文档

### 8.2 重命名状态
- **计划状态**: 待执行
- **目标名称**: BugAgaric
- **执行时间**: 待安排
- **风险评估**: 需要详细评估

### 8.3 建议
1. **准备重命名**: 当前项目运行稳定，可以开始准备重命名
2. **完善文档**: 更新现有文档，确保准确性
3. **评估影响**: 充分评估重命名对项目的影响
4. **制定计划**: 制定详细的重命名计划 