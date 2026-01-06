#!/bin/bash
# Docker快速启动脚本

set -e

echo "=========================================="
echo "AI智能合同审核系统 - Docker部署"
echo "=========================================="

# 检查Docker和Docker Compose
if ! command -v docker &> /dev/null; then
    echo "错误: 未安装Docker，请先安装Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: 未安装Docker Compose，请先安装Docker Compose"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "创建.env文件..."
    cp .env.example .env
    echo "警告: 请编辑.env文件，修改SECRET_KEY和数据库密码！"
    read -p "按Enter继续，或Ctrl+C取消..."
fi

# 选择环境
echo ""
echo "请选择部署环境:"
echo "1) 开发环境 (development)"
echo "2) 生产环境 (production)"
read -p "请输入选项 (1/2): " env_choice

case $env_choice in
    1)
        COMPOSE_FILE="docker-compose.yml -f docker-compose.dev.yml"
        echo "使用开发环境配置"
        ;;
    2)
        COMPOSE_FILE="docker-compose.yml -f docker-compose.prod.yml"
        echo "使用生产环境配置"
        ;;
    *)
        echo "无效选项，使用默认配置"
        COMPOSE_FILE="docker-compose.yml"
        ;;
esac

# 构建镜像
echo ""
echo "构建Docker镜像..."
docker-compose -f $COMPOSE_FILE build

# 启动服务
echo ""
echo "启动服务..."
docker-compose -f $COMPOSE_FILE up -d

# 等待服务启动
echo ""
echo "等待服务启动..."
sleep 10

# 检查服务状态
echo ""
echo "检查服务状态..."
docker-compose -f $COMPOSE_FILE ps

# 执行数据库迁移
echo ""
echo "执行数据库迁移..."
docker-compose -f $COMPOSE_FILE exec -T backend python manage.py migrate

# 收集静态文件
echo ""
echo "收集静态文件..."
docker-compose -f $COMPOSE_FILE exec -T backend python manage.py collectstatic --noinput

# 创建超级用户提示
echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  前端: http://localhost"
echo "  后端API: http://localhost:8000"
echo "  Django Admin: http://localhost:8000/admin"
echo ""
echo "创建超级用户:"
echo "  docker-compose -f $COMPOSE_FILE exec backend python manage.py createsuperuser"
echo ""
echo "查看日志:"
echo "  docker-compose -f $COMPOSE_FILE logs -f"
echo ""
echo "停止服务:"
echo "  docker-compose -f $COMPOSE_FILE down"
echo ""

