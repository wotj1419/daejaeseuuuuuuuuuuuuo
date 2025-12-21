import http from './http'

export const favoritesApi = {
  // 영화 좋아요 토글
  toggleFavorite(movieId) {
    return http.post(`/accounts/favorites/${movieId}/toggle/`)
  },

  // 좋아요 상태 확인
  checkFavoriteStatus(movieId) {
    return http.get(`/accounts/favorites/${movieId}/status/`)
  },

  // 내가 좋아요한 영화 목록
  getMyMovies() {
    return http.get('/accounts/my-movies/')
  },

  // 내가 작성한 리뷰 목록
  getMyReviews() {
    return http.get('/accounts/my-reviews/')
  },
}
