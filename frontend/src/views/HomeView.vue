<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { moviesApi } from '@/api/movies'

// Swiper 관련 임포트
import { Swiper, SwiperSlide } from 'swiper/vue'
import { Autoplay, EffectFade, Pagination } from 'swiper/modules'
import 'swiper/css'
import 'swiper/css/effect-fade'
import 'swiper/css/pagination'

const router = useRouter()
const searchQuery = ref('')
const loading = ref(false)
const error = ref(null)
const searchResults = ref([])
const totalResults = ref(0)
const isAiMode = ref(false)
const aiResult = ref('')

// 인기 영화 목록 (캐러셀용)
const popularMovies = ref([])

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

async function fetchPopularMovies() {
  try {
    const { data } = await moviesApi.list()
    popularMovies.value = data.slice(0, 10) // 상위 10개만 표시
  } catch (e) {
    console.error('인기 영화를 불러오는데 실패했습니다:', e)
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
        :autoplay="{
          delay: 5000,
          disableOnInteraction: false,
        }"
        :pagination="{ clickable: true }"
        class="hero-swiper"
      >
        <swiper-slide v-for="movie in popularMovies" :key="movie.tmdb_id">
          <div 
            class="slide-content" 
            :style="{ backgroundImage: `url(${posterUrl(movie.poster_path)})` }"
          >
            <div class="slide-blur-overlay"></div>
            <div class="slide-dark-overlay"></div>
            <div class="hero-content">
              <h1 class="hero-title">{{ movie.title }}</h1>
              <p class="hero-subtitle">{{ movie.overview?.substring(0, 150) }}...</p>
              <div class="hero-actions">
                <button @click="goToMovieDetail(movie.tmdb_id)" class="detail-button primary">
                  <span class="play-icon">▶</span> 영화 보러 가기
                </button>
              </div>
            </div>
          </div>
        </swiper-slide>
        
        <!-- 기본 배경 (영화 로딩 중이거나 없을 때) -->
        <swiper-slide v-if="popularMovies.length === 0">
          <div class="slide-content default-bg">
            <div class="hero-content">
              <h1 class="hero-title">Movie Mate</h1>
              <p class="hero-subtitle">당신의 취향을 저격할 영화를 찾아줍니다.</p>
            </div>
          </div>
        </swiper-slide>
      </swiper>

      <!-- Search Overlay -->
      <div class="search-overlay">
        <div class="search-wrapper">
          <div class="mode-selector">
            <button 
              class="mode-btn" 
              :class="{ active: !isAiMode }" 
              @click="isAiMode = false"
            >
              🔍 일반 검색
            </button>
            <button 
              class="mode-btn ai" 
              :class="{ active: isAiMode }" 
              @click="isAiMode = true"
            >
              🤖 AI 영화 추천
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
  height: 90vh;
  width: 100%;
  overflow: hidden;
  background-color: #000;
}

.hero-swiper {
  width: 100%;
  height: 100%;
}

.slide-content {
  width: 100%;
  height: 100%;
  background-size: cover;
  background-position: center;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  background-repeat: no-repeat;
}

/* 썸네일에 어둡고 블러 처리 된 효과 (연하게 조정) */
.slide-blur-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  backdrop-filter: blur(8px) brightness(0.5); /* 블러를 연하게, 밝기는 유지 */
  z-index: 1;
}

.slide-dark-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    to bottom,
    rgba(0, 0, 0, 0.2) 0%,
    rgba(0, 0, 0, 0.4) 50%,
    rgba(0, 0, 0, 0.8) 100%
  );
  z-index: 2;
}

/* 실제 영화 포스터가 은은하게 배경으로 보임 */
.slide-content::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image: inherit;
  background-size: cover;
  background-position: center;
  filter: blur(15px) opacity(0.7); /* 블러를 연하게 하여 그림이 더 잘 보이게 함 */
  z-index: 0;
}

.default-bg {
  background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
}

.hero-content {
  position: relative;
  z-index: 10;
  text-align: left; /* 왼쪽 정렬로 변경하여 세련미 추구 */
  width: 100%;
  max-width: 1200px;
  padding: 0 50px;
  margin-top: -150px;
}

.hero-title {
  font-size: clamp(40px, 6vw, 80px);
  font-weight: 900;
  color: #ffffff;
  margin-bottom: 20px;
  line-height: 1;
  text-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  animation: fadeInLeft 0.8s ease-out;
}

.hero-subtitle {
  font-size: clamp(16px, 2vw, 22px);
  color: #cccccc;
  margin-bottom: 40px;
  max-width: 600px;
  line-height: 1.5;
  text-shadow: 0 5px 15px rgba(0, 0, 0, 0.5);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  animation: fadeInLeft 1s ease-out;
}

.hero-actions {
  display: flex;
  gap: 15px;
  animation: fadeInLeft 1.2s ease-out;
}

.detail-button {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  background-color: #ffffff;
  color: #000000;
  border: none;
  border-radius: 8px;
  font-size: 18px;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.play-icon {
  font-size: 20px;
}

.detail-button:hover {
  background-color: #1db954;
  color: #ffffff;
  transform: scale(1.05) translateY(-5px);
  box-shadow: 0 15px 30px rgba(29, 185, 84, 0.4);
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-50px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Search Overlay */
.search-overlay {
  position: absolute;
  bottom: 8%;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 900px;
  z-index: 20;
  padding: 0 30px;
}

.hero-gradient {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 300px;
  background: linear-gradient(to top, #000000, transparent);
  z-index: 15;
}

/* Search Wrapper & Mode Selector */
.search-wrapper {
  background: rgba(20, 20, 20, 0.7);
  backdrop-filter: blur(20px);
  padding: 10px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.8);
}

.mode-selector {
  display: flex;
  padding: 5px;
  gap: 5px;
  background: rgba(0, 0, 0, 0.3);
  border-radius: 15px;
  margin-bottom: 10px;
}

.mode-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 10px;
  background: transparent;
  color: #888;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
}

.mode-btn.active {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.mode-btn.ai.active {
  background: linear-gradient(135deg, #1db954 0%, #169b43 100%);
  color: #ffffff;
  box-shadow: 0 5px 15px rgba(29, 185, 84, 0.3);
}

.input-group {
  display: flex;
  padding: 5px;
  gap: 10px;
}

.search-input {
  flex: 1;
  padding: 18px 25px;
  background-color: transparent;
  border: none;
  font-size: 18px;
  color: #ffffff;
}

.search-input:focus {
  outline: none;
}

.search-button {
  padding: 0 40px;
  background-color: #ffffff;
  color: #000000;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 900;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-button:hover:not(:disabled) {
  background-color: #1db954;
  color: #ffffff;
}

.mini-spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(0, 0, 0, 0.1);
  border-top: 3px solid #000;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Swiper Customize */
:deep(.swiper-pagination) {
  bottom: 40px !important;
  left: auto !important;
  right: 50px !important;
  width: auto !important;
}

:deep(.swiper-pagination-bullet) {
  background: rgba(255, 255, 255, 0.5);
  width: 10px;
  height: 10px;
  opacity: 1;
}

:deep(.swiper-pagination-bullet-active) {
  background: #1db954;
  width: 25px;
  border-radius: 5px;
}

/* Content Section */
.content-section {
  max-width: 1400px;
  margin: 0 auto;
  padding: 60px 50px;
}

.error-message {
  color: #ff4444;
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
  color: #1db954;
}

.loading-spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(29, 185, 84, 0.1);
  border-top: 4px solid #1db954;
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}

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
  color: #1db954;
  font-size: 24px;
  margin-bottom: 16px;
}

.ai-content {
  line-height: 1.8;
  white-space: pre-wrap;
  color: #e5e5e5;
  font-size: 16px;
}

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
  background-color: #1db954;
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

@media (max-width: 768px) {
  .hero {
    height: 70vh;
  }
  
  .search-overlay {
    bottom: 50px;
    width: 95%;
  }

  .search-wrapper {
    padding: 20px;
    gap: 15px;
  }

  .search-box {
    flex-direction: column;
  }

  .search-button {
    height: 50px;
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
