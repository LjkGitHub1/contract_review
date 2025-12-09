import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || '')

  const login = async (username, password) => {
    try {
      const response = await api.post('/auth/login/', { username, password })
      token.value = response.data.access
      localStorage.setItem('token', token.value)
      await fetchUserInfo()
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

  const fetchUserInfo = async () => {
    try {
      const response = await api.get('/users/users/me/')
      user.value = response.data
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  return {
    user,
    token,
    login,
    logout,
    fetchUserInfo,
  }
})

