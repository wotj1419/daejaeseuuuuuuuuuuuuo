<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { moviesApi } from '@/api/movies'

const router = useRouter()
const searchQuery = ref('')
const loading = ref(false)
const error = ref(null)
const searchResults = ref([])
const totalResults = ref(0)
const isAiMode = ref(false)
const aiResult = ref('')

// TMDB poster_path가 상대경로일 때 보정
function posterUrl(poster_path) {
  if (!poster_path) return ''
  if (poster_path.startsWith('http')) return poster_path
  return `https://image.tmdb.org/t/p/w500${poster_path}`
}

async function searchMovies() {
  const query = searchQuery.value.trim()
  if (!query) {
    error.value = '검색어를 입력해주세요.'
    return
  }

  loading.value = true
  error.value = null
  searchResults.value = []

  try {
    if (isAiMode.value) {
      const { data } = await moviesApi.aiRecommend(query)
      aiResult.value = data.result
      
      // AI가 추천해준 영화 목록을 결과에 표시
      if (data.movies && data.movies.length > 0) {
        searchResults.value = data.movies
      } else {
        searchResults.value = []
      }
      totalResults.value = searchResults.value.length
    } else {
      const { data } = await moviesApi.search(query)
      searchResults.value = data.results || []
      totalResults.value = data.total_results || 0
      aiResult.value = ''
      
      if (searchResults.value.length === 0) {
        error.value = '검색 결과가 없습니다.'
      }
    }
  } catch (e) {
    console.error(e)
    error.value = isAiMode.value 
      ? 'AI 추천 중 오류가 발생했습니다.' 
      : '영화 검색 중 오류가 발생했습니다.'
    searchResults.value = []
    aiResult.value = ''
  } finally {
    loading.value = false
  }
}

function goToMovieDetail(tmdbId) {
  // DB에 있는 영화인지 확인하고, 없으면 먼저 저장하는 로직이 필요할 수 있음
  // 일단 tmdb_id로 검색하거나, 영화 상세 페이지로 이동
  router.push({ name: 'movieDetail', params: { movieId: tmdbId } })
}
</script>

<template>
  <div class="home-container">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">Movie Mate</h1>
        <p class="hero-subtitle">취향에 맞는 영화를 찾아보세요. </p>
        
        <div class="search-wrapper">
          <div class="mode-toggle">
            <label class="switch">
              <input type="checkbox" v-model="isAiMode">
              <span class="slider round"></span>
            </label>
            <span class="mode-label">{{ isAiMode ? '🤖 AI 추천 모드' : '🔍 일반 검색' }}</span>
          </div>
          
          <div class="search-box">
            <input 
              v-model="searchQuery" 
              @keyup.enter="searchMovies"
              :placeholder="isAiMode ? 'AI에게 기분이나 상황을 말해보세요 (예: 오늘 기분이 우울해)' : '영화 제목을 검색하세요'" 
              class="search-input"
            />
            <button @click="searchMovies" :disabled="loading" class="search-button">
              {{ loading ? '검색 중...' : '검색' }}
            </button>
          </div>
        </div>
      </div>
      <div class="hero-gradient"></div>
    </section>

    <!-- Content Section -->
    <section class="content-section">
      <div v-if="error" class="error-message">{{ error }}</div>
      
      <!-- AI 결과 표시 -->
      <div v-if="aiResult" class="ai-result-box">
        <h3>🤖 AI의 추천</h3>
        <div class="ai-content">{{ aiResult }}</div>
      </div>
      
      <div v-if="totalResults > 0" class="results-info">
        총 {{ totalResults }}개의 영화를 찾았습니다.
      </div>

      <div v-if="loading" class="loading">
        <div class="loading-spinner"></div>
        <p>검색 중...</p>
      </div>

      <div v-if="!loading && searchResults.length > 0" class="movies-grid">
        <div 
          v-for="movie in searchResults" 
          :key="movie.tmdb_id" 
          class="movie-card"
          @click="goToMovieDetail(movie.tmdb_id)"
        >
          <div class="poster">
            <img 
              v-if="movie.poster_path" 
              :src="posterUrl(movie.poster_path)" 
              alt="poster" 
            />
            <div v-else class="noimg">No Image</div>
            <div class="card-overlay">
              <div class="play-button">▶</div>
            </div>
          </div>
          <div class="movie-info">
            <div class="title">{{ movie.title }}</div>
            <div class="meta">
              <span>⭐ {{ movie.vote_average?.toFixed(1) || '-' }}</span>
              <span>{{ movie.release_date?.substring(0, 4) || '-' }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home-container {
  width: 100%;
  min-height: 100vh;
  background-color: #000000;
}

/* Hero Section */
.hero {
  position: relative;
  height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 30% 50%, rgba(0, 255, 0, 0.1) 0%, transparent 50%);
  animation: pulse 8s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; }
  50% { opacity: 0.6; }
}

.hero-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 150px;
  background: linear-gradient(to top, #000000, transparent);
}

.hero-content {
  position: relative;
  z-index: 10;
  text-align: center;
  max-width: 900px;
  padding: 0 20px;
}

.hero-title {
  font-size: 56px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 20px;
  line-height: 1.2;
  text-shadow: 2px 2px 20px rgba(0, 0, 0, 0.8);
}

.hero-subtitle {
  font-size: 24px;
  color: #e5e5e5;
  margin-bottom: 40px;
  font-weight: 400;
  text-shadow: 1px 1px 10px rgba(0, 0, 0, 0.8);
}

/* Search Wrapper */
.search-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
  width: 100%;
}

.mode-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mode-label {
  font-weight: 600;
  color: #1DB954;
  font-size: 16px;
  text-shadow: 0 0 10px rgba(29, 185, 84, 0.5);
}

.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 32px;
}

.switch input { 
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #333;
  transition: .4s;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
}

.slider:before {
  position: absolute;
  content: "";
  height: 24px;
  width: 24px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
}

input:checked + .slider {
  background-color: #1DB954;
  box-shadow: 0 0 20px rgba(29, 185, 84, 0.6);
}

input:checked + .slider:before {
  transform: translateX(28px);
}

.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%;
}

/* Search Box */
.search-box {
  display: flex;
  gap: 12px;
  width: 100%;
  max-width: 700px;
}

.search-input {
  flex: 1;
  padding: 18px 24px;
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

.search-button {
  padding: 18px 36px;
  background-color: #1DB954;
  color: #000000;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  box-shadow: 0 4px 20px rgba(29, 185, 84, 0.4);
}

.search-button:hover:not(:disabled) {
  background-color: #169B43;
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(29, 185, 84, 0.6);
}

.search-button:disabled {
  background-color: #555;
  cursor: not-allowed;
  box-shadow: none;
}

/* Content Section */
.content-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 60px 50px;
}

.error-message {
  color: #FF4444;
  margin: 24px 0;
  padding: 16px 24px;
  background-color: rgba(255, 68, 68, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(255, 68, 68, 0.3);
  text-align: center;
}

.results-info {
  color: #888;
  margin: 24px 0;
  font-size: 16px;
  text-align: center;
}

.loading {
  text-align: center;
  padding: 60px 20px;
  color: #1DB954;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(29, 185, 84, 0.1);
  border-top: 4px solid #1DB954;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* AI Result Box */
.ai-result-box {
  background: linear-gradient(135deg, rgba(0, 255, 0, 0.1) 0%, rgba(0, 200, 0, 0.05) 100%);
  border-radius: 16px;
  padding: 30px;
  margin: 30px 0;
  border: 1px solid rgba(0, 255, 0, 0.3);
  box-shadow: 0 4px 20px rgba(0, 255, 0, 0.2);
}

.ai-result-box h3 {
  margin-top: 0;
  color: #1DB954;
  font-size: 24px;
  margin-bottom: 16px;
}

.ai-content {
  line-height: 1.8;
  white-space: pre-wrap;
  color: #e5e5e5;
  font-size: 16px;
}

/* Movies Grid */
.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 24px;
  margin-top: 40px;
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
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
}

.movie-info {
  padding: 16px;
}

.title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #ffffff;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  display: flex;
  justify-content: space-between;
  color: #888;
  font-size: 13px;
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 36px;
  }
  
  .hero-subtitle {
    font-size: 18px;
  }
  
  .search-box {
    flex-direction: column;
  }
  
  .search-button {
    width: 100%;
  }
  
  .movies-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 16px;
  }
  
  .content-section {
    padding: 40px 20px;
  }
}
</style>

