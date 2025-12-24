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
  updatePost(id, payload) {
    return http.patch(`/boards/free/${id}/`, payload)
  },
  deletePost(id) {
    return http.delete(`/boards/free/${id}/`)
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

    getMyPosts() {
    return http.get('/boards/my-posts/')
  },

  getShowtimes(params) {
    return http.get('/boards/theaters/showtimes/', { params })
  },
}

