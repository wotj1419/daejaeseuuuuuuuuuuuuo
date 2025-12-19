import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)

  // 로컬 스토리지에서 초기 상태 복원
  const initAuth = () => {
    const storedUser = localStorage.getItem('user')
    const accessToken = localStorage.getItem('access_token')
    
    if (storedUser && accessToken) {
      try {
        user.value = JSON.parse(storedUser)
      } catch (e) {
        console.error('사용자 정보 파싱 오류:', e)
        clearAuth()
      }
    }
  }

  // 인증 상태 확인
  const isAuthenticated = computed(() => !!user.value)

  // 로그인
  const login = async (username, password) => {
    loading.value = true
    error.value = null
    
    try {
      const { data } = await authApi.login(username, password)
      
      // 토큰 저장
      localStorage.setItem('access_token', data.tokens.access)
      localStorage.setItem('refresh_token', data.tokens.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      user.value = data.user
      return { success: true, message: data.message }
    } catch (err) {
      const errorMessage = err.response?.data?.error || '로그인에 실패했습니다.'
      error.value = errorMessage
      return { success: false, message: errorMessage }
    } finally {
      loading.value = false
    }
  }

  // 회원가입
  const register = async (userData) => {
    loading.value = true
    error.value = null
    
    try {
      const { data } = await authApi.register(userData)
      
      // 토큰 저장
      localStorage.setItem('access_token', data.tokens.access)
      localStorage.setItem('refresh_token', data.tokens.refresh)
      localStorage.setItem('user', JSON.stringify(data.user))
      
      user.value = data.user
      return { success: true, message: data.message }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.response?.data?.password?.[0] || '회원가입에 실패했습니다.'
      error.value = errorMessage
      return { success: false, message: errorMessage }
    } finally {
      loading.value = false
    }
  }

  // 로그아웃
  const logout = async () => {
    loading.value = true
    error.value = null
    
    try {
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        await authApi.logout(refreshToken)
      }
    } catch (err) {
      console.error('로그아웃 오류:', err)
    } finally {
      clearAuth()
      loading.value = false
    }
  }

  // 인증 정보 초기화
  const clearAuth = () => {
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  // 사용자 정보 조회
  const fetchProfile = async () => {
    loading.value = true
    error.value = null
    
    try {
      const { data } = await authApi.getProfile()
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
      return data
    } catch (err) {
      error.value = '사용자 정보를 불러오지 못했습니다.'
      throw err
    } finally {
      loading.value = false
    }
  }

  // 사용자 정보 수정
  const updateProfile = async (userData) => {
    loading.value = true
    error.value = null
    
    try {
      const { data } = await authApi.updateProfile(userData)
      user.value = data
      localStorage.setItem('user', JSON.stringify(data))
      return { success: true, data }
    } catch (err) {
      const errorMessage = err.response?.data?.error || '정보 수정에 실패했습니다.'
      error.value = errorMessage
      return { success: false, message: errorMessage }
    } finally {
      loading.value = false
    }
  }

  // 초기화
  initAuth()

  return {
    user,
    loading,
    error,
    isAuthenticated,
    login,
    register,
    logout,
    fetchProfile,
    updateProfile,
    clearAuth,
  }
})

