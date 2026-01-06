# Docker部署指南

本文档介绍如何使用Docker和Docker Compose部署AI智能合同审核系统。

## 前置要求

- Docker Engine 20.10+
- Docker Compose 2.0+
- 至少4GB可用内存
- 至少10GB可用磁盘空间

## 快速开始

### 1. 克隆项目（如果还没有）

```bash
git clone <your-repo-url>
cd AI合同
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（重要：修改SECRET_KEY和数据库密码）
nano .env
# 或
vim .env
```

**重要配置项：**

- `SECRET_KEY`: Django密钥，生产环境必须修改
- `DB_PASSWORD`: MySQL数据库密码
- `DB_ROOT_PASSWORD`: MySQL root密码
- `CORS_ALLOWED_ORIGINS`: 允许的前端域名（多个用逗号分隔）

### 3. 构建并启动服务

```bash
# 构建所有镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 4. 初始化数据库

```bash
# 如果contract_review.sql存在，数据库会自动初始化
# 否则需要手动创建超级用户

# 进入后端容器
docker-compose exec backend bash

# 创建超级用户
python manage.py createsuperuser

# 退出容器
exit
```

### 5. 访问应用

- **前端**: http://localhost (或 http://localhost:80)
- **后端API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

## 服务说明

### 服务列表

| 服务名 | 容器名 | 端口 | 说明 |
|--------|--------|------|------|
| db | contract_review_db | 3306 | MySQL数据库 |
| redis | contract_review_redis | 6379 | Redis缓存和Celery消息队列 |
| backend | contract_review_backend | 8000 | Django后端API |
| celery | contract_review_celery | - | Celery Worker（处理异步任务） |
| celery-beat | contract_review_celery_beat | - | Celery Beat（定时任务，可选） |
| frontend | contract_review_frontend | 80 | Vue前端（Nginx） |

### 数据持久化

以下数据会持久化到Docker volumes：

- `mysql_data`: MySQL数据
- `redis_data`: Redis数据
- `backend_media`: 上传的媒体文件
- `backend_static`: Django静态文件
- `backend_logs`: 应用日志

## 常用命令

### 启动和停止

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 停止并删除volumes（注意：会删除数据）
docker-compose down -v

# 重启服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
```

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f celery
docker-compose logs -f frontend

# 查看最近100行日志
docker-compose logs --tail=100 backend
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec db bash

# 进入Redis容器
docker-compose exec redis sh
```

### 数据库操作

```bash
# 执行数据库迁移
docker-compose exec backend python manage.py migrate

# 创建超级用户
docker-compose exec backend python manage.py createsuperuser

# 收集静态文件
docker-compose exec backend python manage.py collectstatic --noinput

# 进入MySQL命令行
docker-compose exec db mysql -u root -p
# 密码：.env文件中DB_ROOT_PASSWORD的值
```

### 重建服务

```bash
# 重新构建并启动
docker-compose up -d --build

# 只重建特定服务
docker-compose build backend
docker-compose up -d backend
```

## 生产环境配置

### 1. 修改环境变量

```bash
# 编辑.env文件
nano .env
```

**必须修改的配置：**

```env
DEBUG=False
SECRET_KEY=<生成一个强密钥>
DB_PASSWORD=<强密码>
DB_ROOT_PASSWORD=<强密码>
CORS_ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. 使用Gunicorn（已配置）

后端已配置使用Gunicorn，4个工作进程。如需调整：

编辑 `docker-compose.yml` 中的 `backend` 服务：

```yaml
command: >
  sh -c "python manage.py migrate &&
         python manage.py collectstatic --noinput &&
         gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120"
```

### 3. 配置HTTPS（使用Nginx反向代理）

如果需要HTTPS，可以在Docker Compose外部配置Nginx反向代理，或使用Traefik等工具。

### 4. 资源限制

在 `docker-compose.yml` 中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

### 5. 日志管理

配置日志轮转，编辑 `docker-compose.yml`：

```yaml
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 故障排查

### 1. 服务无法启动

```bash
# 查看服务状态
docker-compose ps

# 查看错误日志
docker-compose logs <service_name>

# 检查端口占用
netstat -tlnp | grep <port>
```

### 2. 数据库连接失败

```bash
# 检查数据库容器状态
docker-compose ps db

# 查看数据库日志
docker-compose logs db

# 测试数据库连接
docker-compose exec backend python manage.py dbshell
```

### 3. Celery任务不执行

```bash
# 检查Celery容器状态
docker-compose ps celery

# 查看Celery日志
docker-compose logs celery

# 重启Celery
docker-compose restart celery
```

### 4. 前端无法访问后端API

```bash
# 检查前端Nginx配置
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# 检查后端服务
docker-compose logs backend

# 测试后端API
curl http://localhost:8000/api/users/users/me/
```

### 5. 静态文件404

```bash
# 重新收集静态文件
docker-compose exec backend python manage.py collectstatic --noinput

# 检查静态文件目录
docker-compose exec backend ls -la /app/staticfiles/
```

## 备份和恢复

### 备份数据库

```bash
# 备份MySQL数据
docker-compose exec db mysqldump -u root -p contract_review > backup_$(date +%Y%m%d_%H%M%S).sql

# 备份volumes
docker run --rm -v contract_review_mysql_data:/data -v $(pwd):/backup alpine tar czf /backup/mysql_backup.tar.gz /data
```

### 恢复数据库

```bash
# 恢复SQL文件
docker-compose exec -T db mysql -u root -p contract_review < backup.sql

# 恢复volume
docker run --rm -v contract_review_mysql_data:/data -v $(pwd):/backup alpine tar xzf /backup/mysql_backup.tar.gz -C /
```

## 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker-compose build

# 3. 停止服务
docker-compose down

# 4. 启动服务（会自动运行迁移）
docker-compose up -d

# 5. 检查服务状态
docker-compose ps
docker-compose logs -f
```

## 性能优化

### 1. 增加Celery Worker数量

编辑 `docker-compose.yml`：

```yaml
celery:
  command: celery -A config worker --loglevel=info --concurrency=8
```

### 2. 使用Redis持久化

Redis已配置AOF持久化，数据会保存到volume。

### 3. 数据库连接池

在Django settings中配置数据库连接池（使用django-db-connection-pool）。

## 安全建议

1. **修改默认密码**：所有默认密码必须修改
2. **使用HTTPS**：生产环境必须使用HTTPS
3. **限制CORS**：只允许必要的域名
4. **定期更新**：保持Docker镜像和依赖更新
5. **备份数据**：定期备份数据库和重要文件
6. **监控日志**：定期检查日志，发现异常

## 常见问题

### Q: 如何修改端口？

编辑 `.env` 文件中的 `FRONTEND_PORT` 和 `BACKEND_PORT`，然后重启服务。

### Q: 如何添加新的环境变量？

1. 在 `.env` 文件中添加
2. 在 `docker-compose.yml` 的 `environment` 部分添加
3. 重启服务

### Q: 如何查看容器资源使用情况？

```bash
docker stats
```

### Q: 如何清理未使用的资源？

```bash
# 清理未使用的镜像、容器、网络
docker system prune

# 清理所有未使用的资源（包括volumes，谨慎使用）
docker system prune -a --volumes
```

## 技术支持

如遇问题，请查看：
1. 服务日志：`docker-compose logs`
2. Docker日志：`docker logs <container_name>`
3. 系统日志：`journalctl -u docker`

