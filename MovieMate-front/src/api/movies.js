import http from './http'

export const moviesApi = {
  // ✅ 너 백엔드에 영화목록 API가 있다면 이걸 사용
  list(params = {}) {
    return http.get('/movies/', { params })
  },

  // (있으면 사용) 영화 상세
  detail(movieId) {
    return http.get(`/movies/${movieId}/`)
  },

  // 이미 있던 추천
  recommend(movieId) {
    return http.get(`/movies/${movieId}/recommend/`)
  },

  // 검색 API
  search(query) {
    return http.get('/movies/search/', { params: { q: query } })
  },

  // 예고편 API
  trailer(movieId) {
    return http.get(`/movies/${movieId}/trailer/`)
  },
}
