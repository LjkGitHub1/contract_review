# AI智能合同审核系统

基于Django和Vue3的AI智能合同审核系统，提供合同管理、智能审核、风险识别等功能。

## 技术栈

### 后端
- Django 4.2.7
- Django REST Framework
- Celery (异步任务)
- MySQL 8.0
- JWT认证
- django-filter

### 前端
- Vue 3
- Element Plus
- Vue Router
- Pinia
- Axios

## 项目结构

```
.
├── backend/              # Django后端
│   ├── apps/            # 应用模块
│   │   ├── users/       # 用户管理
│   │   ├── contracts/  # 合同管理
│   │   ├── reviews/    # 合同审核
│   │   ├── rules/      # 规则引擎
│   │   ├── clauses/    # 条款识别
│   │   ├── risks/      # 风险识别
│   │   ├── comparisons/# 对比分析
│   │   ├── knowledge/  # 知识图谱
│   │   └── recommendations/ # 智能推荐
│   ├── config/         # 配置文件
│   └── manage.py
├── frontend/            # Vue3前端
│   ├── src/
│   │   ├── views/      # 页面
│   │   ├── components/ # 组件
│   │   ├── stores/     # 状态管理
│   │   ├── router/    # 路由
│   │   └── utils/     # 工具函数
│   └── package.json
└── 数据库设计文档.md
```

## 安装和运行

### 后端设置

1. 安装Python依赖：
```bash
cd backend
pip install -r requirements.txt
```

2. 配置环境变量：
```bash
cp .env.example .env
# 编辑.env文件，配置数据库和Redis连接信息
```

3. 创建数据库：
```sql
CREATE DATABASE contract_review CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

4. 运行迁移：
```bash
python manage.py migrate
```

5. 创建超级用户：
```bash
python manage.py createsuperuser
```

6. 启动开发服务器：
```bash
python manage.py runserver
```

7. 启动Celery Worker（新终端）：
```bash
celery -A config worker -l info
```

### 前端设置

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 启动开发服务器：
```bash
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

## 功能模块

### 1. 用户与权限管理
- 用户管理
- 角色权限管理（RBAC）
- 部门管理
- 审计日志

### 2. 合同管理
- 合同起草辅助
- 合同模板库
- 个性化定制
- 合同版本管理

### 3. 合同审核
- 自动审核
- 审核意见闭环
- 报告生成

### 4. 规则引擎
- 审核规则库构建
- 审核规则动态调用

### 5. 条款识别
- 关键条款语义理解提取
- 结构化展示

### 6. 风险识别及预警
- 多维度风险扫描
- 风险量化分级
- 实时预警处理

### 7. 对比分析
- 合同版本对比
- 合同与模板对比
- 跨行业合同对比

### 8. 知识图谱
- 实体和关系定义
- 法律法规库
- 案例库

### 9. 智能推荐
- 条款推荐
- 模板推荐
- 风险应对建议推荐

## API文档

启动后端服务后，访问：
- Django Admin: http://localhost:8000/admin/
- API根路径: http://localhost:8000/api/

## 默认账号

创建超级用户后，使用以下信息登录：
- 用户名：admin（或您创建的用户名）
- 密码：您设置的密码

## 注意事项

1. 确保MySQL 8.0已安装并运行
2. 确保Redis已安装并运行（用于Celery）
3. 生产环境请修改SECRET_KEY和DEBUG设置
4. 建议使用虚拟环境管理Python依赖

## 开发计划

- [ ] 集成大模型API进行智能审核
- [ ] 完善文件上传和解析功能
- [ ] 实现知识图谱可视化
- [ ] 添加更多审核规则
- [ ] 优化前端UI/UX

## 许可证

MIT License

