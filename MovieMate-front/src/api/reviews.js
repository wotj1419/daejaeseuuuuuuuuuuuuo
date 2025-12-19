import http from './http'

export const reviewsApi = {
  listByMovie(movieId) {
    return http.get(`/movies/${movieId}/reviews/`)
  },
  createByMovie(movieId, payload) {
    // payload: { content, rating }
    return http.post(`/movies/${movieId}/reviews/`, payload)
  },
  detail(reviewId) {
    return http.get(`/reviews/${reviewId}/`)
  },
  update(reviewId, payload) {
    return http.put(`/reviews/${reviewId}/`, payload)
  },
  remove(reviewId) {
    return http.delete(`/reviews/${reviewId}/`)
  },
}
