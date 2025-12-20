<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecommendationStore } from '@/stores/recommendation'
import { moviesApi } from '@/api/movies'

const route = useRoute()
const router = useRouter()
const store = useRecommendationStore()

const movieId = computed(() => Number(route.params.movieId))

// movie detail
const movie = ref(null)
const loading = ref(false)
const error = ref(null)

async function loadMovieDetail() {
  loading.value = true
  error.value = null
  try {
    const { data } = await moviesApi.detail(movieId.value)
    movie.value = data
  } catch (err) {
    console.error(err)
    error.value = '영화 정보를 불러올 수 없습니다.'
  } finally {
    loading.value = false
  }
}

// trailer
const trailerUrl = ref(null)
const trailerError = ref(null)
const trailerLoading = ref(false)

function goCommunity() {
  router.push({ name: 'community', params: { movieId: movieId.value } })
}

async function loadTrailer() {
  trailerLoading.value = true
  trailerError.value = null
  trailerUrl.value = null
  
  try {
    const { data } = await moviesApi.trailer(movieId.value)
    if (data.trailer) {
      trailerUrl.value = data.trailer
    } else {
      trailerError.value = '예고편이 없습니다.'
    }
  } catch (err) {
    console.error('예고편 로딩 오류:', err)
    trailerError.value = '예고편을 불러오지 못했습니다.'
  } finally {
    trailerLoading.value = false
  }
}

function posterUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w500${path}`
}

// movieId가 바뀔 때마다(추천 영화 클릭 시 등) 데이터를 새로 불러옴
watch(movieId, async (newId) => {
  if (newId) {
    // 페이지 최상단으로 즉시 이동 (이질감 제거)
    window.scrollTo(0, 0)
    
    await loadMovieDetail()
    if (movie.value) {
      store.fetchRecommend(newId)
      await loadTrailer()
    }
  }
}, { immediate: true })
</script>

<template>
  <div>
    <div v-if="loading" class="loading">영화 정보를 불러오는 중...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="movie" class="movie-detail">
      <div class="header">
        <h1>{{ movie.title }}</h1>
        <p class="en-title" v-if="movie.original_title">{{ movie.original_title }}</p>
      </div>

      <div class="info-section">
        <div class="poster-wrapper">
          <img :src="posterUrl(movie.poster_path)" alt="poster" class="big-poster" v-if="movie.poster_path"/>
          <div v-else class="no-poster">No Image</div>
        </div>

        <div class="text-info">
          <div class="meta-row">
            <span>📅 {{ movie.release_date }}</span>
            <span>⭐ {{ movie.vote_average }}</span>
            <span>💬 리뷰 {{ movie.review_count }}개</span>
          </div>
          
          <div class="genres" v-if="movie.genres && movie.genres.length">
             <span v-for="g in movie.genres" :key="g" class="genre-tag">{{ g }}</span>
          </div>

          <div class="overview" v-if="movie.overview">
            <h3>줄거리</h3>
            <p>{{ movie.overview }}</p>
          </div>

          <button @click="goCommunity" class="community-btn">
            📢 리뷰 커뮤니티로 이동
          </button>
        </div>
      </div>
      
      <!-- 🎬 예고편 -->
      <section style="margin:40px 0;">
        <h3>🎬 예고편</h3>

        <div v-if="trailerLoading" style="text-align:center; padding:40px; color:#666;">
          예고편을 불러오는 중...
        </div>

        <div v-else-if="trailerUrl" class="trailer-container">
          <iframe
            :src="trailerUrl"
            width="100%"
            height="420"
            frameborder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowfullscreen
            class="trailer-iframe"
          />
        </div>

        <div v-else-if="trailerError" class="trailer-error">
          {{ trailerError }}
        </div>

        <div v-else class="trailer-error">
          예고편이 없습니다.
        </div>
      </section>
    </div>

      <!-- ⭐ 추천 영화 -->
      <section class="recommend-section">
        <h3 class="section-title">비슷한 분위기의 추천 영화</h3>
        <p v-if="store.loading" class="loading-small">추천 영화를 찾는 중...</p>
        <p v-if="store.error" class="error-small">{{ store.error }}</p>

        <div v-if="store.items.length" class="recommend-grid">
          <div
            v-for="m in store.items"
            :key="m.id"
            class="recommend-card"
            @click="router.push({ name: 'movieDetail', params: { movieId: m.tmdb_id } })"
          >
            <div class="recommend-poster">
              <img
                v-if="m.poster_path"
                :src="posterUrl(m.poster_path)"
                alt="poster"
              />
              <div v-else class="no-poster-small">No Image</div>
            </div>
            <div class="recommend-info">
              <div class="recommend-title">{{ m.title }}</div>
              <div class="recommend-meta">
                <span class="rating">⭐ {{ m.vote_average?.toFixed(1) }}</span>
                <span class="popularity">🔥 {{ Math.round(m.popularity) }}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
</template>

<style scoped>
.movie-detail {
  padding: 40px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 40px;
  border-bottom: 1px solid #222;
  padding-bottom: 20px;
}

.header h1 {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 10px;
  color: #ffffff;
}

.en-title {
  color: #888;
  font-size: 1.2rem;
  font-weight: 400;
}

.info-section {
  display: flex;
  gap: 50px;
  flex-wrap: wrap;
  margin-bottom: 60px;
}

.poster-wrapper {
  flex-shrink: 0;
}

.big-poster {
  width: 350px;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.text-info {
  flex: 1;
  min-width: 300px;
}

.meta-row {
  display: flex;
  gap: 20px;
  font-size: 1.2rem;
  margin-bottom: 25px;
  color: #e5e5e5; /* 밝은 색으로 변경 */
}

.genres {
  margin-bottom: 30px;
}

.genre-tag {
  display: inline-block;
  background: rgba(255, 255, 255, 0.1); /* 어두운 배경에 맞는 태그 색상 */
  padding: 8px 16px;
  border-radius: 4px;
  margin-right: 10px;
  font-size: 0.95rem;
  font-weight: 600;
  color: #1ed760;
  border: 1px solid rgba(30, 215, 96, 0.3);
}

.overview h3 {
  margin-bottom: 15px;
  font-size: 1.5rem;
  color: #ffffff;
}

.overview p {
  line-height: 1.8;
  color: #cccccc; /* 기존보다 밝게 조정 */
  font-size: 1.1rem;
  letter-spacing: -0.02em;
}

.community-btn {
  margin-top: 40px;
  background-color: #1db954;
  color: white;
  border: none;
  padding: 16px 32px;
  border-radius: 50px;
  font-size: 1.1rem;
  font-weight: 800;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  box-shadow: 0 4px 15px rgba(29, 185, 84, 0.3);
}

.community-btn:hover {
  background-color: #1ed760;
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(29, 185, 84, 0.5);
}

/* 예고편 섹션 */
.trailer-container {
  position: relative;
  width: 100%;
  max-width: 1000px;
  margin: 30px 0;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
  background: #000;
}

.trailer-iframe {
  aspect-ratio: 16 / 9;
  width: 100%;
  height: auto;
  border: none;
}

/* 추천 섹션 */
.recommend-section {
  margin-top: 80px;
  padding-top: 40px;
  border-top: 1px solid #222;
}

.section-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 30px;
  color: #ffffff;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 25px;
}

.recommend-card {
  background: #181818;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #282828;
}

.recommend-card:hover {
  transform: translateY(-10px);
  border-color: #1db954;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
}

.recommend-poster {
  width: 100%;
  aspect-ratio: 2 / 3; /* 포스터 비율 유지 */
  overflow: hidden;
  background: #222;
}

.recommend-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* 공간을 꽉 채우되 비율 유지 */
  transition: transform 0.5s ease;
}

.recommend-card:hover .recommend-poster img {
  transform: scale(1.1);
}

.recommend-info {
  padding: 15px;
}

.recommend-title {
  font-size: 1rem;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.recommend-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #888;
}

.recommend-meta .rating {
  color: #1db954;
  font-weight: 600;
}

.loading { text-align: center; padding: 100px; font-size: 1.5rem; color: #1db954; }
.error { text-align: center; padding: 100px; color: #ff4444; }
.loading-small { color: #888; text-align: center; padding: 20px; }
.error-small { color: #ff4444; text-align: center; padding: 20px; }
.no-poster-small { height: 100%; display: flex; align-items: center; justify-content: center; color: #444; }

@media (max-width: 768px) {
  .big-poster { width: 100%; }
  .header h1 { font-size: 2rem; }
  .info-section { gap: 30px; }
}
</style>
