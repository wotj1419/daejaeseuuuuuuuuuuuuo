import http from './http'

export const accountsApi = {
  getProfile() {
    return http.get('/accounts/profile/')
  },
  updateProfile(payload) {
    return http.patch('/accounts/profile/', payload)
  },
}
