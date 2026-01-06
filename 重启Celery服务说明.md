# 重启 Celery 服务说明

## Windows 环境下重启 Celery 服务

### 方法1：使用任务管理器（推荐）

1. **停止 Celery 进程**：
   - 按 `Ctrl + Shift + Esc` 打开任务管理器
   - 在"进程"或"详细信息"标签页中
   - 查找名为 `celery.exe` 或包含 `celery` 的进程
   - 右键点击 → 选择"结束任务"

2. **重新启动 Celery**：
   - 双击运行 `start_celery.bat` 文件
   - 或者在命令行中执行：
     ```bash
     cd backend
     celery -A config worker -l info
     ```

### 方法2：使用命令行（PowerShell）

1. **查找 Celery 进程**：
   ```powershell
   Get-Process | Where-Object {$_.ProcessName -like "*celery*" -or $_.CommandLine -like "*celery*"}
   ```

2. **停止 Celery 进程**：
   ```powershell
   # 方法1：根据进程名停止
   Stop-Process -Name "python" -Force
   # 注意：这会停止所有Python进程，请谨慎使用
   
   # 方法2：根据进程ID停止（更安全）
   # 先查找进程ID
   Get-Process python | Where-Object {$_.Path -like "*AI合同*"}
   # 然后停止特定进程（替换PID为实际进程ID）
   Stop-Process -Id <PID> -Force
   ```

3. **重新启动 Celery**：
   ```powershell
   cd backend
   celery -A config worker -l info
   ```

### 方法3：使用批处理脚本（最简单）

创建一个重启脚本 `restart_celery.bat`：

```batch
@echo off
echo 正在停止 Celery 服务...
taskkill /F /FI "WINDOWTITLE eq celery*" /T 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *celery*" /T 2>nul
timeout /t 2 /nobreak >nul
echo 正在启动 Celery 服务...
cd backend
start "Celery Worker" cmd /k "celery -A config worker -l info"
echo Celery 服务已重启
pause
```

### 方法4：检查 Celery 是否正在运行

```powershell
# 检查是否有 Celery 进程
Get-Process | Where-Object {$_.ProcessName -eq "python"} | Select-Object Id, ProcessName, Path
```

## 验证 Celery 是否正常运行

重启后，检查以下几点：

1. **查看 Celery 输出**：
   - 应该看到类似以下信息：
     ```
     celery@hostname v5.x.x
     [config]
     .> task: apps.reviews.tasks.process_review_task
     ```

2. **测试任务执行**：
   - 创建一个新的审核任务
   - 观察任务是否能正常处理

3. **查看日志**：
   - 检查 `backend/logs/django.log` 或 `backend/logs/error.log`
   - 查看是否有错误信息

## 常见问题

### 问题1：无法停止 Celery 进程
- **解决方案**：使用任务管理器强制结束进程

### 问题2：重启后任务仍然卡住
- **解决方案**：
  1. 检查 Redis 是否正常运行（Celery 使用 Redis 作为消息队列）
  2. 清除 Redis 中的旧任务：
     ```bash
     redis-cli FLUSHDB
     ```
  3. 检查后端日志查看具体错误

### 问题3：Celery 启动失败
- **可能原因**：
  - Redis 未启动
  - 虚拟环境未激活
  - 依赖包未安装
- **解决方案**：
  ```bash
  # 激活虚拟环境
  conda activate hetong  # 或你的虚拟环境名称
  
  # 安装依赖
  pip install -r requirements.txt
  
  # 确保 Redis 运行
  # Windows 下需要安装并启动 Redis
  ```

## 快速重启命令（一键脚本）

将以下内容保存为 `restart_celery.bat` 并放在项目根目录：

```batch
@echo off
chcp 65001 >nul
echo ========================================
echo 正在重启 Celery 服务...
echo ========================================
echo.

echo [1/3] 停止现有 Celery 进程...
for /f "tokens=2" %%a in ('tasklist ^| findstr /i "python.exe"') do (
    wmic process where "ProcessId=%%a" get CommandLine 2>nul | findstr /i "celery" >nul
    if !errorlevel! equ 0 (
        echo 找到 Celery 进程，正在停止...
        taskkill /F /PID %%a >nul 2>&1
    )
)
timeout /t 2 /nobreak >nul

echo [2/3] 检查 Redis 连接...
cd backend
python -c "import redis; r=redis.Redis(); r.ping()" 2>nul
if errorlevel 1 (
    echo 警告: Redis 可能未运行，请确保 Redis 服务已启动
)

echo [3/3] 启动 Celery Worker...
start "Celery Worker" cmd /k "cd /d %~dp0backend && celery -A config worker -l info"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo Celery 服务重启完成！
echo ========================================
echo.
echo 提示：
echo - Celery Worker 窗口已打开，请查看是否有错误信息
echo - 如果看到 "ready" 消息，说明 Celery 已成功启动
echo - 按任意键关闭此窗口
pause >nul
```

