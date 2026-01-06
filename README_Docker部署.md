# Docker部署说明

## 快速开始

### 方式1: 一键部署（推荐）

**服务器部署:**
```bash
sudo bash 服务器部署一键脚本.sh
```

**本地开发:**
```bash
# Linux/Mac
chmod +x 快速启动脚本.sh
./快速启动脚本.sh

# Windows
快速启动脚本.bat
```

### 方式2: 手动部署

```bash
# 1. 配置环境变量
cp .env.example .env
nano .env  # 修改SECRET_KEY和数据库密码

# 2. 构建并启动
docker compose build
docker compose up -d

# 3. 初始化数据库
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
```

## 文档索引

- **详细部署指南**: [服务器Docker部署指南.md](服务器Docker部署指南.md)
- **快速命令参考**: [服务器快速部署命令.md](服务器快速部署命令.md)
- **部署检查清单**: [服务器部署检查清单.md](服务器部署检查清单.md)
- **Docker部署指南**: [Docker部署指南.md](Docker部署指南.md)
- **快速参考**: [Docker快速参考.md](Docker快速参考.md)
- **文件总览**: [Docker部署文件总览.md](Docker部署文件总览.md)

## 服务说明

启动后包含以下服务：

- **前端** (端口80): Vue.js应用，Nginx服务
- **后端** (端口8000): Django API，Gunicorn服务
- **数据库** (端口3306): MySQL 8.0
- **Redis** (端口6379): 缓存和消息队列
- **Celery**: 异步任务处理
- **Celery Beat**: 定时任务（可选）

## 访问地址

- **前端**: http://localhost
- **后端API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

## 环境要求

- Docker Engine 20.10+
- Docker Compose 2.0+
- 至少4GB内存
- 至少20GB磁盘空间

## 重要配置

部署前必须修改 `.env` 文件中的：

- `SECRET_KEY` - Django密钥（生成强密钥）
- `DB_PASSWORD` - 数据库密码
- `DB_ROOT_PASSWORD` - 数据库root密码
- `CORS_ALLOWED_ORIGINS` - 允许的前端域名

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

# 执行迁移
docker compose exec backend python manage.py migrate
```

## 生产环境

使用生产环境配置：

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 故障排查

查看详细故障排查指南：
- [服务器Docker部署指南.md - 故障排查章节](服务器Docker部署指南.md#故障排查)

## 技术支持

如遇问题：
1. 查看服务日志: `docker compose logs`
2. 检查服务状态: `docker compose ps`
3. 参考详细文档: [服务器Docker部署指南.md](服务器Docker部署指南.md)

