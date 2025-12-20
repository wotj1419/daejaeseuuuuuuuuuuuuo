<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { favoritesApi } from '@/api/favorites'
import { moviesApi } from '@/api/movies'

const router = useRouter()
const loading = ref(false)
const movies = ref([])

async function loadMyMovies() {
  loading.value = true
  try {
    const { data } = await favoritesApi.getMyMovies()
    movies.value = data
  } catch (e) {
    console.error('내 영화 목록 로드 실패:', e)
  } finally {
    loading.value = false
  }
}

function posterUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w500${path}`
}

function goToMovieDetail(tmdbId) {
  router.push({ name: 'movieDetail', params: { movieId: tmdbId } })
}

onMounted(loadMyMovies)
</script>

<template>
  <div class="my-movies-container">
    <section class="header-section">
      <h1 class="page-title">⭐ 내 영화</h1>
      <p class="page-subtitle">좋아요한 영화 목록</p>
    </section>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>영화 목록을 불러오는 중...</p>
    </div>

    <section v-else-if="movies.length > 0" class="movies-section">
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

    <div v-else class="empty-state">
      <div class="empty-icon">💫</div>
      <p>아직 좋아요한 영화가 없어요.</p>
      <p class="empty-subtitle">영화 목록에서 별 버튼을 눌러보세요!</p>
      <button @click="router.push({ name: 'movies' })" class="go-movies-btn">
        영화 목록 보러가기
      </button>
    </div>
  </div>
</template>

<style scoped>
.my-movies-container {
  width: 100%;
  min-height: 100vh;
  background-color: #000000;
  padding-bottom: 60px;
}

.header-section {
  padding: 60px 50px 40px;
  background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%);
  border-bottom: 1px solid #222;
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
  text-align: center;
}

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

.empty-state {
  text-align: center;
  padding: 100px 20px;
}

.empty-icon {
  font-size: 72px;
  margin-bottom: 20px;
  opacity: 0.5;
}

.empty-state p {
  color: #888;
  font-size: 18px;
  margin-bottom: 8px;
}

.empty-subtitle {
  color: #666;
  font-size: 14px;
  margin-bottom: 30px !important;
}

.go-movies-btn {
  padding: 14px 28px;
  background-color: #1DB954;
  color: #000000;
  border: none;
  border-radius: 50px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 15px rgba(29, 185, 84, 0.4);
}

.go-movies-btn:hover {
  background-color: #1ed760;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(29, 185, 84, 0.6);
}

@media (max-width: 768px) {
  .header-section {
    padding: 40px 20px 30px;
  }
  
  .page-title {
    font-size: 32px;
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
