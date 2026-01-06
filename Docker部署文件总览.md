# Docker部署文件总览

本文档列出所有Docker部署相关的文件及其用途。

## 核心配置文件

### 1. `docker-compose.yml`
- **用途**: 主Docker Compose配置文件
- **内容**: 定义所有服务（db, redis, backend, celery, celery-beat, frontend）
- **使用**: `docker compose up -d`

### 2. `docker-compose.prod.yml`
- **用途**: 生产环境覆盖配置
- **内容**: 生产环境优化（更多workers、资源限制、日志配置）
- **使用**: `docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d`

### 3. `docker-compose.dev.yml`
- **用途**: 开发环境覆盖配置
- **内容**: 开发环境配置（开发服务器、热重载）
- **使用**: `docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d`

### 4. `.env.example`
- **用途**: 环境变量模板
- **内容**: 所有可配置的环境变量及默认值
- **使用**: 复制为 `.env` 并修改配置

## Dockerfile文件

### 5. `backend/Dockerfile`
- **用途**: 后端Docker镜像构建文件
- **内容**: Python 3.11环境、安装依赖、配置工作目录
- **使用**: 由docker-compose自动使用

### 6. `frontend/Dockerfile`
- **用途**: 前端生产环境Docker镜像（多阶段构建）
- **内容**: Node.js构建 + Nginx服务
- **使用**: 由docker-compose自动使用

### 7. `frontend/Dockerfile.dev`
- **用途**: 前端开发环境Docker镜像
- **内容**: Node.js开发服务器
- **使用**: 开发环境配置中使用

### 8. `frontend/nginx.conf`
- **用途**: 前端Nginx配置（用于Docker）
- **内容**: 路由配置、API代理、静态文件服务
- **使用**: 由前端Dockerfile复制到容器

## 忽略文件

### 9. `.dockerignore`
- **用途**: 根目录Docker构建忽略文件
- **内容**: 排除不需要的文件（node_modules、.git等）

### 10. `backend/.dockerignore`
- **用途**: 后端Docker构建忽略文件
- **内容**: 排除Python缓存、虚拟环境等

### 11. `frontend/.dockerignore`
- **用途**: 前端Docker构建忽略文件
- **内容**: 排除node_modules、构建产物等

## 部署脚本

### 12. `快速启动脚本.sh`
- **用途**: Linux/Mac一键部署脚本
- **功能**: 检查环境、配置、构建、启动
- **使用**: `chmod +x 快速启动脚本.sh && ./快速启动脚本.sh`

### 13. `快速启动脚本.bat`
- **用途**: Windows一键部署脚本
- **功能**: 检查环境、配置、构建、启动
- **使用**: 双击运行或 `快速启动脚本.bat`

### 14. `服务器部署一键脚本.sh`
- **用途**: 服务器端一键部署脚本（包含Docker安装）
- **功能**: 自动安装Docker、配置环境、部署服务
- **使用**: `sudo bash 服务器部署一键脚本.sh`

## 文档文件

### 15. `Docker部署指南.md`
- **用途**: 详细的Docker部署文档
- **内容**: 完整部署流程、配置说明、故障排查

### 16. `Docker快速参考.md`
- **用途**: 快速参考手册
- **内容**: 常用命令、快速操作指南

### 17. `服务器Docker部署指南.md`
- **用途**: 服务器端详细部署指南
- **内容**: 服务器环境准备、安装、部署、维护

### 18. `服务器部署检查清单.md`
- **用途**: 部署检查清单
- **内容**: 逐步检查项，确保部署完整

### 19. `服务器快速部署命令.md`
- **用途**: 服务器快速部署命令参考
- **内容**: 常用命令、快速操作

### 20. `Docker部署文件总览.md`
- **用途**: 本文档，文件总览
- **内容**: 所有部署文件说明

## 文件结构

```
AI合同/
├── docker-compose.yml              # 主配置文件
├── docker-compose.prod.yml          # 生产环境配置
├── docker-compose.dev.yml           # 开发环境配置
├── .env.example                     # 环境变量模板
├── .dockerignore                    # Docker忽略文件
│
├── backend/
│   ├── Dockerfile                   # 后端Dockerfile
│   ├── .dockerignore                # 后端忽略文件
│   └── requirements.txt             # Python依赖（已添加gunicorn）
│
├── frontend/
│   ├── Dockerfile                   # 前端生产Dockerfile
│   ├── Dockerfile.dev               # 前端开发Dockerfile
│   ├── nginx.conf                   # Nginx配置
│   └── .dockerignore                # 前端忽略文件
│
├── 快速启动脚本.sh                  # Linux/Mac启动脚本
├── 快速启动脚本.bat                 # Windows启动脚本
├── 服务器部署一键脚本.sh            # 服务器部署脚本
│
└── 文档/
    ├── Docker部署指南.md
    ├── Docker快速参考.md
    ├── 服务器Docker部署指南.md
    ├── 服务器部署检查清单.md
    ├── 服务器快速部署命令.md
    └── Docker部署文件总览.md
```

## 部署流程

### 本地开发环境

1. 复制 `.env.example` 为 `.env`
2. 修改 `.env` 配置
3. 运行 `快速启动脚本.sh` 或 `快速启动脚本.bat`
4. 或手动执行：
   ```bash
   docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
   ```

### 服务器生产环境

1. 上传项目到服务器
2. 运行 `sudo bash 服务器部署一键脚本.sh`
3. 或手动执行：
   ```bash
   # 安装Docker（如未安装）
   # 配置.env
   docker compose -f docker-compose.yml -f docker-compose.prod.yml build
   docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   docker compose exec backend python manage.py migrate
   docker compose exec backend python manage.py createsuperuser
   ```

## 服务说明

| 服务名 | 容器名 | 端口 | 说明 |
|--------|--------|------|------|
| db | contract_review_db | 3306 | MySQL 8.0数据库 |
| redis | contract_review_redis | 6379 | Redis缓存和消息队列 |
| backend | contract_review_backend | 8000 | Django后端（Gunicorn） |
| celery | contract_review_celery | - | Celery Worker |
| celery-beat | contract_review_celery_beat | - | Celery Beat（可选） |
| frontend | contract_review_frontend | 80 | Vue前端（Nginx） |

## 数据持久化

数据保存在Docker volumes中：

- `mysql_data`: MySQL数据库数据
- `redis_data`: Redis数据
- `backend_media`: 上传的媒体文件
- `backend_static`: Django静态文件
- `backend_logs`: 应用日志

## 环境变量说明

主要环境变量（在 `.env` 中配置）：

- `DEBUG`: 调试模式（生产环境设为False）
- `SECRET_KEY`: Django密钥（必须修改）
- `DB_NAME`: 数据库名称
- `DB_USER`: 数据库用户
- `DB_PASSWORD`: 数据库密码（必须修改）
- `DB_ROOT_PASSWORD`: 数据库root密码（必须修改）
- `CORS_ALLOWED_ORIGINS`: 允许的前端域名
- `FRONTEND_PORT`: 前端端口（默认80）
- `BACKEND_PORT`: 后端端口（默认8000）

## 常用命令

```bash
# 启动服务
docker compose up -d

# 停止服务
docker compose down

# 查看状态
docker compose ps

# 查看日志
docker compose logs -f

# 重启服务
docker compose restart

# 进入容器
docker compose exec backend bash

# 执行迁移
docker compose exec backend python manage.py migrate

# 创建用户
docker compose exec backend python manage.py createsuperuser
```

## 故障排查

如遇问题，请查看：

1. **服务日志**: `docker compose logs [service_name]`
2. **服务状态**: `docker compose ps`
3. **详细文档**: `服务器Docker部署指南.md`
4. **检查清单**: `服务器部署检查清单.md`

## 更新和维护

1. **更新代码**: `git pull` 或重新上传文件
2. **重新构建**: `docker compose build`
3. **重启服务**: `docker compose down && docker compose up -d`
4. **执行迁移**: `docker compose exec backend python manage.py migrate`

## 注意事项

1. **生产环境必须修改**:
   - `SECRET_KEY`
   - `DB_PASSWORD`
   - `DB_ROOT_PASSWORD`
   - `DEBUG=False`

2. **安全建议**:
   - 使用HTTPS
   - 限制数据库和Redis端口（仅内网）
   - 配置防火墙
   - 定期备份数据

3. **性能优化**:
   - 使用生产环境配置
   - 根据服务器资源调整workers数量
   - 配置日志轮转

4. **备份**:
   - 定期备份数据库
   - 备份重要配置文件
   - 保存环境变量信息

