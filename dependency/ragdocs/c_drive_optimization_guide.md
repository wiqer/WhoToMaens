# C盘压力减轻完整指南

## 概述

除了转移依赖资源，还有很多其他方式可以减轻C盘压力。本指南提供全面的C盘优化解决方案。

## 主要优化方法

### 1. 系统文件清理

#### Windows临时文件
```bash
# 清理Windows临时文件
python scripts/c_drive_optimization.py --clean-temp

# 手动清理路径
C:\Windows\Temp
C:\Windows\Prefetch
%TEMP%
%TMP%
```

#### Windows更新文件
```bash
# 清理Windows更新缓存
python scripts/c_drive_optimization.py --clean-windows

# 手动命令
dism /online /cleanup-image /startcomponentcleanup
cleanmgr /sagerun:1
```

#### 回收站
```bash
# 清空回收站
python scripts/c_drive_optimization.py --clean-recycle

# PowerShell命令
Clear-RecycleBin -Force
```

### 2. 用户文件优化

#### 移动用户文件夹
```bash
# 分析用户文件夹大小
python scripts/c_drive_optimization.py --move-folders
```

**手动移动方法：**
1. 右键点击文件夹 → 属性 → 位置
2. 选择新位置（如 `D:\Users\用户名\Documents`）
3. 点击"移动"按钮

**可移动的文件夹：**
- Documents（文档）
- Downloads（下载）
- Pictures（图片）
- Videos（视频）
- Music（音乐）
- Desktop（桌面）

#### 下载文件夹清理
```bash
# 分析下载文件夹
python scripts/c_drive_optimization.py --analyze
```

**清理建议：**
- 删除已安装的安装包
- 清理重复文件
- 移除临时下载文件
- 整理过期的文档

### 3. 浏览器缓存清理

```bash
# 清理浏览器缓存
python scripts/c_drive_optimization.py --clean-browser
```

**缓存位置：**
- Chrome: `%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cache`
- Edge: `%LOCALAPPDATA%\Microsoft\Edge\User Data\Default\Cache`
- Firefox: `%LOCALAPPDATA%\Mozilla\Firefox\Profiles`

### 4. 应用程序优化

#### Docker优化
```bash
# 分析Docker存储
python scripts/c_drive_optimization.py --optimize-docker

# Docker清理命令
docker image prune -a          # 清理未使用的镜像
docker container prune         # 清理未使用的容器
docker volume prune           # 清理未使用的卷
docker builder prune          # 清理构建缓存
```

#### Git仓库优化
```bash
# 分析Git仓库
python scripts/c_drive_optimization.py --optimize-git

# Git优化命令
git gc --aggressive           # 清理历史记录
git filter-branch            # 删除大文件历史
git clone --depth 1          # 浅克隆
```

### 5. 大文件分析

```bash
# 分析C盘大文件
python scripts/c_drive_optimization.py --analyze-large
```

**常见大文件类型：**
- 视频文件 (.mp4, .avi, .mkv)
- 游戏文件 (.iso, .zip)
- 虚拟机文件 (.vmdk, .vdi)
- 数据库文件 (.mdf, .ldf)
- 日志文件 (.log)

### 6. 系统设置优化

#### 禁用休眠文件
```bash
# 以管理员身份运行
powercfg -h off
```

**效果：** 释放与内存大小相等的空间

#### 压缩系统文件
```bash
# 启用系统文件压缩
compact /compactos:always
```

#### 优化虚拟内存
1. 系统属性 → 高级 → 性能设置 → 高级
2. 虚拟内存 → 更改
3. 取消"自动管理"
4. 设置自定义大小或移动到其他盘符

### 7. 存储感知功能

**启用存储感知：**
1. 设置 → 系统 → 存储
2. 开启"存储感知"
3. 配置自动清理规则

**清理规则：**
- 临时文件：1天后删除
- 回收站：30天后清空
- 下载文件夹：60天后清理

### 8. 云存储集成

#### OneDrive优化
- 启用"文件按需下载"
- 将大文件移动到云端
- 同步重要文件到本地

#### 其他云存储
- Google Drive
- Dropbox
- 百度网盘
- 阿里云盘

### 9. 符号链接优化

#### 创建符号链接
```bash
# 移动大文件夹并创建符号链接
mklink /D "C:\原路径" "D:\新路径"
```

**适用场景：**
- 游戏文件夹
- 开发工具
- 大型数据集
- 媒体文件

### 10. 磁盘清理工具

#### Windows磁盘清理
```bash
# 运行磁盘清理
cleanmgr
```

**清理项目：**
- Windows更新清理
- 临时文件
- 回收站
- 系统错误内存转储文件
- 系统日志文件

#### 第三方工具
- CCleaner
- Wise Disk Cleaner
- BleachBit
- TreeSize

## 自动化脚本

### 一键优化
```bash
# 执行所有优化操作
python scripts/c_drive_optimization.py --all
```

### 生成优化报告
```bash
# 生成详细报告
python scripts/c_drive_optimization.py --report
```

### 定期清理
```bash
# 创建定时任务
schtasks /create /tn "C盘清理" /tr "python scripts/c_drive_optimization.py --all" /sc weekly /d sun
```

## 预防措施

### 1. 定期维护
- 每周运行清理脚本
- 每月检查大文件
- 每季度深度清理

### 2. 存储监控
```bash
# 监控磁盘使用情况
python scripts/c_drive_optimization.py --analyze
```

### 3. 应用程序管理
- 定期卸载不需要的程序
- 使用便携版软件
- 将大型应用安装到其他盘符

### 4. 文件管理
- 使用云存储备份
- 定期整理文件
- 避免在C盘存储大文件

## 高级优化技巧

### 1. 系统还原点管理
```bash
# 清理系统还原点
vssadmin delete shadows /all
```

### 2. 页面文件优化
- 将页面文件移动到其他盘符
- 根据内存大小调整页面文件大小

### 3. 系统日志清理
```bash
# 清理事件日志
wevtutil el | Foreach-Object {wevtutil cl "$_"}
```

### 4. 字体文件优化
- 删除不需要的字体
- 将字体文件移动到其他盘符

### 5. 驱动程序清理
- 删除旧版本驱动程序
- 清理驱动程序缓存

## 监控和维护

### 1. 空间监控脚本
```bash
# 创建监控脚本
@echo off
python scripts/c_drive_optimization.py --analyze
if %errorlevel% neq 0 (
    echo C盘空间不足，请及时清理
    python scripts/c_drive_optimization.py --all
)
```

### 2. 告警设置
- 设置磁盘使用率告警
- 配置自动清理规则
- 定期发送清理提醒

### 3. 备份策略
- 重要文件定期备份
- 使用增量备份
- 云端备份重要数据

## 注意事项

### 1. 安全考虑
- 不要删除系统关键文件
- 备份重要数据
- 测试清理脚本效果

### 2. 性能影响
- 避免在系统繁忙时清理
- 分批处理大文件
- 监控清理过程

### 3. 兼容性
- 确保脚本兼容Windows版本
- 测试第三方工具
- 验证符号链接功能

## 总结

通过以上多种方法的组合使用，可以显著减轻C盘压力：

1. **立即效果**：清理临时文件、缓存、回收站
2. **中期效果**：移动用户文件夹、优化应用程序
3. **长期效果**：建立良好的文件管理习惯

建议根据实际情况选择合适的优化方法，并建立定期维护机制。 