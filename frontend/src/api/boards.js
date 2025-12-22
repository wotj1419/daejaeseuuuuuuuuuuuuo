import http from './http'

export const boardsApi = {
  listFree() {
    return http.get('/boards/free/')
  },
  createFree(payload) {
    return http.post('/boards/free/', payload)
  },
  listFriends() {
    return http.get('/boards/friends/')
  },
  createFriend(payload) {
    return http.post('/boards/friends/', payload)
  },
}
