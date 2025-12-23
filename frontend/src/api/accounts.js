import http from './http'

export const accountsApi = {
  getProfile() {
    return http.get('/accounts/profile/')
  },
  getProfileSummary() {
    return http.get('/accounts/profile/summary/')
  },
  updateProfile(payload) {
    return http.patch('/accounts/profile/', payload)
  },
  getFollowers() {
    return http.get('/accounts/followers/')
  },
  getFollowings() {
    return http.get('/accounts/followings/')
  },
  getUsers() {
    return http.get('/accounts/users/')
  },
  toggleFollow(username) {
    return http.post(`/accounts/follow/${encodeURIComponent(username)}/toggle/`)
  },
  getMyTaste() {
    return http.get('/accounts/me/taste/')
  },
  getSimilarUsers(params = {}) {
    return http.get('/accounts/me/similar-users/', { params })
  },
  getLocation() {
    return http.get('/accounts/my-location/')
  },
  updateLocation(payload) {
    return http.patch('/accounts/my-location/', payload)
  },
  // Backwards compatibility for legacy friend routes in components that haven't been renamed yet.
  getFriends() {
    return http.get('/accounts/followings/')
  },
  toggleFriend(username) {
    return http.post(`/accounts/follow/${encodeURIComponent(username)}/toggle/`)
  },
}
