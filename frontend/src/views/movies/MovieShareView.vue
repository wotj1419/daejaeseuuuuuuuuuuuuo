<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { favoritesApi } from '@/api/favorites'
import { moviesApi } from '@/api/movies'
import { accountsApi } from '@/api/accounts'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const searchUsername = ref(route.query.username || '')
const favorites = ref([])
const loading = ref(false)
const error = ref('')
const infoMessage = ref('')
const userProfile = ref(null)
const lifeMovie = ref(null)
const lifeMovieLoading = ref(false)
const lifeMovieError = ref('')
const followLoading = ref(false)
const isFollowing = ref(false)

function posterUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w500${path}`
}

function goToMovieDetail(tmdbId) {
  router.push({ name: 'movieDetail', params: { movieId: tmdbId } })
}

async function loadLifeMovie(name) {
  if (!name?.trim()) {
    lifeMovie.value = null
    lifeMovieError.value = ''
    return
  }

  lifeMovieLoading.value = true
  lifeMovieError.value = ''

  try {
    const { data } = await moviesApi.search(name.trim())
    const movie = (data.results || [])[0]
    if (movie) {
      lifeMovie.value = {
        ...movie,
        tmdb_id: movie.tmdb_id || movie.id,
      }
      lifeMovieError.value = ''
    } else {
      lifeMovie.value = null
      lifeMovieError.value = '인생 영화 정보를 찾을 수 없습니다.'
    }
  } catch (err) {
    console.error('인생 영화 검색 오류:', err)
    lifeMovie.value = null
    lifeMovieError.value = '인생 영화 정보를 불러오는 중 오류가 발생했습니다.'
  } finally {
    lifeMovieLoading.value = false
  }
}

async function searchFavorites({ updateQuery = true } = {}) {
  const username = searchUsername.value.trim()
  if (!username) {
    error.value = '사용자 아이디를 입력해 주세요.'
    favorites.value = []
    infoMessage.value = ''
    return
  }

  if (updateQuery) {
    router.replace({ query: { username } })
  }

  loading.value = true
  error.value = ''
  infoMessage.value = ''
  favorites.value = []
  lifeMovie.value = null
  lifeMovieError.value = ''
  userProfile.value = null
  isFollowing.value = false

  try {
    const { data } = await favoritesApi.getUserFavorites(username)
    userProfile.value = data.profile || null
    const movieList = Array.isArray(data.movies) ? data.movies : []
    favorites.value = movieList
    if (!movieList.length) {
      infoMessage.value = '좋아요한 영화가 아직 없습니다.'
    } else {
      infoMessage.value = ''
    }
    await loadLifeMovie(userProfile.value?.favorite_movie_name)
    await fetchFollowState()
  } catch (err) {
    console.error('유저 좋아요 목록 조회 실패:', err)
    if (err.response?.status === 404) {
      error.value = '해당 사용자를 찾을 수 없습니다.'
    } else {
      error.value = '좋아요한 영화 목록을 불러오는 중 오류가 발생했습니다.'
    }
    userProfile.value = null
    favorites.value = []
    infoMessage.value = ''
    lifeMovie.value = null
    lifeMovieError.value = ''
  } finally {
    loading.value = false
  }
}

async function fetchFollowState() {
  if (!isAuthenticated.value) return
  if (!userProfile.value?.username) return
  if (authStore.user?.username === userProfile.value.username) return
  try {
    const { data } = await accountsApi.getUsers()
    const target = data.find((u) => u.username === userProfile.value.username)
    isFollowing.value = !!target?.is_following
  } catch (err) {
    console.error('팔로우 상태 조회 실패', err)
  }
}

async function toggleFollow() {
  if (!userProfile.value?.username) return
  if (!isAuthenticated.value) {
    router.push({ name: 'login' })
    return
  }
  if (authStore.user?.username === userProfile.value.username) return
  followLoading.value = true
  try {
    await accountsApi.toggleFollow(userProfile.value.username)
    isFollowing.value = !isFollowing.value
  } catch (err) {
    console.error('팔로우 토글 실패', err)
    alert(err.response?.data?.error || '팔로우 처리 중 문제가 발생했습니다.')
  } finally {
    followLoading.value = false
  }
}

onMounted(() => {
  if (searchUsername.value) {
    searchFavorites({ updateQuery: false })
  }
})
</script>

<template>
  <div class="share-page">
    <section class="share-intro">
      <div>
        <h1>프로필 공유</h1>
        <p>관심 있는 유저의 좋아요 목록을 확인하고, 함께 감상할 영화를 발견해보세요.</p>
      </div>
      <div class="share-search">
        <input
          v-model="searchUsername"
          @keyup.enter="searchFavorites"
          placeholder="예) movielover123"
        />
        <button @click="searchFavorites" :disabled="loading">
          {{ loading ? '조회 중…' : '검색' }}
        </button>
      </div>
    </section>

    <div v-if="userProfile" class="share-profile">
      <div class="life-header">
        <div>
          <h2>{{ userProfile.username }}님의 인생 영화</h2>
          <p class="life-movie">
            {{ userProfile.favorite_movie_name || '등록된 인생 영화가 없습니다.' }}
          </p>
        </div>
        <button
          v-if="authStore.user?.username !== userProfile.username"
          class="follow-btn"
          :class="{ active: isFollowing }"
          :disabled="followLoading"
          @click="toggleFollow"
        >
          <span v-if="followLoading">처리 중...</span>
          <span v-else>{{ isFollowing ? '팔로우 취소' : '팔로우' }}</span>
        </button>
      </div>

      <div v-if="lifeMovie" class="life-movie-card" @click="goToMovieDetail(lifeMovie.tmdb_id)">
        <div class="life-movie-poster">
          <img v-if="lifeMovie.poster_path" :src="posterUrl(lifeMovie.poster_path)" alt="life movie poster" />
          <div v-else class="life-movie-noimg">No Image</div>
        </div>
        <div class="life-movie-details">
          <h3>{{ lifeMovie.title }}</h3>
          <p>{{ lifeMovie.overview }}</p>
        </div>
      </div>

      <div v-else-if="lifeMovieLoading" class="life-movie-placeholder">
        인생 영화 정보를 불러오는 중입니다…
      </div>

      <div v-else-if="userProfile.favorite_movie_name" class="life-movie-placeholder">
        {{ lifeMovieError || '등록된 인생 영화 정보를 찾을 수 없습니다.' }}
      </div>

      <p v-if="userProfile.bio" class="profile-bio">{{ userProfile.bio }}</p>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="infoMessage" class="info-message">{{ infoMessage }}</div>

    <div v-if="loading" class="loading-row">
      <span>좋아요한 영화 목록을 불러오는 중입니다…</span>
    </div>

    <section v-if="favorites.length" class="movies-section">
      <div class="movies-section-header">
        <div>
          <p class="section-label">영화 목록</p>
          <h3 class="section-title">{{ userProfile?.username || '사용자' }}가 좋아한 영화</h3>
        </div>
      </div>
      <div class="movies-grid">
        <div
          v-for="movie in favorites"
          :key="movie.tmdb_id"
          class="movie-card"
          @click="goToMovieDetail(movie.tmdb_id)"
        >
          <div class="poster">
            <img v-if="movie.poster_path" :src="posterUrl(movie.poster_path)" alt="poster" />
            <div v-else class="noimg">No Image</div>
          </div>
          <div class="movie-info">
            <div class="title">{{ movie.title }}</div>
            <div class="meta">
              <span>★ {{ movie.vote_average?.toFixed(1) || '-' }}</span>
              <span>{{ movie.release_date?.substring(0, 4) || '-' }}</span>
            </div>
            <p v-if="movie.ai_reason" class="reason">「{{ movie.ai_reason }}」</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.share-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 120px 40px 80px;
  color: #fff;
}

.share-intro {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 40px;
}

.share-intro h1 {
  font-size: 2.4rem;
  font-weight: 800;
}

.share-intro p {
  color: #bbb;
  max-width: 540px;
}

.share-profile {
  margin-bottom: 20px;
  padding: 20px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.12);
}

.share-profile h2 {
  font-size: 1.6rem;
  margin-bottom: 6px;
}

.life-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.life-movie {
  font-size: 1.2rem;
  font-weight: 700;
  color: #4f9171;
  margin: 0 0 6px;
}

.profile-bio {
  color: #ccc;
  margin: 0;
}

.life-movie-card {
  margin-top: 16px;
  display: flex;
  gap: 16px;
  cursor: pointer;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.life-movie-card:hover {
  transform: translateY(-4px);
  border-color: #4f9171;
}

.life-movie-poster {
  width: 110px;
  min-width: 110px;
  aspect-ratio: 2 / 3;
  overflow: hidden;
  border-radius: 12px;
  background: #222;
}

.life-movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.life-movie-noimg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #777;
  font-size: 0.85rem;
}

.life-movie-details {
  flex: 1;
}

.life-movie-details h3 {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 700;
  color: #fff;
}

.life-movie-details p {
  margin: 0;
  color: #ccc;
  line-height: 1.4;
  max-height: 60px;
  overflow: hidden;
}

.life-movie-placeholder {
  margin-top: 14px;
  color: #bbb;
  font-size: 0.95rem;
}

.share-search {
  display: flex;
  gap: 12px;
}

.movies-section {
  margin-top: 40px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.movies-section-header {
  margin-bottom: 24px;
}

.section-label {
  font-size: 14px;
  letter-spacing: 0.2em;
  color: #aaa;
  text-transform: uppercase;
}

.section-title {
  font-size: 26px;
  font-weight: 700;
  margin: 6px 0 0;
  color: #fff;
}

.share-search input {
  padding: 14px 18px;
  border-radius: 999px;
  border: 1px solid #555;
  background-color: rgba(255, 255, 255, 0.04);
  color: #fff;
  min-width: 280px;
}

.share-search button {
  border: none;
  border-radius: 999px;
  padding: 0 32px;
  background: #37664b;
  color: #f6f6f6;
  font-weight: 700;
  cursor: pointer;
}

.share-search button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message,
.info-message {
  color: #ff6b6b;
  text-align: center;
  margin-bottom: 20px;
}

.info-message {
  color: #bbb;
}

.loading-row {
  text-align: center;
  color: #ccc;
  margin-bottom: 20px;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}

.movie-card {
  background: #151515;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid #222;
}

.movie-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
  border-color: #4f9171;
}

.poster {
  aspect-ratio: 2 / 3;
  background: #222;
  overflow: hidden;
}

.poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.noimg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.movie-info {
  padding: 16px;
}

.title {
  font-weight: 700;
  margin-bottom: 10px;
}

.meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #999;
  margin-bottom: 10px;
}

.reason {
  font-size: 0.85rem;
  color: #9ed3b4;
}

.follow-btn {
  min-width: 120px;
  padding: 10px 18px;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: #2d4d3a;
  color: #f1f1f1;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.follow-btn.active {
  background: #4f9171;
  border-color: #4f9171;
  color: #06110c;
}

.follow-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .share-page {
    padding: 100px 20px 60px;
  }

  .share-intro {
    justify-content: flex-start;
  }

  .share-search input {
    flex: 1;
    min-width: 0;
  }
}
</style>
