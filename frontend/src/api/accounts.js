import http from './http'

export const accountsApi = {
  getProfile() {
    return http.get('/accounts/profile/')
  },
  updateProfile(payload) {
    return http.patch('/accounts/profile/', payload)
  },
  getFriends() {
    return http.get('/accounts/friends/')
  },
  getUsers() {
    return http.get('/accounts/users/')
  },
  toggleFriend(username) {
    return http.post(`/accounts/friends/${username}/toggle/`)
  },
}
