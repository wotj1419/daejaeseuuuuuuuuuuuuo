<script setup>
import { ref, onMounted, computed, watch } from 'vue'
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
const similarUsers = ref([])
const similarLoading = ref(false)
const similarError = ref('')
const similarInfo = ref('')

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
    console.error('인생 영화 검색 실패:', err)
    lifeMovie.value = null
    lifeMovieError.value = '인생 영화 정보를 불러오는 중 문제가 발생했습니다.'
  } finally {
    lifeMovieLoading.value = false
  }
}

async function searchFavorites({ updateQuery = true } = {}) {
  const username = searchUsername.value.trim()
  if (!username) {
    error.value = '사용자 이름을 입력해주세요'
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
    console.error('타인 좋아요 목록 조회 실패:', err)
    if (err.response?.status === 404) {
      error.value = '해당 사용자를 찾을 수 없습니다.'
    } else {
      error.value = '좋아요한 영화 목록을 불러오는 중 문제가 발생했습니다.'
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

async function loadSimilarUsers() {
  if (!isAuthenticated.value) {
    similarUsers.value = []
    similarInfo.value = ''
    similarError.value = ''
    return
  }

  similarLoading.value = true
  similarError.value = ''
  similarInfo.value = ''
  try {
    const { data } = await favoritesApi.getSimilarUsers()
    similarUsers.value = data.results || []
    if (!similarUsers.value.length) {
      similarInfo.value = '내가 좋아하는 장르와 비슷한 사용자가 아직 없습니다.'
    }
  } catch (err) {
    console.error('좋아요 사용자 추천 불러오기 오류:', err)
    similarError.value = '비슷한 취향 프로필을 불러오는 중 문제가 발생했습니다.'
    similarUsers.value = []
  } finally {
    similarLoading.value = false
  }
}

function selectSimilarUser(user) {
  if (!user?.username) return
  searchUsername.value = user.username
  searchFavorites()
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

function formatSummary(user) {
  const genres = Array.isArray(user.top_genres) ? user.top_genres.filter(Boolean) : []
  const titles = Array.isArray(user.sample_titles) ? user.sample_titles.filter(Boolean) : []
  const parts = []
  if (genres.length) {
    parts.push(`주요 장르: ${genres.join(', ')}`)
  }
  if (titles.length) {
    parts.push(`대표작: ${titles.join(', ')}`)
  }
  if (!parts.length && user.summary) {
    return user.summary
  }
  if (!parts.length) {
    return '요약 정보가 없습니다.'
  }
  return parts.join('\n')
}

onMounted(() => {
  if (searchUsername.value) {
    searchFavorites({ updateQuery: false })
  }
  loadSimilarUsers()
})

watch(isAuthenticated, (authed) => {
  if (authed) {
    loadSimilarUsers()
  } else {
    similarUsers.value = []
    similarError.value = ''
    similarInfo.value = ''
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
        <div class="search-avatar" v-if="userProfile?.profile_image">
          <img :src="userProfile.profile_image" alt="profile" />
        </div>
        <input
          v-model="searchUsername"
          @keyup.enter="searchFavorites"
          placeholder="예) movielover123"
        />
        <button @click="searchFavorites" :disabled="loading">
          {{ loading ? '검색 중...' : '검색' }}
        </button>
      </div>
    </section>

    <section class="similar-section">
      <div class="similar-header">
        <p class="section-label">취향 공유</p>
        <h3 class="section-title">나와 비슷한 좋아요 장르의 유저가 있어요.</h3>
        <p class="similar-sub">좋아요 목록의 장르와 대표작을 계산해 선별했어요.</p>
      </div>

      <div v-if="!isAuthenticated" class="similar-gate">
        <p>로그인하면 비슷한 장르를 가진 사용자 추천을 보여드릴게요.</p>
        <button @click="router.push({ name: 'login' })">로그인</button>
      </div>

      <div v-else>
        <div v-if="similarLoading" class="similar-loading">불러오는 중...</div>
        <div v-else-if="similarError" class="error-message">{{ similarError }}</div>
        <div v-else-if="similarInfo" class="info-message">{{ similarInfo }}</div>
        <div v-else class="similar-row">
          <article
            v-for="u in similarUsers"
            :key="u.username"
            class="similar-card"
            @click="selectSimilarUser(u)"
          >
            <div class="card-top">
              <div class="profile-chip" v-if="u.profile_image">
                <img :src="u.profile_image" alt="profile" />
              </div>
              <div class="profile-chip placeholder" v-else>
                {{ u.username?.charAt(0).toUpperCase() || 'U' }}
              </div>
              <div>
                <h4>{{ u.username }}</h4>
                <p class="mini-text">{{ u.favorite_movie_name || '좋아하는 영화 정보가 없어요.' }}</p>
              </div>
            </div>
            <p class="summary">{{ formatSummary(u) }}</p>
            <div class="sample-list">
              <span class="sample-label">대표작</span>
              <span
                v-for="title in (u.sample_titles || [])"
                :key="title"
                class="sample-pill"
              >
                🎬 {{ title }}
              </span>
              <span v-if="!u.sample_titles?.length" class="sample-pill muted">정보 없음</span>
            </div>
            <p class="mini-text" v-if="u.bio">{{ u.bio }}</p>
          </article>
        </div>
      </div>
    </section>

    <div v-if="userProfile" class="share-profile">
      <div class="life-header">
        <div class="life-user">
          <div class="profile-chip" v-if="userProfile.profile_image">
            <img :src="userProfile.profile_image" alt="profile" />
          </div>
          <div class="profile-chip placeholder" v-else>
            {{ userProfile.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <div>
            <h2>{{ userProfile.username }}님의 인생 영화</h2>
            <p class="life-movie">
              {{ userProfile.favorite_movie_name || '등록된 인생 영화가 없습니다.' }}
            </p>
          </div>
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
            <p v-if="movie.ai_reason" class="reason">{{ movie.ai_reason }}</p>
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

.life-user {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-chip {
  width: 46px;
  height: 46px;
  border-radius: 50%;
  overflow: hidden;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: linear-gradient(135deg, #1db954, #1ed760);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #000;
}

.profile-chip img {
  width: 100%;
  height: 100%;
  object-fit: cover;
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
  align-items: center;
}

.search-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: linear-gradient(135deg, #1db954, #1ed760);
  flex-shrink: 0;
}

.search-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.movies-section {
  margin-top: 40px;
  padding: 30px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 30px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.similar-section {
  margin-top: 50px;
  margin-bottom: 32px;
  padding: 26px;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 24px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.similar-header {
  margin-bottom: 16px;
}

.similar-sub {
  color: #8fa799;
  margin: 6px 0 0;
}

.similar-gate {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed rgba(255, 255, 255, 0.15);
  border-radius: 14px;
  padding: 14px 16px;
}

.similar-gate button {
  border: none;
  border-radius: 12px;
  padding: 10px 16px;
  background: #2d4d3a;
  color: #f6f6f6;
  font-weight: 700;
  cursor: pointer;
}

.similar-loading {
  color: #9ed3b4;
}

.similar-row {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-bottom: 6px;
}

.similar-card {
  width: 100%;
  padding: 16px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  min-height: 140px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.similar-card:hover {
  border-color: #4f9171;
  transform: translateY(-3px);
}

.card-top {
  display: flex;
  align-items: center;
  gap: 10px;
}

.summary {
  color: #cde6d6;
  margin: 0;
  line-height: 1.4;
  white-space: pre-line;
  word-break: keep-all;
}

.mini-text {
  color: #9aa7a0;
  margin: 0;
  font-size: 0.9rem;
}

.sample-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.sample-label {
  font-size: 0.85rem;
  color: #9aa7a0;
}

.sample-pill {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.08);
  color: #e6f5ec;
  font-size: 0.9rem;
}

.sample-pill.muted {
  color: #8b9992;
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
  border-radius: 12px;
  padding: 12px 18px;
  min-width: 76px;
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
