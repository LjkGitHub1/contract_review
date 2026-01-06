import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/utils/api'

const RECENT_USERS_KEY = 'recent_users'
const MAX_RECENT_USERS = 5

// 获取最近登录用户列表
const getRecentUsers = () => {
  try {
    const stored = localStorage.getItem(RECENT_USERS_KEY)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error('获取最近登录用户失败:', error)
    return []
  }
}

// 保存最近登录用户
const saveRecentUser = (userInfo, token) => {
  try {
    let recentUsers = getRecentUsers()
    
    // 移除已存在的相同用户
    recentUsers = recentUsers.filter(u => u.id !== userInfo.id)
    
    // 添加到开头
    recentUsers.unshift({
      id: userInfo.id,
      username: userInfo.username,
      real_name: userInfo.real_name || userInfo.username,
      email: userInfo.email,
      role: userInfo.role,
      reviewer_level: userInfo.reviewer_level,
      token: token,
      loginTime: new Date().toISOString()
    })
    
    // 只保留最近5个
    recentUsers = recentUsers.slice(0, MAX_RECENT_USERS)
    
    localStorage.setItem(RECENT_USERS_KEY, JSON.stringify(recentUsers))
  } catch (error) {
    console.error('保存最近登录用户失败:', error)
  }
}

// 移除最近登录用户
const removeRecentUser = (userId) => {
  try {
    let recentUsers = getRecentUsers()
    recentUsers = recentUsers.filter(u => u.id !== userId)
    localStorage.setItem(RECENT_USERS_KEY, JSON.stringify(recentUsers))
  } catch (error) {
    console.error('移除最近登录用户失败:', error)
  }
}

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')
  const recentUsers = ref(getRecentUsers())

  const recentUsersList = computed(() => {
    // 排除当前用户
    return recentUsers.value.filter(u => u.id !== user.value?.id)
  })

  const login = async (username, password) => {
    try {
      const response = await api.post('/auth/login/', { username, password })
      token.value = response.data.access
      localStorage.setItem('token', token.value)
      await fetchUserInfo()
      
      // 保存到最近登录列表
      if (user.value) {
        saveRecentUser(user.value, token.value)
        recentUsers.value = getRecentUsers()
      }
      
      return response.data
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    user.value = null
    token.value = ''
    localStorage.removeItem('token')
  }

  const switchUser = async (userInfo) => {
    try {
      // 使用该用户的token登录
      token.value = userInfo.token
      localStorage.setItem('token', token.value)
      
      // 获取用户信息
      await fetchUserInfo()
      
      // 更新最近登录列表
      if (user.value) {
        saveRecentUser(user.value, token.value)
        recentUsers.value = getRecentUsers()
      }
      
      return true
    } catch (error) {
      console.error('切换用户失败:', error)
      // 如果token失效，从列表中移除
      removeRecentUser(userInfo.id)
      recentUsers.value = getRecentUsers()
      throw error
    }
  }

  const removeRecentUserFromList = (userId) => {
    removeRecentUser(userId)
    recentUsers.value = getRecentUsers()
  }

  const fetchUserInfo = async () => {
    try {
      const response = await api.get('/users/users/me/')
      user.value = response.data
      // 更新最近用户列表（排除当前用户）
      recentUsers.value = getRecentUsers()
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  // 初始化时刷新最近用户列表
  if (token.value) {
    recentUsers.value = getRecentUsers()
  }

  return {
    user,
    token,
    recentUsers: recentUsersList,
    login,
    logout,
    switchUser,
    removeRecentUserFromList,
    fetchUserInfo,
  }
})

