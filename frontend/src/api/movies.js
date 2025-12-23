import http from './http'

export const moviesApi = {
  // AI 영화 추천
  aiRecommend(query, limit = 10) {
    return http.post('/movies/ai-recommend/', { query, limit })
  },

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

  // 출연진 API
  credits(movieId) {
    return http.get(`/movies/${movieId}/credits/`)
  },

  // 인물 상세 API
  personDetail(personId) {
    return http.get(`/person/${personId}/`)
  },

  // 장르 목록 API
  genreList() {
    return http.get('/genres/')
  },

  // 인트로 영상 생성 API
  introVideo(data = {}) {
    return http.post('/intro-video/', data)
  },
}
