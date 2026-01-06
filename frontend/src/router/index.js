import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

// 路由懒加载优化
const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import(/* webpackChunkName: "login" */ '@/views/Login.vue'),
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    component: () => import(/* webpackChunkName: "layout" */ '@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import(/* webpackChunkName: "dashboard" */ '@/views/Dashboard.vue'),
      },
      {
        path: 'contracts',
        name: 'Contracts',
        component: () => import(/* webpackChunkName: "contracts" */ '@/views/contracts/ContractList.vue'),
      },
      {
        path: 'contracts/create',
        name: 'ContractCreate',
        component: () => import(/* webpackChunkName: "contracts" */ '@/views/contracts/ContractCreate.vue'),
      },
      {
        path: 'contracts/:id',
        name: 'ContractDetail',
        component: () => import(/* webpackChunkName: "contracts" */ '@/views/contracts/ContractDetail.vue'),
      },
      {
        path: 'templates',
        name: 'Templates',
        component: () => import(/* webpackChunkName: "templates" */ '@/views/templates/TemplateList.vue'),
      },
      {
        path: 'reviews',
        name: 'Reviews',
        component: () => import(/* webpackChunkName: "reviews" */ '@/views/reviews/ReviewList.vue'),
      },
      {
        path: 'reviews/:id',
        name: 'ReviewDetail',
        component: () => import(/* webpackChunkName: "reviews" */ '@/views/reviews/ReviewDetail.vue'),
      },
      {
        path: 'review-focus-config',
        name: 'ReviewFocusConfig',
        component: () => import(/* webpackChunkName: "reviews" */ '@/views/reviews/ReviewFocusConfig.vue'),
        meta: { requiresAuth: true, roles: ['admin'] },
      },
      {
        path: 'ai-model-config',
        name: 'AIModelConfig',
        component: () => import(/* webpackChunkName: "reviews" */ '@/views/reviews/AIModelConfig.vue'),
        meta: { requiresAuth: true, roles: ['admin'] },
      },
      {
        path: 'rules',
        name: 'Rules',
        component: () => import(/* webpackChunkName: "rules" */ '@/views/rules/RuleList.vue'),
      },
      {
        path: 'rule-matches',
        name: 'RuleMatches',
        component: () => import(/* webpackChunkName: "rules" */ '@/views/rules/RuleMatchList.vue'),
      },
      {
        path: 'knowledge',
        name: 'Knowledge',
        component: () => import(/* webpackChunkName: "knowledge" */ '@/views/knowledge/KnowledgeGraph.vue'),
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import(/* webpackChunkName: "users" */ '@/views/users/UserList.vue'),
      },
      {
        path: 'departments',
        name: 'Departments',
        component: () => import(/* webpackChunkName: "users" */ '@/views/users/DepartmentList.vue'),
      },
      {
        path: 'audit-logs',
        name: 'AuditLogs',
        component: () => import(/* webpackChunkName: "users" */ '@/views/users/AuditLogList.vue'),
      },
      {
        path: 'permission-config',
        name: 'PermissionConfig',
        component: () => import(/* webpackChunkName: "users" */ '@/views/users/PermissionConfig.vue'),
        meta: { requiresAuth: true, roles: ['admin'] },
      },
      {
        path: 'ai-chat',
        name: 'AIChat',
        component: () => import(/* webpackChunkName: "ai" */ '@/views/ai/ChatWindow.vue'),
        meta: { requiresAuth: true },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore()
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    // 如果有token但没有用户信息，则获取用户信息
    if (token && !userStore.user) {
      try {
        await userStore.fetchUserInfo()
      } catch (error) {
        console.error('获取用户信息失败:', error)
        // 如果获取失败，清除token并跳转到登录页
        localStorage.removeItem('token')
        if (to.meta.requiresAuth) {
          next('/login')
          return
        }
      }
    }
    next()
  }
})

export default router

