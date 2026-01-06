<template>
  <el-container class="layout-container">
    <el-aside width="250px" class="sidebar">
      <div class="logo">
        <h2>AI智能合同审核</h2>
      </div>
      <el-menu
        :default-active="activeMenu"
        router
        class="sidebar-menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <span>仪表盘</span>
        </el-menu-item>
        <el-menu-item index="/contracts">
          <el-icon><Document /></el-icon>
          <span>合同管理</span>
        </el-menu-item>
        <el-menu-item index="/templates">
          <el-icon><Files /></el-icon>
          <span>模板库</span>
        </el-menu-item>
        <el-menu-item index="/reviews">
          <el-icon><Search /></el-icon>
          <span>合同审核</span>
        </el-menu-item>
        <el-menu-item index="/rules">
          <el-icon><Setting /></el-icon>
          <span>规则引擎</span>
        </el-menu-item>
        <el-menu-item index="/review-focus-config" v-if="userStore.user?.role === 'admin'">
          <el-icon><Edit /></el-icon>
          <span>审核重点配置</span>
        </el-menu-item>
        <el-menu-item index="/ai-model-config" v-if="userStore.user?.role === 'admin'">
          <el-icon><Cpu /></el-icon>
          <span>AI模型配置</span>
        </el-menu-item>
        <el-menu-item index="/ai-chat">
          <el-icon><ChatDotRound /></el-icon>
          <span>AI智能助手</span>
        </el-menu-item>
        <el-menu-item index="/rule-matches">
          <el-icon><List /></el-icon>
          <span>规则匹配记录</span>
        </el-menu-item>
        <el-menu-item index="/knowledge">
          <el-icon><Connection /></el-icon>
          <span>知识图谱</span>
        </el-menu-item>
        <el-menu-item index="/users" v-if="userStore.user?.role === 'admin'">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/departments" v-if="userStore.user?.role === 'admin'">
          <el-icon><OfficeBuilding /></el-icon>
          <span>部门管理</span>
        </el-menu-item>
        <el-menu-item index="/audit-logs" v-if="userStore.user?.role === 'admin'">
          <el-icon><DocumentCopy /></el-icon>
          <span>操作日志</span>
        </el-menu-item>
        <el-menu-item index="/permission-config" v-if="userStore.user?.role === 'admin'">
          <el-icon><Lock /></el-icon>
          <span>权限配置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h3>{{ pageTitle }}</h3>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand" trigger="click">
            <span class="user-info">
              <el-icon><User /></el-icon>
              {{ userStore.user?.real_name || userStore.user?.username || '用户' }}
              <el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">
                  <el-icon style="margin-right: 8px"><User /></el-icon>
                  个人中心
                </el-dropdown-item>
                <!-- 最近登录用户 -->
                <template v-if="recentUsersList && recentUsersList.length > 0">
                  <el-dropdown-item divided disabled>
                    <span style="color: #909399; font-size: 12px">最近登录</span>
                  </el-dropdown-item>
                  <el-dropdown-item
                    v-for="recentUser in recentUsersList"
                    :key="`recent-${recentUser.id}`"
                    :command="`switch:${recentUser.id}`"
                    class="recent-user-item"
                  >
                    <div style="display: flex; align-items: center; justify-content: space-between; width: 100%; min-width: 200px">
                      <div style="display: flex; align-items: center; flex: 1; min-width: 0">
                        <el-icon style="margin-right: 8px; color: #409EFF; flex-shrink: 0"><RefreshRight /></el-icon>
                        <div style="flex: 1; min-width: 0; overflow: hidden">
                          <div style="font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">
                            {{ recentUser.real_name || recentUser.username }}
                          </div>
                          <div style="font-size: 12px; color: #909399; white-space: nowrap; overflow: hidden; text-overflow: ellipsis">
                            {{ recentUser.email || recentUser.username }}
                          </div>
                        </div>
                      </div>
                      <el-icon
                        class="remove-icon"
                        @click.stop="handleRemoveRecentUser(recentUser.id)"
                        style="margin-left: 10px; color: #909399; flex-shrink: 0; cursor: pointer"
                      >
                        <Close />
                      </el-icon>
                    </div>
                  </el-dropdown-item>
                </template>
                <el-dropdown-item command="logout" divided>
                  <el-icon style="margin-right: 8px"><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
<<<<<<< HEAD
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, OfficeBuilding, DocumentCopy, Edit, Cpu, RefreshRight, Close, SwitchButton, Lock, ChatDotRound } from '@element-plus/icons-vue'
=======
import { ElMessage } from 'element-plus'
import { ArrowDown, OfficeBuilding, DocumentCopy, List } from '@element-plus/icons-vue'
>>>>>>> 38c605c8f8a4027af680fb54da514366df23a6ac

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 计算最近登录用户列表（排除当前用户）
const recentUsersList = computed(() => {
  if (!userStore.recentUsers) return []
  return userStore.recentUsers.filter(u => u.id !== userStore.user?.id)
})

const activeMenu = computed(() => route.path)
const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '仪表盘',
    '/contracts': '合同管理',
    '/templates': '模板库',
    '/reviews': '合同审核',
    '/rules': '规则引擎',
<<<<<<< HEAD
    '/review-focus-config': '审核重点配置',
    '/ai-model-config': 'AI模型配置',
=======
    '/rule-matches': '规则匹配记录',
>>>>>>> 38c605c8f8a4027af680fb54da514366df23a6ac
    '/knowledge': '知识图谱',
    '/users': '用户管理',
    '/departments': '部门管理',
    '/audit-logs': '操作日志',
  }
  return titles[route.path] || 'AI智能合同审核系统'
})

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        type: 'warning',
      })
      userStore.logout()
      router.push('/login')
      ElMessage.success('已退出登录')
    } catch (error) {
      // 用户取消
    }
  } else if (command === 'profile') {
    ElMessage.info('个人中心功能开发中')
  } else if (command.startsWith('switch:')) {
    const userId = parseInt(command.split(':')[1])
    const recentUser = userStore.recentUsers.find(u => u.id === userId)
    if (recentUser) {
      try {
        await userStore.switchUser(recentUser)
        ElMessage.success(`已切换到 ${recentUser.real_name || recentUser.username}`)
        // 刷新页面以更新权限相关的内容
        window.location.reload()
      } catch (error) {
        ElMessage.error('切换用户失败，请重新登录')
        router.push('/login')
      }
    }
  }
}

const handleRemoveRecentUser = (userId) => {
  userStore.removeRecentUserFromList(userId)
  ElMessage.success('已移除')
}

// 页面加载时，如果有token但没有用户信息，则获取用户信息
onMounted(async () => {
  if (userStore.token && !userStore.user) {
    await userStore.fetchUserInfo()
  }
  // 调试：检查最近登录用户
  console.log('最近登录用户:', userStore.recentUsers)
})
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.sidebar {
  background-color: #304156;
  color: #fff;
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #434a50;
}

.logo h2 {
  color: #fff;
  font-size: 18px;
  margin: 0;
}

.sidebar-menu {
  border: none;
  height: calc(100vh - 60px);
  overflow-y: auto;
}

.header {
  background-color: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}

.header-left h3 {
  margin: 0;
  font-size: 20px;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  cursor: pointer;
  color: #606266;
}

.user-info .el-icon {
  margin-right: 5px;
}

.main-content {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}

.recent-user-item {
  padding: 8px 20px;
  min-width: 200px;
}

.recent-user-item:hover {
  background-color: #f5f7fa;
}

.remove-icon {
  opacity: 0;
  transition: opacity 0.2s;
}

.recent-user-item:hover .remove-icon {
  opacity: 1;
}

.remove-icon:hover {
  color: #f56c6c !important;
}
</style>

