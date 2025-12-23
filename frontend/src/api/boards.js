import http from './http'

export const boardsApi = {
  listFree() {
    return http.get('/boards/free/')
  },
  detail(postId) {
    return http.get(`/boards/free/${postId}/`)
  },
  createFree(payload) {
    return http.post('/boards/free/', payload)
  },
  listComments(postId) {
    return http.get(`/boards/free/${postId}/comments/`)
  },
  createComment(postId, payload) {
    return http.post(`/boards/free/${postId}/comments/`, payload)
  },
  updateComment(commentId, payload) {
    return http.patch(`/boards/free/comments/${commentId}/`, payload)
  },
  deleteComment(commentId) {
    return http.delete(`/boards/free/comments/${commentId}/`)
  },
  recommend(postId) {
    return http.post(`/boards/free/${postId}/recommend/`)
  },
  listFriends() {
    return http.get('/boards/friends/')
  },
  createFriend(payload) {
    return http.post('/boards/friends/', payload)
  },
  getNearbyPosts(params) {
    return http.get('/boards/nearby/', { params })
  },
  getNearbyTheaters(params) {
    return http.get('/boards/theaters/', { params })
  },
  getMapConfig() {
    return http.get('/boards/map-config/')
  },
}
