# 前端项目文档

## 快速开始

1. 安装依赖：
```bash
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

## 项目结构

```
src/
├── views/          # 页面组件
│   ├── Login.vue   # 登录页
│   ├── Dashboard.vue # 仪表盘
│   ├── contracts/  # 合同管理页面
│   ├── templates/  # 模板管理页面
│   ├── reviews/    # 审核管理页面
│   ├── rules/      # 规则管理页面
│   ├── knowledge/  # 知识图谱页面
│   └── users/      # 用户管理页面
├── layouts/        # 布局组件
│   └── MainLayout.vue
├── stores/         # Pinia状态管理
│   └── user.js
├── router/         # 路由配置
│   └── index.js
└── utils/          # 工具函数
    └── api.js      # API请求封装
```

## 主要功能

### 1. 登录认证
- JWT Token认证
- 自动刷新Token
- 路由守卫

### 2. 合同管理
- 合同列表（支持搜索和过滤）
- 创建合同
- 合同详情
- 版本管理

### 3. 合同审核
- 审核任务列表
- 启动审核任务
- 查看审核结果
- 审核意见展示

### 4. 模板管理
- 模板列表
- 使用模板创建合同

### 5. 规则引擎
- 规则列表展示

### 6. 知识图谱
- 实体列表
- 法律法规库
- 案例库

### 7. 用户管理
- 用户列表（管理员可见）

## 技术栈

- Vue 3 (Composition API)
- Element Plus (UI组件库)
- Vue Router (路由)
- Pinia (状态管理)
- Axios (HTTP客户端)
- Vite (构建工具)

## 环境变量

可以在 `vite.config.js` 中配置API代理地址。

## 开发规范

1. 使用Composition API
2. 组件使用 `<script setup>` 语法
3. API请求统一使用 `@/utils/api.js`
4. 状态管理使用Pinia
5. 样式使用scoped

