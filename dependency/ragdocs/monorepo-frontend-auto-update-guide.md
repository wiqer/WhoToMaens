# BugAgaric Monorepo前端自动依赖更新指南

## 📋 概述

UltraRAG项目采用Monorepo架构，包含多个前端包。为确保所有前端依赖的安全性和最新性，我们实现了自动化的依赖更新与安全扫描系统。

## 🏗️ 系统架构

```
BugAgaric Monorepo
├── frontend/                 # 主前端应用
│   ├── package.json
│   └── package-lock.json
├── admin-portal/            # 管理后台
│   ├── package.json
│   └── package-lock.json
├── scripts/
│   └── auto_update_all_frontends.sh  # 自动化脚本
└── .github/workflows/
    └── monorepo-frontend-auto-update.yml  # CI工作流
```

## 🚀 自动化流程

### 1. 定时触发
- **频率**: 每周一凌晨2点自动运行
- **触发条件**: GitHub Actions schedule
- **手动触发**: 支持workflow_dispatch手动执行

### 2. 执行步骤
1. **检出代码**: 获取最新代码
2. **环境准备**: 配置Node.js和Git
3. **依赖升级**: 对所有前端包执行依赖升级
4. **安全扫描**: 生成安全审计报告
5. **变更检测**: 检查是否有依赖变更
6. **PR创建**: 如有变更，自动创建PR
7. **报告上传**: 上传安全报告到Artifacts

## 📦 支持的前端包

### 当前配置
- `frontend/` - 主前端应用
- `admin-portal/` - 管理后台

### 扩展配置
如需添加新的前端包，请修改以下文件：

1. **脚本配置** (`scripts/auto_update_all_frontends.sh`):
```bash
PACKAGES=("frontend" "admin-portal" "new-package")
```

2. **CI配置** (`.github/workflows/monorepo-frontend-auto-update.yml`):
```yaml
path: |
  frontend/npm_audit_report.json
  admin-portal/npm_audit_report.json
  new-package/npm_audit_report.json
```

## 🔧 本地使用

### 手动执行
```bash
# 给脚本执行权限
chmod +x scripts/auto_update_all_frontends.sh

# 执行自动化更新
bash scripts/auto_update_all_frontends.sh
```

### 执行结果
脚本会输出详细的执行过程：
```
🚀 开始Monorepo多包依赖升级与安全扫描...
✅ 发现前端包: frontend
✅ 发现前端包: admin-portal
📦 将处理 2 个前端包: frontend admin-portal

🔄 处理 frontend ...
==================================
📋 当前依赖状态:
⬆️  升级依赖到最新版本...
📥 安装最新依赖并生成锁定文件...
🔒 自动修复安全漏洞...
🛡️  生成安全扫描报告...
📊 安全报告摘要:
   发现漏洞数量: 0
✅ frontend 处理完成

🔄 处理 admin-portal ...
==================================
...
```

## 📊 安全报告

### 报告位置
每个前端包都会生成安全报告：
- `frontend/npm_audit_report.json`
- `admin-portal/npm_audit_report.json`

### 报告内容
```json
{
  "metadata": {
    "vulnerabilities": {
      "total": 0,
      "high": 0,
      "moderate": 0,
      "low": 0
    }
  },
  "vulnerabilities": {}
}
```

### 漏洞等级
- **High**: 高危漏洞，需要立即修复
- **Moderate**: 中危漏洞，建议尽快修复
- **Low**: 低危漏洞，可选择性修复

## 🤖 CI自动PR

### PR标题
```
🤖 Monorepo Frontend Dependency Update & Security Scan
```

### PR内容
自动PR包含以下信息：
- 更新的前端包列表
- 安全扫描结果摘要
- 更新内容说明
- 注意事项和验证步骤
- 自动生成的依赖更新摘要

### PR标签
- `dependencies` - 依赖相关
- `automated` - 自动生成
- `security` - 安全相关

## 🔍 验证步骤

### 1. 检查依赖状态
```bash
# 检查主前端
cd frontend
npm list --depth=0

# 检查管理后台
cd ../admin-portal
npm list --depth=0
```

### 2. 运行安全扫描
```bash
# 检查主前端安全
cd frontend
npm audit

# 检查管理后台安全
cd ../admin-portal
npm audit
```

### 3. 运行测试
```bash
# 测试主前端
cd frontend
npm test

# 测试管理后台
cd ../admin-portal
npm test
```

### 4. 功能验证
- 启动开发服务器
- 检查核心功能
- 验证UI组件
- 测试用户交互

## ⚠️ 注意事项

### 1. 依赖升级风险
- **Major版本升级**: 可能包含破坏性变更
- **Peer Dependencies**: 需要检查兼容性
- **TypeScript类型**: 可能影响类型定义

### 2. 安全漏洞处理
- **高危漏洞**: 必须立即修复，CI会阻断
- **中危漏洞**: 建议尽快修复
- **低危漏洞**: 可选择性修复

### 3. 回滚策略
如果升级后出现问题：
```bash
# 回滚到上一个版本
git checkout HEAD~1 -- frontend/package.json frontend/package-lock.json
git checkout HEAD~1 -- admin-portal/package.json admin-portal/package-lock.json

# 重新安装依赖
cd frontend && npm install
cd ../admin-portal && npm install
```

## 🛠️ 故障排除

### 常见问题

#### 1. 脚本执行失败
```bash
# 检查脚本权限
ls -la scripts/auto_update_all_frontends.sh

# 重新设置权限
chmod +x scripts/auto_update_all_frontends.sh
```

#### 2. 依赖安装失败
```bash
# 清理缓存
npm cache clean --force

# 删除node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

#### 3. 安全扫描失败
```bash
# 检查npm版本
npm --version

# 更新npm
npm install -g npm@latest

# 重新扫描
npm audit
```

### 日志查看
```bash
# 查看CI日志
# 在GitHub Actions页面查看详细日志

# 查看本地执行日志
bash scripts/auto_update_all_frontends.sh 2>&1 | tee update.log
```

## 📈 最佳实践

### 1. 定期检查
- 每周检查自动PR
- 及时处理安全漏洞
- 验证功能正常性

### 2. 团队协作
- 分配PR审查人员
- 建立测试流程
- 记录更新历史

### 3. 监控告警
- 关注CI执行状态
- 监控安全漏洞数量
- 跟踪依赖更新频率

## 🔗 相关资源

- [GitHub Actions文档](https://docs.github.com/en/actions)
- [npm audit文档](https://docs.npmjs.com/cli/v8/commands/npm-audit)
- [npm-check-updates文档](https://github.com/raineorshine/npm-check-updates)
- [项目CI配置](/.github/workflows/)

---

**最后更新**: 2024年1月
**版本**: v1.0.0
**维护者**: UltraRAG开发团队 