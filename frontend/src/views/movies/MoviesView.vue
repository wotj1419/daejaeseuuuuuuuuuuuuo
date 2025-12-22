<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { moviesApi } from '@/api/movies'
import { favoritesApi } from '@/api/favorites'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const error = ref(null)
const allMovies = ref([])
const favoriteStatus = ref(new Map()) // tmdb_id -> boolean

const q = ref('')

// TMDB poster_path가 상대경로일 때 보정
function posterUrl(poster_path) {
  if (!poster_path) return ''
  if (poster_path.startsWith('http')) return poster_path
  return `https://image.tmdb.org/t/p/w500${poster_path}`
}

const movies = computed(() => {
  const query = q.value.trim().toLowerCase()
  if (!query) return allMovies.value

  return allMovies.value.filter((m) => {
    const title = (m.title || '').toLowerCase()
    const overview = (m.overview || '').toLowerCase()
    return title.includes(query) || overview.includes(query)
  })
})

async function loadMovies() {
  loading.value = true
  error.value = null
  try {
    // ✅ 백엔드 영화목록 API 호출
    const { data } = await moviesApi.list()

    // DRF pagination 쓰는 경우 { results: [...] } 형태일 수 있어서 둘 다 처리
    allMovies.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    console.error(e)
    error.value = '영화 목록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

function goToMovieDetail(tmdbId) {
  router.push({ name: 'movieDetail', params: { movieId: tmdbId } })
}

// 좋아요 토글
async function toggleFavorite(event, movieTmdbId) {
  event.stopPropagation() // 영화 카드 클릭 방지
  
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    router.push({ name: 'login' })
    return
  }

  try {
    const { data } = await favoritesApi.toggleFavorite(movieTmdbId)
    // 좋아요 상태 업데이트
    favoriteStatus.value.set(movieTmdbId, data.is_favorited)
  } catch (e) {
    console.error('좋아요 토글 실패:', e)
    alert('좋아요 처리 중 오류가 발생했습니다.')
  }
}

// 좋아요 상태 로드
async function loadFavoriteStatuses() {
  if (!authStore.isAuthenticated) return

  try {
    const { data } = await favoritesApi.getMyMovies()
    const favoriteIds = new Set(data.map(m => m.tmdb_id))
    
    // 현재 표시된 영화들의 좋아요 상태 설정
    allMovies.value.forEach(movie => {
      favoriteStatus.value.set(movie.tmdb_id, favoriteIds.has(movie.tmdb_id))
    })
  } catch (e) {
    console.error('좋아요 상태 로드 실패:', e)
  }
}

onMounted(async () => {
  await loadMovies()
  await loadFavoriteStatuses()
})
</script>

<template>
  <div class="movies-container">
    <!-- Header Section -->
    <section class="header-section">
      <div class="header-content">
        <h1 class="page-title">영화 목록</h1>
        <p class="page-subtitle">검색 가능한 모든 영화를 둘러보세요</p>
        
        <div class="search-bar">
          <input 
            v-model="q" 
            placeholder="영화 제목이나 줄거리로 검색하세요..." 
            class="search-input"
          />
          <button @click="loadMovies" class="refresh-button">
            <span>⟳</span> 새로고침
          </button>
        </div>
        
        <div class="movie-count">
          <span class="count-badge">{{ movies.length }}</span>개의 영화
        </div>
      </div>
    </section>

    <!-- Loading State -->
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>영화 목록을 불러오는 중...</p>
    </div>

    <!-- Error State -->
    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- Movies Grid -->
    <section v-if="!loading && movies.length > 0" class="movies-section">
      <div class="movies-grid">
        <div 
          v-for="m in movies" 
          :key="m.id" 
          class="movie-card"
          @click="goToMovieDetail(m.tmdb_id)"
        >
          <div class="poster">
            <img v-if="m.poster_path" :src="posterUrl(m.poster_path)" alt="poster" />
            <div v-else class="noimg">No Image</div>
            
            <!-- 좋아요 버튼 -->
            <button 
              v-if="authStore.isAuthenticated"
              class="favorite-btn"
              :class="{ 'is-favorited': favoriteStatus.get(m.tmdb_id) }"
              @click="toggleFavorite($event, m.tmdb_id)"
            >
              {{ favoriteStatus.get(m.tmdb_id) ? '⭐' : '☆' }}
            </button>
            
            <div class="card-overlay">
              <div class="play-button">▶</div>
            </div>
          </div>

          <div class="movie-info">
            <div class="title">{{ m.title }}</div>
            <div class="meta">
              <span>⭐ {{ m.vote_average ?? '-' }}</span>
              <span>🔥 {{ m.popularity?.toFixed(0) ?? '-' }}</span>
            </div>
            <p class="overview" v-if="m.overview">{{ m.overview }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Empty State -->
    <div v-else-if="!loading && !error" class="empty-state">
      <div class="empty-icon">🎬</div>
      <p>영화 데이터가 없습니다.</p>
    </div>
  </div>
</template>

<style scoped>
.movies-container {
  width: 100%;
  min-height: 100vh;
  background-color: #000000;
  padding-bottom: 60px;
}

/* Header Section */
.header-section {
  padding: 60px 50px 40px;
  background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%);
  border-bottom: 1px solid #222;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
}

.page-title {
  font-size: 48px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 12px;
  text-align: center;
}

.page-subtitle {
  font-size: 18px;
  color: #888;
  margin-bottom: 40px;
  text-align: center;
}

/* Search Bar */
.search-bar {
  display: flex;
  gap: 12px;
  max-width: 700px;
  margin: 0 auto 24px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  flex: 1;
  min-width: 280px;
  padding: 16px 24px;
  background-color: rgba(255, 255, 255, 0.1);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  font-size: 16px;
  color: #ffffff;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-input:focus {
  outline: none;
  border-color: #1DB954;
  background-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 0 20px rgba(29, 185, 84, 0.3);
}

.refresh-button {
  padding: 16px 28px;
  background-color: #1DB954;
  color: #000000;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  box-shadow: 0 4px 20px rgba(29, 185, 84, 0.4);
}

.refresh-button span {
  font-size: 20px;
  display: inline-block;
}

.refresh-button:hover {
  background-color: #169B43;
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(29, 185, 84, 0.6);
}

.refresh-button:active span {
  animation: rotate 0.6s ease-in-out;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Movie Count */
.movie-count {
  text-align: center;
  color: #888;
  font-size: 18px;
  font-weight: 500;
}

.count-badge {
  display: inline-block;
  background: linear-gradient(135deg, #1DB954 0%, #169B43 100%);
  color: #000000;
  padding: 4px 16px;
  border-radius: 20px;
  font-weight: 700;
  font-size: 20px;
  margin-right: 6px;
  box-shadow: 0 2px 10px rgba(29, 185, 84, 0.4);
}

/* Loading */
.loading {
  text-align: center;
  padding: 100px 20px;
  color: #1DB954;
}

.loading-spinner {
  width: 60px;
  height: 60px;
  border: 5px solid rgba(29, 185, 84, 0.1);
  border-top: 5px solid #1DB954;
  border-radius: 50%;
  margin: 0 auto 24px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Error Message */
.error-message {
  max-width: 600px;
  margin: 60px auto;
  padding: 24px;
  background-color: rgba(255, 68, 68, 0.1);
  border: 1px solid rgba(255, 68, 68, 0.3);
  border-radius: 12px;
  color: #FF4444;
  text-align: center;
  font-size: 16px;
}

/* Movies Section */
.movies-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 50px;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 24px;
}

.movie-card {
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #141414;
}

.movie-card:hover {
  transform: scale(1.05);
  box-shadow: 0 8px 30px rgba(29, 185, 84, 0.3);
  z-index: 10;
}

.poster {
  position: relative;
  width: 100%;
  height: 320px;
  overflow: hidden;
  background: #222;
  display: flex;
  align-items: center;
  justify-content: center;
}

.poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.movie-card:hover .poster img {
  transform: scale(1.1);
}

.card-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.9) 0%, transparent 50%);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.movie-card:hover .card-overlay {
  opacity: 1;
}

.play-button {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #1DB954;
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: bold;
  padding-left: 4px;
  transform: scale(0.8);
  transition: transform 0.3s ease;
  box-shadow: 0 4px 20px rgba(29, 185, 84, 0.6);
}

.movie-card:hover .play-button {
  transform: scale(1);
}

.noimg {
  color: #666;
  font-size: 14px;
}

/* 좋아요 버튼 */
.favorite-btn {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.7);
  border: 2px solid rgba(255, 255, 255, 0.3);
  color: #888;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  z-index: 10;
  backdrop-filter: blur(10px);
}

.favorite-btn:hover {
  background: rgba(0, 0, 0, 0.9);
  border-color: #FFD700;
  transform: scale(1.1);
}

.favorite-btn.is-favorited {
  color: #FFD700;
  border-color: #FFD700;
  background: rgba(255, 215, 0, 0.15);
}

.movie-info {
  padding: 16px;
}

.title {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: 10px;
  color: #ffffff;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.3;
}

.meta {
  display: flex;
  justify-content: space-between;
  color: #888;
  font-size: 14px;
  margin-bottom: 10px;
}

.overview {
  color: #aaa;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 0;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 100px 20px;
  color: #666;
}

.empty-icon {
  font-size: 72px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state p {
  font-size: 18px;
}

/* Responsive */
@media (max-width: 768px) {
  .header-section {
    padding: 40px 20px 30px;
  }
  
  .page-title {
    font-size: 32px;
  }
  
  .page-subtitle {
    font-size: 16px;
  }
  
  .search-bar {
    flex-direction: column;
  }
  
  .search-input {
    width: 100%;
  }
  
  .refresh-button {
    width: 100%;
    justify-content: center;
  }
  
  .movies-section {
    padding: 30px 20px;
  }
  
  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
  }
  
  .poster {
    height: 240px;
  }
}
</style>

