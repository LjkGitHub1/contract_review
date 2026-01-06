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
        echo 找到 Celery 进程 PID: %%a，正在停止...
        taskkill /F /PID %%a >nul 2>&1
    )
)
timeout /t 2 /nobreak >nul

echo [2/3] 检查环境...
cd backend
if not exist "manage.py" (
    echo 错误: 找不到 manage.py，请确保在项目根目录运行此脚本
    pause
    exit /b 1
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

