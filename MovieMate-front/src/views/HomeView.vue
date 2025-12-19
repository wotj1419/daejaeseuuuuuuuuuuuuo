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
    const { data } = await moviesApi.search(query)
    searchResults.value = data.results || []
    totalResults.value = data.total_results || 0
    
    if (searchResults.value.length === 0) {
      error.value = '검색 결과가 없습니다.'
    }
  } catch (e) {
    console.error(e)
    error.value = '영화 검색 중 오류가 발생했습니다.'
    searchResults.value = []
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
  <div>
    <h1>MovieMate</h1>
    <p style="color:#666; margin-bottom:20px;">
      영화 추천 멘트를 입력하면 관련 영화를 추천해드립니다.
    </p>

    <div class="search-container">
      <div class="search-box">
        <input 
          v-model="searchQuery" 
          @keyup.enter="searchMovies"
          placeholder="예: 액션 영화 추천해줘, 로맨스 영화, 공포 영화 등" 
          class="search-input"
        />
        <button @click="searchMovies" :disabled="loading" class="search-button">
          {{ loading ? '검색 중...' : '검색' }}
        </button>
      </div>
    </div>

    <div v-if="error" class="error-message">{{ error }}</div>
    
    <div v-if="totalResults > 0" class="results-info">
      총 {{ totalResults }}개의 영화를 찾았습니다.
    </div>

    <div v-if="loading" class="loading">검색 중...</div>

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
        </div>
        <div class="movie-info">
          <div class="title">{{ movie.title }}</div>
          <div class="meta">
            <span>⭐ {{ movie.vote_average?.toFixed(1) || '-' }}</span>
            <span>🔥 {{ movie.popularity?.toFixed(0) || '-' }}</span>
          </div>
          <p class="overview" v-if="movie.overview">{{ movie.overview }}</p>
          <div class="release-date" v-if="movie.release_date">
            {{ movie.release_date }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.search-container {
  margin: 20px 0;
}

.search-box {
  display: flex;
  gap: 10px;
  max-width: 600px;
}

.search-input {
  flex: 1;
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.search-input:focus {
  outline: none;
  border-color: #4CAF50;
}

.search-button {
  padding: 12px 24px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-button:hover:not(:disabled) {
  background-color: #45a049;
}

.search-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.error-message {
  color: #f44336;
  margin: 16px 0;
  padding: 12px;
  background-color: #ffebee;
  border-radius: 8px;
}

.results-info {
  color: #666;
  margin: 16px 0;
  font-size: 14px;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
  font-size: 18px;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 24px;
}

.movie-card {
  border: 1px solid #eee;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  background: white;
}

.movie-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.poster {
  width: 100%;
  height: 400px;
  overflow: hidden;
  background: #f4f4f4;
  display: flex;
  align-items: center;
  justify-content: center;
}

.poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.noimg {
  color: #777;
  font-size: 14px;
}

.movie-info {
  padding: 16px;
}

.title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: #333;
}

.meta {
  display: flex;
  justify-content: space-between;
  color: #555;
  font-size: 14px;
  margin-bottom: 8px;
}

.overview {
  color: #666;
  font-size: 13px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin: 8px 0;
}

.release-date {
  color: #999;
  font-size: 12px;
  margin-top: 8px;
}
</style>
