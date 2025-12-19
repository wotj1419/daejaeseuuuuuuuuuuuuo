import http from './http'

export const authApi = {
  // 회원가입
  register(userData) {
    return http.post('/accounts/register/', userData)
  },

  // 로그인
  login(username, password) {
    return http.post('/accounts/login/', { username, password })
  },

  // 로그아웃
  logout(refreshToken) {
    return http.post('/accounts/logout/', { refresh: refreshToken })
  },

  // 사용자 정보 조회
  getProfile() {
    return http.get('/accounts/profile/')
  },

  // 사용자 정보 수정
  updateProfile(userData) {
    return http.put('/accounts/profile/update/', userData)
  },

  // 토큰 갱신
  refreshToken(refreshToken) {
    return http.post('/accounts/token/refresh/', { refresh: refreshToken })
  },
}

