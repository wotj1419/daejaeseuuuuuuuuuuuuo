<script setup>
import { computed, onMounted, ref } from 'vue'
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

onMounted(async () => {
  await loadMovieDetail()
  
  // 영화 정보가 있으면 추천 영화 및 예고편 로딩
  if (movie.value) {
    store.fetchRecommend(movieId.value)
    await loadTrailer()
  }
})
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
    <h3>추천 영화</h3>
    <p v-if="store.loading">불러오는 중...</p>
    <p v-if="store.error">{{ store.error }}</p>

    <div
      v-if="store.items.length"
      style="display:grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap:12px; margin-top:12px;"
    >
      <div
        v-for="m in store.items"
        :key="m.id"
        class="recommend-card"
        @click="router.push({ name: 'movieDetail', params: { movieId: m.tmdb_id } })"
      >
        <img
          v-if="m.poster_path"
          :src="m.poster_path"
          alt="poster"
          style="width:100%; height:260px; object-fit:cover; border-radius:10px; background:#f4f4f4;"
        />
        <div style="margin-top:10px; font-weight:700;">
          {{ m.title }}
        </div>
        <div style="margin-top:6px; color:#555; font-size:14px;">
          ⭐ {{ m.vote_average }} · 🔥 {{ m.popularity }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.movie-detail {
  padding: 20px 0;
}

.header {
  margin-bottom: 30px;
}

.en-title {
  color: #888;
  font-size: 1.2rem;
}

.info-section {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.big-poster {
  width: 300px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.text-info {
  flex: 1;
  min-width: 300px;
}

.meta-row {
  display: flex;
  gap: 15px;
  font-size: 1.1rem;
  margin-bottom: 15px;
  color: #444;
}

.genres {
  margin-bottom: 20px;
}

.genre-tag {
  display: inline-block;
  background: #eee;
  padding: 6px 12px;
  border-radius: 20px;
  margin-right: 8px;
  font-size: 0.9rem;
  color: #555;
}

.overview h3 {
  margin-bottom: 10px;
}

.overview p {
  line-height: 1.6;
  color: #333;
}

.community-btn {
  margin-top: 30px;
  background-color: #ff4081;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.community-btn:hover {
  background-color: #e91e63;
}

/* 기존 스타일 유지 */
.trailer-container {
  position: relative;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.trailer-iframe {
  width: 100%;
  height: 420px;
  border: none;
  border-radius: 12px;
  background: #000;
}

.recommend-card {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 10px;
  cursor: pointer;
  transition: transform 0.2s;
}
.recommend-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
</style>
