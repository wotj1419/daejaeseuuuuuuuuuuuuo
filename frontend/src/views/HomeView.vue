<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { moviesApi } from '@/api/movies'
import { favoritesApi } from '@/api/favorites'
import { useAuthStore } from '@/stores/auth'

// Swiper 관련 임포트
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Autoplay, EffectFade, Pagination } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/effect-fade'
import 'swiper/css/pagination'

const router = useRouter()
const authStore = useAuthStore()
const searchQuery = ref('')
const loading = ref(false)
const error = ref(null)
const searchResults = ref([])
const totalResults = ref(0)
const isAiMode = ref(false)
const aiResult = ref('')

// 인기 영화 목록 (캐러셀용)
const popularMovies = ref([])
// 영화별 예고편 URL 저장 (tmdb_id: url)
const trailers = ref({})
// 영화별 좋아요 상태 저장 (tmdb_id: boolean)
const favoriteStatuses = ref({})

// TMDB poster_path가 상대경로일 때 보정
function posterUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w500${path}`
}

// 배경화면용 고해상도 이미지 경로
function backdropUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/original${path}`
}

/**
 * 영화 목록을 불러오고 각 영화의 예고편 및 좋아요 상태 정보를 가져옵니다.
 */
async function fetchPopularMovies() {
  try {
    const { data } = await moviesApi.list()
    popularMovies.value = data.slice(0, 10) // 상위 10개만 표시
    
    popularMovies.value.forEach(async (movie) => {
      // 1. 예고편 가져오기
      try {
        const response = await moviesApi.trailer(movie.tmdb_id)
        if (response.data && response.data.trailer) {
          trailers.value[movie.tmdb_id] = `${response.data.trailer}?autoplay=1&mute=1&controls=0&loop=1&playlist=${response.data.trailer.split('/').pop()}&rel=0&showinfo=0`
        }
      } catch (err) {
        console.warn(`${movie.title}의 예고편을 가져오는데 실패했습니다.`)
      }

      // 2. 좋아요 상태 가져오기 (로그인 시)
      if (authStore.isAuthenticated) {
        try {
          const { data: statusData } = await favoritesApi.checkFavoriteStatus(movie.tmdb_id)
          favoriteStatuses.value[movie.tmdb_id] = statusData.is_favorited
        } catch (err) {
          console.error('좋아요 상태 확인 실패:', err)
        }
      }
    })
  } catch (e) {
    console.error('인기 영화를 불러오는데 실패했습니다:', e)
  }
}

/**
 * 좋아요 상태를 토글합니다.
 */
async function toggleFavorite(movieId, event) {
  if (event) event.stopPropagation() // 카드 클릭 이벤트 전파 방지

  if (!authStore.isAuthenticated) {
    if (confirm('로그인이 필요한 기능입니다. 로그인 페이지로 이동하시겠습니까?')) {
      router.push({ name: 'login' })
    }
    return
  }

  try {
    const { data } = await favoritesApi.toggleFavorite(movieId)
    favoriteStatuses.value[movieId] = data.is_favorited
  } catch (err) {
    console.error('좋아요 토글 실패:', err)
  }
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
    // 검색 결과가 있으면 해당 영역으로 스크롤
    if (searchResults.value.length > 0) {
      setTimeout(() => {
        document.querySelector('.content-section')?.scrollIntoView({ behavior: 'smooth' })
      }, 100)
    }
  }
}

function goToMovieDetail(tmdbId) {
  router.push({ name: 'movieDetail', params: { movieId: tmdbId } })
}

onMounted(() => {
  fetchPopularMovies()
})
</script>

<template>
  <div class="home-container">
    <!-- Hero Section with Swiper Carousel -->
    <section class="hero">
      <swiper
        :modules="[Autoplay, EffectFade, Pagination]"
        :slides-per-view="1"
        :loop="true"
        :effect="'fade'"
        :fade-effect="{ crossFade: true }"
        :autoplay="{
          delay: 5000,
          disableOnInteraction: false,
        }"
        :pagination="{ clickable: true }"
        class="hero-swiper"
      >
        <swiper-slide v-for="movie in popularMovies" :key="movie.tmdb_id" v-slot="{ isActive }">
          <!-- 배경 이미지 레이어: 예고편이 로딩되기 전이나 없을 때 보여줍니다. -->
          <div class="slide-background" :style="{ backgroundImage: `url(${backdropUrl(movie.backdrop_path)})` }"></div>
          
          <!-- 예고편 비디오 레이어: 활성 슬라이드이고 예고편 URL이 있을 때만 렌더링합니다. -->
          <div v-if="isActive && trailers[movie.tmdb_id]" class="video-container">
            <iframe
              :src="trailers[movie.tmdb_id]"
              frameborder="0"
              allow="autoplay; encrypted-media; gyroscope; picture-in-picture"
              allowfullscreen
              class="video-iframe"
            ></iframe>
          </div>

          <!-- 오버레이 레이어: 텍스트 가독성을 위해 어둡게 처리합니다. -->
          <div class="slide-overlay"></div>
          
          <!-- 컨텐츠 레이어 -->
          <div class="hero-content">
            <h1 class="hero-title">{{ movie.title }}</h1>
            <p class="hero-subtitle">{{ movie.overview?.substring(0, 150) }}...</p>
            <div class="hero-actions">
              <button @click="goToMovieDetail(movie.tmdb_id)" class="detail-button primary">
                <span class="play-icon">▶</span> 상세정보
              </button>
              <!-- 💖 히어로 섹션 좋아요 버튼 -->
              <button 
                @click="toggleFavorite(movie.tmdb_id)" 
                class="hero-favorite-btn"
                :class="{ active: favoriteStatuses[movie.tmdb_id] }"
              >
                {{ favoriteStatuses[movie.tmdb_id] ? '❤️' : '🤍' }}
              </button>
            </div>
          </div>
        </swiper-slide>
        
        <!-- 기본 배경 (로딩 중 또는 데이터 없음) -->
        <swiper-slide v-if="popularMovies.length === 0">
          <div class="slide-background default-bg"></div>
          <div class="hero-content">
            <h1 class="hero-title">Movie Mate</h1>
            <p class="hero-subtitle">당신의 취향을 저격할 영화를 찾아줍니다.</p>
          </div>
        </swiper-slide>
      </swiper>

      <!-- 검색 컨테이너 (Hero 내부 하단 중앙 배치) -->
      <div class="search-container">
        <div class="search-wrapper">
          <div class="mode-selector">
            <button 
              class="mode-btn" 
              :class="{ active: !isAiMode }" 
              @click="isAiMode = false"
            >
              <span>🪐 일반 검색</span>
            </button>
            <button 
              class="mode-btn ai" 
              :class="{ active: isAiMode }" 
              @click="isAiMode = true"
            >
              <span>✨ AI 영화 추천</span>
            </button>
          </div>
          
          <div class="search-box">
            <div class="input-group">
              <input 
                v-model="searchQuery" 
                @keyup.enter="searchMovies"
                :placeholder="isAiMode ? '오늘 기분이 어떤가요? 상황에 맞는 영화를 추천해드릴게요.' : '궁금한 영화 제목을 입력하세요'" 
                class="search-input"
              />
              <button @click="searchMovies" :disabled="loading" class="search-button">
                <span v-if="!loading">검색하기</span>
                <span v-else class="mini-spinner"></span>
              </button>
            </div>
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
            <!-- 카드 위 좋아요 버튼 -->
            <button 
              class="card-favorite-btn" 
              :class="{ active: favoriteStatuses[movie.tmdb_id] }"
              @click="toggleFavorite(movie.tmdb_id, $event)"
            >
              {{ favoriteStatuses[movie.tmdb_id] ? '❤️' : '🤍' }}
            </button>
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
  height: 95vh;
  width: 100%;
  background-color: #000;
  overflow: hidden;
}

.hero-swiper {
  width: 100%;
  height: 100%;
}

:deep(.swiper-slide) {
  position: relative;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background-color: #000;
}

.slide-background {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  z-index: 1;
}

/* 비디오 컨테이너 스타일: 화면을 꽉 채우도록 설정 */
.video-container {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100vw;
  height: 100vh;
  transform: translate(-50%, -50%);
  z-index: 2;
  overflow: hidden;
  pointer-events: none; /* 클릭 방지 */
}

/* iframe 스타일: 16:9 비율을 유지하며 화면을 채움 */
.video-iframe {
  width: 100vw;
  height: 56.25vw; /* 100 * 9 / 16 */
  min-height: 100vh;
  min-width: 177.77vh; /* 100 * 16 / 9 */
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.default-bg {
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
}

.slide-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: radial-gradient(circle, rgba(0,0,0,0.2) 0%, rgba(0,0,0,0.6) 80%);
  background-color: rgba(0, 0, 0, 0.4);
  z-index: 2;
  pointer-events: none;
}

.hero-content {
  position: absolute;
  top: 40%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 10;
  text-align: center;
  width: 100%;
  max-width: 1000px;
  padding: 0 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.hero-title {
  font-size: clamp(40px, 5vw, 70px);
  font-weight: 900;
  color: #ffffff;
  margin-bottom: 20px;
  line-height: 1.1;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
  animation: fadeInUp 0.8s ease-out;
}

.hero-subtitle {
  font-size: clamp(16px, 1.5vw, 20px);
  color: #e5e5e5;
  margin-bottom: 30px;
  max-width: 800px;
  line-height: 1.6;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  animation: fadeInUp 1s ease-out;
}

.hero-actions {
  display: flex;
  gap: 15px;
  animation: fadeInUp 1.2s ease-out;
}

.detail-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 28px;
  background-color: rgba(255, 255, 255, 0.9);
  color: #000000;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s ease;
}

.play-icon {
  font-size: 18px;
}

.detail-button:hover {
  background-color: #1db954;
  color: #ffffff;
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(29, 185, 84, 0.3);
}

/* 히어로 섹션 좋아요 버튼 */
.hero-favorite-btn {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
  backdrop-filter: blur(5px);
}

.hero-favorite-btn:hover {
  background-color: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
  border-color: #ff4757;
}

.hero-favorite-btn.active {
  background-color: rgba(255, 71, 87, 0.15);
  border-color: #ff4757;
}

/* 영화 카드 좋아요 버튼 */
.card-favorite-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  opacity: 0; /* 평소에는 숨김 */
}

.movie-card:hover .card-favorite-btn {
  opacity: 1; /* 호버 시 노출 */
}

.card-favorite-btn:hover {
  transform: scale(1.1);
  background: rgba(0, 0, 0, 0.7);
  border-color: #ff4757;
}

.card-favorite-btn.active {
  opacity: 1;
  background: rgba(255, 71, 87, 0.1);
  border-color: #ff4757;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Search Container Positioning */
.search-container {
  position: absolute;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  width: 90%;
  max-width: 800px;
  z-index: 20;
}

.hero-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 200px;
  background: linear-gradient(to top, #000000 0%, transparent 100%);
  z-index: 15;
  pointer-events: none;
}

/* Search Box CSS */
/* 검색창 전체 컨테이너: 강력한 유리 질감 효과 */
.search-wrapper {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  padding: 10px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-wrapper:focus-within {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  box-shadow: 0 30px 60px -12px rgba(0, 0, 0, 0.8), 0 0 20px rgba(29, 185, 84, 0.1);
}

.mode-selector {
  display: flex;
  gap: 6px;
  background: rgba(0, 0, 0, 0.4);
  padding: 5px;
  border-radius: 22px;
  margin-bottom: 10px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.mode-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 18px;
  background: transparent;
  color: #888;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  letter-spacing: -0.5px;
}

.mode-btn:hover:not(.active) {
  color: #bbb;
  background: rgba(255, 255, 255, 0.05);
}

.mode-btn.active {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.mode-btn.ai.active {
  background: linear-gradient(135deg, #1db954, #1ed760);
  color: #000;
  box-shadow: 0 4px 20px rgba(29, 185, 84, 0.4);
}

.input-group {
  display: flex;
  gap: 8px;
}

.search-input {
  flex: 1;
  padding: 14px 20px;
  background: transparent;
  border: none;
  font-size: 16px;
  color: #fff;
}

.search-input:focus {
  outline: none;
}

.search-input::placeholder {
  color: #777;
  transition: color 0.3s;
}

.search-input:focus::placeholder {
  color: #999;
}

.search-button {
  padding: 0 32px;
  background: linear-gradient(135deg, #ffffff 0%, #f0f0f0 100%);
  color: #000;
  border: none;
  border-radius: 18px;
  font-weight: 800;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(255, 255, 255, 0.1);
}

.search-button:hover:not(:disabled) {
  background: #1db954;
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(29, 185, 84, 0.4);
}

.search-button:active:not(:disabled) {
  transform: translateY(0);
}

.mini-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0,0,0,0.1);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Shared Spinner Animation */
@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Swiper Customize */
:deep(.swiper-pagination) {
  bottom: 30px !important;
  right: 30px !important;
  left: auto !important;
  width: auto !important;
}

:deep(.swiper-pagination-bullet) {
  background: rgba(255, 255, 255, 0.4);
  width: 8px;
  height: 8px;
  transition: all 0.3s;
}

:deep(.swiper-pagination-bullet-active) {
  background: #1db954;
  width: 24px;
  border-radius: 4px;
}

/* Content Section */
.content-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 50px;
}

.error-message {
  color: #ff4444;
  margin: 24px 0;
  text-align: center;
}

.results-info {
  color: #888;
  margin: 24px 0;
  text-align: center;
}

.loading {
  text-align: center;
  padding: 60px 0;
  color: #1db954;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(29, 185, 84, 0.2);
  border-top-color: #1db954;
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 1s linear infinite;
}

.ai-result-box {
  background: rgba(29, 185, 84, 0.05);
  border: 1px solid rgba(29, 185, 84, 0.2);
  border-radius: 16px;
  padding: 24px;
  margin: 30px 0;
}

.ai-result-box h3 {
  color: #1db954;
  margin: 0 0 12px 0;
}

.ai-content {
  color: #ddd;
  line-height: 1.6;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  margin-top: 20px;
}

.movie-card {
  background: #141414;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s;
}

.movie-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.5);
  z-index: 5;
}

.poster {
  position: relative;
  aspect-ratio: 2/3;
  overflow: hidden;
  background: #222;
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

.card-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
}

.movie-card:hover .card-overlay {
  opacity: 1;
}

.play-button {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: #1db954;
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.movie-info {
  padding: 12px;
}

.title {
  color: #fff;
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.meta {
  display: flex;
  justify-content: space-between;
  color: #888;
  font-size: 12px;
}

@media (max-width: 768px) {
  .hero {
    height: 80vh;
  }
  
  .hero-content {
    top: 35%;
  }

  .hero-title {
    font-size: 32px;
  }
  
  .search-container {
    bottom: 30px;
    width: 95%;
  }
  
  .search-wrapper {
    padding: 10px;
  }
  
  .search-input {
    font-size: 14px;
    padding: 12px;
  }
  
  .search-button {
    padding: 0 20px;
    font-size: 14px;
  }
}
</style>
