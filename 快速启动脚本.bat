@echo off
REM Docker快速启动脚本 (Windows)

echo ==========================================
echo AI智能合同审核系统 - Docker部署
echo ==========================================
echo.

REM 检查Docker
where docker >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未安装Docker，请先安装Docker Desktop
    pause
    exit /b 1
)

REM 检查Docker Compose
where docker-compose >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo 错误: 未安装Docker Compose，请先安装Docker Compose
    pause
    exit /b 1
)

REM 检查.env文件
if not exist .env (
    echo 创建.env文件...
    copy .env.example .env
    echo 警告: 请编辑.env文件，修改SECRET_KEY和数据库密码！
    pause
)

REM 选择环境
echo.
echo 请选择部署环境:
echo 1) 开发环境 (development)
echo 2) 生产环境 (production)
set /p env_choice="请输入选项 (1/2): "

if "%env_choice%"=="1" (
    set COMPOSE_FILE=docker-compose.yml -f docker-compose.dev.yml
    echo 使用开发环境配置
) else if "%env_choice%"=="2" (
    set COMPOSE_FILE=docker-compose.yml -f docker-compose.prod.yml
    echo 使用生产环境配置
) else (
    set COMPOSE_FILE=docker-compose.yml
    echo 使用默认配置
)

REM 构建镜像
echo.
echo 构建Docker镜像...
docker-compose -f %COMPOSE_FILE% build

REM 启动服务
echo.
echo 启动服务...
docker-compose -f %COMPOSE_FILE% up -d

REM 等待服务启动
echo.
echo 等待服务启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo.
echo 检查服务状态...
docker-compose -f %COMPOSE_FILE% ps

REM 执行数据库迁移
echo.
echo 执行数据库迁移...
docker-compose -f %COMPOSE_FILE% exec -T backend python manage.py migrate

REM 收集静态文件
echo.
echo 收集静态文件...
docker-compose -f %COMPOSE_FILE% exec -T backend python manage.py collectstatic --noinput

REM 完成提示
echo.
echo ==========================================
echo 部署完成！
echo ==========================================
echo.
echo 访问地址:
echo   前端: http://localhost
echo   后端API: http://localhost:8000
echo   Django Admin: http://localhost:8000/admin
echo.
echo 创建超级用户:
echo   docker-compose -f %COMPOSE_FILE% exec backend python manage.py createsuperuser
echo.
echo 查看日志:
echo   docker-compose -f %COMPOSE_FILE% logs -f
echo.
echo 停止服务:
echo   docker-compose -f %COMPOSE_FILE% down
echo.
pause

