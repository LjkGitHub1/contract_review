# 后端API文档

## 快速开始

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 配置环境变量（复制.env.example为.env并修改）：
```bash
cp .env.example .env
```

3. 创建数据库并运行迁移：
```bash
python manage.py migrate
```

4. 创建超级用户：
```bash
python manage.py createsuperuser
```

5. 启动开发服务器：
```bash
python manage.py runserver
```

6. 启动Celery Worker（新终端）：
```bash
celery -A config worker -l info
```

## API端点

### 认证
- `POST /api/auth/login/` - 登录获取JWT Token
- `POST /api/auth/refresh/` - 刷新Token

### 用户管理
- `GET /api/users/users/` - 用户列表
- `GET /api/users/users/me/` - 当前用户信息
- `POST /api/users/users/` - 创建用户
- `GET /api/users/departments/` - 部门列表
- `GET /api/users/roles/` - 角色列表
- `GET /api/users/permissions/` - 权限列表
- `GET /api/users/audit-logs/` - 审计日志

### 合同管理
- `GET /api/contracts/contracts/` - 合同列表
- `POST /api/contracts/contracts/` - 创建合同
- `GET /api/contracts/contracts/{id}/` - 合同详情
- `POST /api/contracts/contracts/{id}/create_version/` - 创建新版本
- `GET /api/contracts/contracts/{id}/versions/` - 获取版本列表
- `GET /api/contracts/templates/` - 模板列表
- `POST /api/contracts/templates/` - 创建模板

### 合同审核
- `GET /api/reviews/tasks/` - 审核任务列表
- `POST /api/reviews/tasks/` - 创建审核任务
- `POST /api/reviews/tasks/{id}/start/` - 启动审核任务
- `GET /api/reviews/tasks/{id}/result/` - 获取审核结果
- `GET /api/reviews/results/` - 审核结果列表
- `GET /api/reviews/opinions/` - 审核意见列表
- `GET /api/reviews/cycles/` - 审核闭环列表

### 规则引擎
- `GET /api/rules/rules/` - 规则列表
- `POST /api/rules/rules/` - 创建规则
- `GET /api/rules/matches/` - 规则匹配记录

### 条款识别
- `GET /api/clauses/clauses/` - 条款列表
- `POST /api/clauses/clauses/{id}/confirm/` - 确认条款

### 风险识别
- `GET /api/risks/risks/` - 风险列表
- `POST /api/risks/risks/{id}/handle/` - 处理风险

### 对比分析
- `GET /api/comparisons/tasks/` - 对比任务列表
- `POST /api/comparisons/tasks/` - 创建对比任务
- `GET /api/comparisons/diffs/` - 对比差异列表

### 知识图谱
- `GET /api/knowledge/entities/` - 实体列表
- `GET /api/knowledge/relations/` - 关系列表
- `GET /api/knowledge/regulations/` - 法律法规列表
- `GET /api/knowledge/cases/` - 案例列表

### 智能推荐
- `GET /api/recommendations/recommendations/` - 推荐列表
- `POST /api/recommendations/recommendations/{id}/accept/` - 接受推荐
- `POST /api/recommendations/recommendations/{id}/reject/` - 拒绝推荐

## 认证

所有API请求（除登录外）都需要在Header中携带JWT Token：
```
Authorization: Bearer <your_token>
```

## 分页

列表接口支持分页参数：
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认20）

## 过滤

大部分列表接口支持过滤，使用查询参数：
- `?status=draft` - 按状态过滤
- `?contract_type=procurement` - 按合同类型过滤
- `?search=关键词` - 搜索

