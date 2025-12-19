import axios from 'axios'

const http = axios.create({
  baseURL: `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}/api`,
  timeout: 10000,
})

// 요청 인터셉터: 토큰 추가
http.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, (error) => {
  return Promise.reject(error)
})

// 응답 인터셉터: 토큰 만료 시 처리
http.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    // 401 에러이고, 아직 재시도하지 않은 경우
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          const response = await http.post('/accounts/token/refresh/', {
            refresh: refreshToken
          })
          const { access } = response.data
          localStorage.setItem('access_token', access)
          originalRequest.headers.Authorization = `Bearer ${access}`
          return http(originalRequest)
        }
      } catch (refreshError) {
        // 리프레시 토큰도 만료된 경우 로그아웃 처리
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default http
