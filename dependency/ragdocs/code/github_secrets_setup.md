# GitHub Secrets 配置指南

## 概述

本文档指导您如何在 GitHub 仓库中配置 Secrets，以启用 CI/CD 自动化通知功能。

## 配置步骤

### 1. 访问 GitHub 仓库设置

1. 打开浏览器，访问您的 GitHub 仓库：https://github.com/wiqer/BugAgaric
2. 点击仓库页面顶部的 **Settings** 标签
3. 在左侧菜单中找到 **Secrets and variables** → **Actions**

### 2. 配置邮件通知 Secrets

#### 2.1 获取 Gmail 应用密码

如果您使用 Gmail，需要创建应用密码：

1. 访问 [Google 账户设置](https://myaccount.google.com/)
2. 点击 **安全性** → **2 步验证**
3. 在 **应用专用密码** 部分，点击 **生成新的应用专用密码**
4. 选择应用类型为 **邮件**，设备类型为 **其他**
5. 复制生成的 16 位密码

#### 2.2 添加邮件 Secrets

在 GitHub Secrets 页面点击 **New repository secret**，添加以下密钥：

| Secret 名称 | 值 | 说明 |
|------------|----|----|
| `EMAIL_USERNAME` | `your-email@gmail.com` | 您的 Gmail 邮箱地址 |
| `EMAIL_PASSWORD` | `your-16-digit-app-password` | Gmail 应用专用密码 |
| `NOTIFICATION_EMAIL` | `team@company.com` | 接收通知的邮箱地址 |

### 3. 配置 Slack 通知

#### 3.1 创建 Slack Webhook

1. 访问 [Slack API 网站](https://api.slack.com/)
2. 登录您的 Slack 工作区
3. 点击 **Create New App** → **From scratch**
4. 输入应用名称（如：BugAgaric CI/CD）
5. 选择工作区
6. 在左侧菜单找到 **Incoming Webhooks**
7. 点击 **Activate Incoming Webhooks**
8. 点击 **Add New Webhook to Workspace**
9. 选择要发送通知的频道（如：#ci-cd）
10. 复制生成的 Webhook URL

#### 3.2 添加 Slack Secret

在 GitHub Secrets 页面添加：

| Secret 名称 | 值 | 说明 |
|------------|----|----|
| `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/services/YOUR/WEBHOOK/URL` | Slack Webhook URL |

### 4. 验证配置

配置完成后，您可以通过以下方式验证：

1. 推送代码到仓库触发 CI/CD 流程
2. 查看 GitHub Actions 页面
3. 检查是否收到邮件和 Slack 通知

## 其他可选配置

### GitHub Token（用于构建产物管理）

如果您需要使用构建产物管理功能，可以添加：

| Secret 名称 | 值 | 说明 |
|------------|----|----|
| `GITHUB_TOKEN` | `ghp_xxxxxxxxxxxxxxxxxxxx` | GitHub Personal Access Token |

**获取方法：**
1. 访问 [GitHub Settings](https://github.com/settings/tokens)
2. 点击 **Generate new token** → **Generate new token (classic)**
3. 选择权限：`repo`, `workflow`, `actions:read`
4. 复制生成的 token

## 安全注意事项

1. **不要**在代码中硬编码这些密钥
2. **不要**在日志中输出这些密钥
3. 定期轮换密钥
4. 使用最小权限原则
5. 监控密钥使用情况

## 故障排除

### 邮件发送失败

1. 检查 Gmail 应用密码是否正确
2. 确认 2 步验证已启用
3. 检查邮箱地址格式
4. 查看 GitHub Actions 日志

### Slack 通知失败

1. 检查 Webhook URL 是否正确
2. 确认 Slack 应用已安装到工作区
3. 检查频道权限
4. 查看 GitHub Actions 日志

### 权限问题

1. 确认 GitHub Token 有足够权限
2. 检查仓库设置中的 Actions 权限
3. 确认工作流文件路径正确

## 测试配置

您可以使用以下命令测试配置：

```bash
# 运行快速启动脚本测试功能
bash scripts/ci_quick_start.sh test

# 手动触发工作流测试通知
# 在 GitHub Actions 页面手动运行 notifications 工作流
```

## 联系支持

如果遇到配置问题，请：

1. 查看 GitHub Actions 日志
2. 检查 Secrets 配置
3. 参考本文档故障排除部分
4. 提交 GitHub Issue 寻求帮助 