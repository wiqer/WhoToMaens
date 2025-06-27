# BugAgaric 依赖资源转移指南

## 概述

本指南帮助您将BugAgaric项目的Python虚拟环境和npm包转移到其他盘符，以减轻C盘压力。

## 当前依赖资源分析

根据分析，项目中的主要依赖资源包括：

- **venv**: 约2.4GB (Python虚拟环境)
- **.venv**: 约5.0GB (备用Python虚拟环境)  
- **node_modules**: 约90MB (npm包)

总计约7.5GB的依赖资源占用C盘空间。

## 转移方案

### 目标磁盘分配

- **D盘**: Python虚拟环境 (venv, .venv) + pip缓存
- **E盘**: npm包 (node_modules) + npm缓存
- **H盘**: 备用存储空间

### 转移策略

1. **符号链接**: 使用符号链接保持项目结构不变
2. **自动备份**: 转移前自动创建备份
3. **全局配置**: 设置pip和npm的全局缓存目录
4. **空间检查**: 自动检查目标磁盘可用空间

## 使用方法

### 方法一：使用批处理文件（推荐）

```bash
# 以管理员身份运行
scripts/transfer_dependencies.bat

# 自定义目标磁盘
scripts/transfer_dependencies.bat --venv-disk D --npm-disk E

# 仅显示将要执行的操作（不实际执行）
scripts/transfer_dependencies.bat --dry-run

# 仅设置全局配置
scripts/transfer_dependencies.bat --config-only
```

### 方法二：使用PowerShell脚本

```powershell
# 以管理员身份运行PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 执行转移
.\scripts\transfer_dependencies.ps1

# 自定义参数
.\scripts\transfer_dependencies.ps1 -VenvDisk D -NpmDisk E -DryRun
```

### 方法三：使用Python脚本

```bash
# 执行转移
python scripts/transfer_dependencies.py

# 自定义参数
python scripts/transfer_dependencies.py --venv-disk D --npm-disk E

# 仅设置全局配置
python scripts/transfer_dependencies.py --config-only
```

## 转移过程

### 1. 预检查
- 检查管理员权限
- 分析当前依赖资源大小
- 检查目标磁盘可用空间
- 验证目标路径

### 2. 备份
- 自动创建转移前的备份
- 备份保留7天

### 3. 转移操作
- 复制文件到目标位置
- 删除原始文件
- 创建符号链接

### 4. 全局配置
- 设置pip缓存目录到D盘
- 设置npm缓存目录到E盘

## 转移后的使用

### Python虚拟环境

```bash
# 激活虚拟环境（路径保持不变）
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 安装新包
pip install package_name

# 查看pip缓存位置
pip cache dir
```

### Node.js包

```bash
# 安装依赖（路径保持不变）
npm install

# 查看npm缓存位置
npm config get cache
```

### 项目开发

```bash
# 启动开发服务器
npm run dev

# 运行Python脚本
python main.py

# 启动Streamlit应用
streamlit run bugagaric/webui/webui.py
```

## 配置文件

转移完成后，会生成配置文件 `config/dependency_paths.yaml`，包含：

- 转移后的路径映射
- 磁盘使用情况
- 使用说明
- 恢复指南

## 恢复操作

### 恢复到原始位置

```bash
# 删除符号链接
rmdir venv
rmdir .venv
rmdir node_modules

# 移动文件回原位置
move D:\BugAgaric\venv .\venv
move D:\BugAgaric\.venv .\.venv
move E:\BugAgaric\node_modules .\node_modules
```

### 从备份恢复

```bash
# 查看备份目录
dir D:\BugAgaric\backup

# 恢复备份
copy D:\BugAgaric\backup\venv .\venv
copy D:\BugAgaric\backup\.venv .\.venv
copy D:\BugAgaric\backup\node_modules .\node_modules
```

## 注意事项

### 权限要求
- 需要管理员权限创建符号链接
- 确保对目标磁盘有写入权限

### 磁盘空间
- 确保目标磁盘有足够空间
- 建议预留1GB额外空间

### 符号链接
- Windows需要启用开发者模式或管理员权限
- 符号链接保持项目结构不变

### 备份管理
- 备份文件保留7天
- 可以手动清理过期备份

## 故障排除

### 常见问题

1. **权限不足**
   ```
   错误: 需要管理员权限
   解决: 以管理员身份运行脚本
   ```

2. **磁盘空间不足**
   ```
   错误: 目标磁盘空间不足
   解决: 选择其他磁盘或清理空间
   ```

3. **符号链接失败**
   ```
   错误: 无法创建符号链接
   解决: 启用Windows开发者模式
   ```

4. **文件被占用**
   ```
   错误: 文件正在使用中
   解决: 关闭相关程序后重试
   ```

### 日志文件

脚本执行时会生成详细日志，包含：
- 转移进度
- 错误信息
- 磁盘使用情况
- 配置信息

## 性能优化建议

### 转移前
- 关闭所有使用虚拟环境的程序
- 清理不必要的文件
- 确保磁盘有足够空间

### 转移后
- 定期清理缓存目录
- 监控磁盘使用情况
- 及时更新依赖

## 联系支持

如果遇到问题，请：
1. 查看日志文件
2. 检查配置文件
3. 参考故障排除指南
4. 提交Issue到项目仓库 