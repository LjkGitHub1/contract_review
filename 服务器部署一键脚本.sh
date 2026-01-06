#!/bin/bash
# 服务器Docker部署一键脚本
# 使用方法: sudo bash 服务器部署一键脚本.sh

set -e

echo "=========================================="
echo "AI智能合同审核系统 - 服务器Docker部署"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "错误: 请使用sudo运行此脚本"
    exit 1
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "检测到未安装Docker，开始安装..."
    
    # 检测操作系统
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        echo "无法检测操作系统，请手动安装Docker"
        exit 1
    fi
    
    # Ubuntu/Debian安装Docker
    if [ "$OS" == "ubuntu" ] || [ "$OS" == "debian" ]; then
        echo "正在为Ubuntu/Debian安装Docker..."
        apt-get update
        apt-get install -y ca-certificates curl gnupg lsb-release
        mkdir -p /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
          $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        systemctl start docker
        systemctl enable docker
    # CentOS/RHEL安装Docker
    elif [ "$OS" == "centos" ] || [ "$OS" == "rhel" ]; then
        echo "正在为CentOS/RHEL安装Docker..."
        yum install -y yum-utils
        yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
        yum install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
        systemctl start docker
        systemctl enable docker
    else
        echo "不支持的操作系统: $OS"
        echo "请手动安装Docker: https://docs.docker.com/engine/install/"
        exit 1
    fi
    
    echo "Docker安装完成！"
else
    echo "Docker已安装: $(docker --version)"
fi

# 检查Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "错误: Docker Compose未安装"
    exit 1
else
    echo "Docker Compose已安装"
fi

# 获取项目目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$SCRIPT_DIR"

echo ""
echo "项目目录: $PROJECT_DIR"
cd "$PROJECT_DIR"

# 检查.env文件
if [ ! -f .env ]; then
    echo ""
    echo "创建.env文件..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "已从.env.example创建.env文件"
        echo ""
        echo "⚠️  重要: 请编辑.env文件，修改以下配置:"
        echo "  1. SECRET_KEY (生成强密钥)"
        echo "  2. DB_PASSWORD (数据库密码)"
        echo "  3. DB_ROOT_PASSWORD (数据库root密码)"
        echo "  4. CORS_ALLOWED_ORIGINS (允许的前端域名)"
        echo ""
        read -p "按Enter继续（请确保已修改.env文件）..."
    else
        echo "错误: 未找到.env.example文件"
        exit 1
    fi
else
    echo ".env文件已存在"
fi

# 配置防火墙
echo ""
echo "配置防火墙..."
if command -v ufw &> /dev/null; then
    echo "使用UFW配置防火墙..."
    ufw allow 80/tcp
    ufw allow 443/tcp
    echo "防火墙规则已添加（80, 443端口）"
elif command -v firewall-cmd &> /dev/null; then
    echo "使用firewalld配置防火墙..."
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=443/tcp
    firewall-cmd --reload
    echo "防火墙规则已添加（80, 443端口）"
else
    echo "未检测到防火墙，请手动配置端口80和443"
fi

# 选择部署环境
echo ""
echo "请选择部署环境:"
echo "1) 生产环境 (production) - 推荐"
echo "2) 开发环境 (development)"
read -p "请输入选项 (1/2，默认1): " env_choice
env_choice=${env_choice:-1}

case $env_choice in
    1)
        COMPOSE_FILES="docker-compose.yml -f docker-compose.prod.yml"
        echo "使用生产环境配置"
        ;;
    2)
        COMPOSE_FILES="docker-compose.yml -f docker-compose.dev.yml"
        echo "使用开发环境配置"
        ;;
    *)
        COMPOSE_FILES="docker-compose.yml"
        echo "使用默认配置"
        ;;
esac

# 构建镜像
echo ""
echo "构建Docker镜像（这可能需要几分钟）..."
docker compose -f $COMPOSE_FILES build

# 启动服务
echo ""
echo "启动服务..."
docker compose -f $COMPOSE_FILES up -d

# 等待服务启动
echo ""
echo "等待服务启动（30秒）..."
sleep 30

# 检查服务状态
echo ""
echo "检查服务状态..."
docker compose -f $COMPOSE_FILES ps

# 执行数据库迁移
echo ""
echo "执行数据库迁移..."
docker compose -f $COMPOSE_FILES exec -T backend python manage.py migrate || {
    echo "警告: 数据库迁移失败，可能是数据库尚未完全启动"
    echo "等待10秒后重试..."
    sleep 10
    docker compose -f $COMPOSE_FILES exec -T backend python manage.py migrate
}

# 收集静态文件
echo ""
echo "收集静态文件..."
docker compose -f $COMPOSE_FILES exec -T backend python manage.py collectstatic --noinput

# 检查服务健康
echo ""
echo "检查服务健康状态..."
sleep 5

# 测试前端
if curl -s http://localhost > /dev/null; then
    echo "✓ 前端服务正常"
else
    echo "✗ 前端服务异常，请检查日志: docker compose logs frontend"
fi

# 测试后端
if curl -s http://localhost:8000 > /dev/null; then
    echo "✓ 后端服务正常"
else
    echo "✗ 后端服务异常，请检查日志: docker compose logs backend"
fi

# 完成提示
echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "访问地址:"
echo "  前端: http://$(hostname -I | awk '{print $1}')"
echo "  后端API: http://$(hostname -I | awk '{print $1}'):8000"
echo "  Django Admin: http://$(hostname -I | awk '{print $1}'):8000/admin"
echo ""
echo "下一步操作:"
echo "  1. 创建超级用户:"
echo "     docker compose -f $COMPOSE_FILES exec backend python manage.py createsuperuser"
echo ""
echo "  2. 查看服务状态:"
echo "     docker compose -f $COMPOSE_FILES ps"
echo ""
echo "  3. 查看日志:"
echo "     docker compose -f $COMPOSE_FILES logs -f"
echo ""
echo "  4. 停止服务:"
echo "     docker compose -f $COMPOSE_FILES down"
echo ""
echo "详细文档请查看: 服务器Docker部署指南.md"
echo ""

