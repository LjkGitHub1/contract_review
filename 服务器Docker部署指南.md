# 服务器Docker部署指南

本文档详细介绍如何在Linux服务器上使用Docker部署AI智能合同审核系统。

## 目录

1. [服务器环境要求](#服务器环境要求)
2. [安装Docker和Docker Compose](#安装docker和docker-compose)
3. [项目部署步骤](#项目部署步骤)
4. [配置说明](#配置说明)
5. [服务管理](#服务管理)
6. [故障排查](#故障排查)
7. [维护和更新](#维护和更新)
8. [安全建议](#安全建议)

## 服务器环境要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **磁盘**: 20GB 可用空间
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+

### 推荐配置
- **CPU**: 4核心+
- **内存**: 8GB+ RAM
- **磁盘**: 50GB+ 可用空间（SSD推荐）
- **操作系统**: Ubuntu 22.04 LTS

### 网络要求
- 开放端口：80（前端）、8000（后端，可选）、3306（MySQL，建议仅内网）、6379（Redis，建议仅内网）
- 如需HTTPS，还需开放443端口

## 安装Docker和Docker Compose

### Ubuntu/Debian

```bash
# 1. 更新系统包
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# 2. 添加Docker官方GPG密钥
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 3. 添加Docker仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 4. 安装Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 5. 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 6. 验证安装
sudo docker --version
sudo docker compose version
```

### CentOS/RHEL

```bash
# 1. 安装必要工具
sudo yum install -y yum-utils

# 2. 添加Docker仓库
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# 3. 安装Docker Engine
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 4. 启动Docker服务
sudo systemctl start docker
sudo systemctl enable docker

# 5. 验证安装
sudo docker --version
sudo docker compose version
```

### 配置Docker（可选但推荐）

```bash
# 1. 将当前用户添加到docker组（避免每次使用sudo）
sudo usermod -aG docker $USER

# 2. 重新登录或执行以下命令使组生效
newgrp docker

# 3. 配置Docker镜像加速（国内服务器推荐）
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ],
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# 4. 重启Docker服务
sudo systemctl daemon-reload
sudo systemctl restart docker
```

## 项目部署步骤

### 步骤1: 上传项目文件到服务器

**方式1: 使用Git（推荐）**

```bash
# 在服务器上克隆项目
cd /opt
sudo git clone <your-repo-url> contract_review
cd contract_review
```

**方式2: 使用SCP上传**

```bash
# 在本地执行
scp -r /path/to/AI合同 root@your-server-ip:/opt/contract_review
```

**方式3: 使用SFTP工具**

使用FileZilla、WinSCP等工具上传项目文件夹到服务器的 `/opt/contract_review`

### 步骤2: 配置环境变量

```bash
# 进入项目目录
cd /opt/contract_review

# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（使用nano或vim）
sudo nano .env
# 或
sudo vim .env
```

**重要配置项：**

```env
# Django配置
DEBUG=False
SECRET_KEY=<生成一个强密钥，至少50个字符>

# 数据库配置
DB_NAME=contract_review
DB_USER=root
DB_PASSWORD=<设置强密码>
DB_HOST=db
DB_PORT=3306
DB_ROOT_PASSWORD=<设置强密码>

# Redis配置
REDIS_PORT=6379

# Celery配置
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
REDIS_CACHE_URL=redis://redis:6379/1

# CORS配置（替换为实际域名）
CORS_ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# 端口配置
BACKEND_PORT=8000
FRONTEND_PORT=80
```

**生成SECRET_KEY：**

```bash
# 方法1: 使用Python
python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# 方法2: 使用OpenSSL
openssl rand -base64 50
```

### 步骤3: 配置防火墙

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp  # 如果使用HTTPS
sudo ufw allow 8000/tcp  # 如果需要直接访问后端API
sudo ufw enable
sudo ufw status

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload
sudo firewall-cmd --list-ports
```

### 步骤4: 构建和启动服务

```bash
# 进入项目目录
cd /opt/contract_review

# 构建Docker镜像（首次部署或更新后）
sudo docker compose build

# 启动所有服务
sudo docker compose up -d

# 查看服务状态
sudo docker compose ps

# 查看日志
sudo docker compose logs -f
```

### 步骤5: 初始化数据库

```bash
# 等待数据库启动（约10-30秒）
sleep 15

# 执行数据库迁移
sudo docker compose exec backend python manage.py migrate

# 收集静态文件
sudo docker compose exec backend python manage.py collectstatic --noinput

# 创建超级用户
sudo docker compose exec backend python manage.py createsuperuser
```

### 步骤6: 验证部署

```bash
# 1. 检查所有服务状态
sudo docker compose ps

# 2. 检查服务健康状态
sudo docker compose exec backend python manage.py check
sudo docker compose exec db mysqladmin ping -h localhost -u root -p

# 3. 测试前端访问
curl http://localhost

# 4. 测试后端API
curl http://localhost:8000/api/users/users/me/

# 5. 查看日志
sudo docker compose logs --tail=50
```

## 配置说明

### 使用生产环境配置

生产环境使用优化配置：

```bash
# 使用生产环境配置启动
sudo docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

生产环境配置特点：
- 更多Gunicorn workers（8个）
- 资源限制和预留
- 日志轮转
- 性能优化

### 自定义端口

如果需要使用其他端口（如8848），修改 `.env` 文件：

```env
FRONTEND_PORT=8848
```

然后修改 `docker-compose.yml` 中的端口映射，或使用环境变量：

```bash
FRONTEND_PORT=8848 sudo docker compose up -d
```

### 配置HTTPS（使用Nginx反向代理）

如果需要HTTPS，可以在Docker外部配置Nginx反向代理：

```nginx
# /etc/nginx/sites-available/contract_review
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## 服务管理

### 启动服务

```bash
cd /opt/contract_review
sudo docker compose up -d
```

### 停止服务

```bash
sudo docker compose down
```

### 重启服务

```bash
# 重启所有服务
sudo docker compose restart

# 重启特定服务
sudo docker compose restart backend
sudo docker compose restart celery
```

### 查看日志

```bash
# 查看所有服务日志
sudo docker compose logs -f

# 查看特定服务日志
sudo docker compose logs -f backend
sudo docker compose logs -f celery
sudo docker compose logs -f frontend

# 查看最近100行日志
sudo docker compose logs --tail=100 backend
```

### 进入容器

```bash
# 进入后端容器
sudo docker compose exec backend bash

# 进入数据库容器
sudo docker compose exec db bash

# 进入Redis容器
sudo docker compose exec redis sh
```

### 数据库操作

```bash
# 执行迁移
sudo docker compose exec backend python manage.py migrate

# 创建超级用户
sudo docker compose exec backend python manage.py createsuperuser

# 进入Django shell
sudo docker compose exec backend python manage.py shell

# 进入MySQL命令行
sudo docker compose exec db mysql -u root -p
```

### 备份和恢复

**备份数据库：**

```bash
# 创建备份目录
mkdir -p /opt/backups

# 备份数据库
sudo docker compose exec db mysqldump -u root -p contract_review > /opt/backups/backup_$(date +%Y%m%d_%H%M%S).sql

# 或使用Docker volume备份
sudo docker run --rm -v contract_review_mysql_data:/data -v /opt/backups:/backup alpine tar czf /backup/mysql_backup_$(date +%Y%m%d_%H%M%S).tar.gz /data
```

**恢复数据库：**

```bash
# 从SQL文件恢复
sudo docker compose exec -T db mysql -u root -p contract_review < /opt/backups/backup_20240101_120000.sql

# 从volume备份恢复
sudo docker run --rm -v contract_review_mysql_data:/data -v /opt/backups:/backup alpine tar xzf /backup/mysql_backup_20240101_120000.tar.gz -C /
```

## 故障排查

### 服务无法启动

```bash
# 1. 检查Docker服务状态
sudo systemctl status docker

# 2. 检查容器状态
sudo docker compose ps -a

# 3. 查看错误日志
sudo docker compose logs

# 4. 检查端口占用
sudo netstat -tlnp | grep -E '80|8000|3306|6379'

# 5. 检查磁盘空间
df -h

# 6. 检查内存使用
free -h
```

### 数据库连接失败

```bash
# 1. 检查数据库容器状态
sudo docker compose ps db

# 2. 查看数据库日志
sudo docker compose logs db

# 3. 测试数据库连接
sudo docker compose exec backend python manage.py dbshell

# 4. 检查环境变量
sudo docker compose exec backend env | grep DB_
```

### Celery任务不执行

```bash
# 1. 检查Celery容器状态
sudo docker compose ps celery

# 2. 查看Celery日志
sudo docker compose logs celery

# 3. 检查Redis连接
sudo docker compose exec celery celery -A config inspect active

# 4. 重启Celery
sudo docker compose restart celery
```

### 前端无法访问

```bash
# 1. 检查前端容器状态
sudo docker compose ps frontend

# 2. 查看前端日志
sudo docker compose logs frontend

# 3. 检查Nginx配置
sudo docker compose exec frontend cat /etc/nginx/conf.d/default.conf

# 4. 测试后端API
curl http://localhost:8000/api/users/users/me/
```

### 静态文件404

```bash
# 重新收集静态文件
sudo docker compose exec backend python manage.py collectstatic --noinput

# 检查静态文件目录
sudo docker compose exec backend ls -la /app/staticfiles/
```

### 内存不足

```bash
# 检查内存使用
free -h
sudo docker stats

# 如果内存不足，可以：
# 1. 减少Gunicorn workers数量
# 2. 减少Celery并发数
# 3. 增加服务器内存
```

## 维护和更新

### 更新项目代码

```bash
# 1. 进入项目目录
cd /opt/contract_review

# 2. 备份数据库（重要！）
sudo docker compose exec db mysqldump -u root -p contract_review > /opt/backups/backup_before_update_$(date +%Y%m%d_%H%M%S).sql

# 3. 拉取最新代码
sudo git pull
# 或重新上传文件

# 4. 重新构建镜像
sudo docker compose build

# 5. 停止服务
sudo docker compose down

# 6. 启动服务（会自动运行迁移）
sudo docker compose up -d

# 7. 执行数据库迁移（如果需要）
sudo docker compose exec backend python manage.py migrate

# 8. 收集静态文件
sudo docker compose exec backend python manage.py collectstatic --noinput

# 9. 检查服务状态
sudo docker compose ps
sudo docker compose logs --tail=50
```

### 清理未使用的资源

```bash
# 清理未使用的镜像
sudo docker image prune -a

# 清理未使用的容器
sudo docker container prune

# 清理未使用的volumes（谨慎使用，会删除数据）
sudo docker volume prune

# 清理所有未使用的资源
sudo docker system prune -a
```

### 监控服务

```bash
# 实时查看资源使用
sudo docker stats

# 查看服务健康状态
sudo docker compose ps

# 设置定时任务检查服务（可选）
# 编辑crontab: crontab -e
# 添加: */5 * * * * cd /opt/contract_review && docker compose ps | grep -q "Up" || docker compose up -d
```

## 安全建议

### 1. 修改默认密码

- 数据库root密码
- Django SECRET_KEY
- 所有默认配置

### 2. 配置防火墙

只开放必要的端口，数据库和Redis端口不要对外开放。

### 3. 使用HTTPS

生产环境必须使用HTTPS，配置SSL证书。

### 4. 定期更新

```bash
# 更新系统包
sudo apt-get update && sudo apt-get upgrade -y  # Ubuntu/Debian
sudo yum update -y  # CentOS/RHEL

# 更新Docker
sudo apt-get install docker-ce docker-ce-cli containerd.io  # Ubuntu/Debian

# 更新项目依赖
sudo docker compose build --no-cache
```

### 5. 定期备份

设置定时备份任务：

```bash
# 编辑crontab
crontab -e

# 添加每日备份（每天凌晨2点）
0 2 * * * cd /opt/contract_review && docker compose exec -T db mysqldump -u root -p<password> contract_review > /opt/backups/daily_backup_$(date +\%Y\%m\%d).sql && find /opt/backups -name "daily_backup_*.sql" -mtime +7 -delete
```

### 6. 日志管理

配置日志轮转，避免日志文件过大。

### 7. 限制资源

在 `docker-compose.prod.yml` 中配置资源限制，防止单个服务占用过多资源。

### 8. 监控和告警

建议配置监控系统（如Prometheus + Grafana）监控服务状态。

## 常见问题

### Q: 如何修改端口？

A: 修改 `.env` 文件中的端口配置，然后重启服务。

### Q: 如何查看容器资源使用？

A: 使用 `sudo docker stats` 命令。

### Q: 如何扩容服务？

A: 修改 `docker-compose.prod.yml` 中的资源限制和worker数量。

### Q: 数据会丢失吗？

A: 数据保存在Docker volumes中，只要volumes不删除，数据不会丢失。建议定期备份。

### Q: 如何查看服务日志？

A: 使用 `sudo docker compose logs -f [service_name]` 命令。

### Q: 服务启动失败怎么办？

A: 查看日志 `sudo docker compose logs`，根据错误信息排查问题。

## 技术支持

如遇问题，请：
1. 查看服务日志：`sudo docker compose logs`
2. 检查服务状态：`sudo docker compose ps`
3. 查看系统资源：`free -h`、`df -h`
4. 查看Docker日志：`sudo journalctl -u docker`

