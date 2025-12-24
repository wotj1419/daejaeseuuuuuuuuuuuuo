import http from './http'

export const moviesApi = {
  // AI 영화 추천
  aiRecommend(query, limit = 10) {
    return http.post('/movies/ai-recommend/', { query, limit })
  },

  // 영화 목록
  list(params = {}) {
    return http.get('/movies/', { params })
  },

  // 영화 상세
  detail(movieId) {
    return http.get(`/movies/${movieId}/`)
  },

  // 비슷한 영화 추천
  recommend(movieId) {
    return http.get(`/movies/${movieId}/recommend/`)
  },

  // 검색
  search(query) {
    return http.get('/movies/search/', { params: { q: query } })
  },

  // 예고편
  trailer(movieId) {
    return http.get(`/movies/${movieId}/trailer/`)
  },

  // 출연진
  credits(movieId) {
    return http.get(`/movies/${movieId}/credits/`)
  },

  // 인물 상세
  personDetail(personId) {
    return http.get(`/person/${personId}/`)
  },

  // 장르 목록
  genreList() {
    return http.get('/genres/')
  },
}
