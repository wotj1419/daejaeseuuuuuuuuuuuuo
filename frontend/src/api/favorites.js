import http from "./http"

export const favoritesApi = {
  toggleFavorite(movieId) {
    return http.post(`/accounts/favorites/${movieId}/toggle/`)
  },

  checkFavoriteStatus(movieId) {
    return http.get(`/accounts/favorites/${movieId}/status/`)
  },

  getMyMovies() {
    return http.get('/accounts/my-movies/')
  },

  getMyReviews() {
    return http.get('/accounts/my-reviews/')
  },

  getSimilarUsers(params = {}) {
    return http.get('/accounts/favorites/similar-users/', { params })
  },

  getUserFavorites(username) {
    return http.get(`/accounts/users/${encodeURIComponent(username)}/favorites/`)
  },
}
