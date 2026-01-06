# Docker部署快速参考

## 一键启动

### Linux/Mac
```bash
chmod +x 快速启动脚本.sh
./快速启动脚本.sh
```

### Windows
```cmd
快速启动脚本.bat
```

## 手动启动

### 1. 配置环境变量
```bash
cp .env.example .env
# 编辑.env，修改SECRET_KEY和数据库密码
```

### 2. 启动服务
```bash
# 开发环境
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# 生产环境
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 或使用默认配置
docker-compose up -d
```

### 3. 初始化数据库
```bash
# 执行迁移
docker-compose exec backend python manage.py migrate

# 创建超级用户
docker-compose exec backend python manage.py createsuperuser
```

## 常用命令

```bash
# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f [service_name]

# 重启服务
docker-compose restart [service_name]

# 停止服务
docker-compose down

# 停止并删除数据
docker-compose down -v

# 进入容器
docker-compose exec backend bash
docker-compose exec db bash
```

## 访问地址

- **前端**: http://localhost
- **后端API**: http://localhost:8000
- **Django Admin**: http://localhost:8000/admin

## 端口映射

默认端口映射（可在.env中修改）：

- 前端: 80
- 后端: 8000
- MySQL: 3306
- Redis: 6379

## 数据持久化

数据保存在Docker volumes中：

- `mysql_data`: 数据库数据
- `redis_data`: Redis数据
- `backend_media`: 上传的文件
- `backend_static`: 静态文件
- `backend_logs`: 日志文件

## 故障排查

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务日志
docker-compose logs backend
docker-compose logs celery

# 检查服务健康状态
docker-compose ps

# 重启所有服务
docker-compose restart
```

## 更新部署

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建
docker-compose build

# 3. 重启服务
docker-compose down
docker-compose up -d

# 4. 执行迁移
docker-compose exec backend python manage.py migrate
```

