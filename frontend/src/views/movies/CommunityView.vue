<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reviewsApi } from '@/api/reviews'
import { moviesApi } from '@/api/movies'

const route = useRoute()
const router = useRouter()
const movieId = computed(() => Number(route.params.movieId))

const reviews = ref([])
const movie = ref(null)
const loading = ref(false)
const movieLoading = ref(false)

async function loadMovie() {
  movieLoading.value = true
  try {
    const { data } = await moviesApi.detail(movieId.value)
    movie.value = data
  } catch (e) {
    console.error('영화 정보 로딩 실패:', e)
  } finally {
    movieLoading.value = false
  }
}

async function load() {
  loading.value = true
  try {
    const { data } = await reviewsApi.listByMovie(movieId.value)
    reviews.value = data
  } catch (e) {
    console.error(e)
    alert('리뷰 목록 불러오기 실패')
  } finally {
    loading.value = false
  }
}

function posterUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w500${path}`
}

function goCreate() {
  router.push({ name: 'postCreate', params: { movieId: movieId.value } })
}

function goDetail(id) {
  router.push({ name: 'postDetail', params: { id } })
}

onMounted(() => {
  loadMovie()
  load()
})
</script>

<template>
  <div class="community-container">
    <!-- 헤더 섹션 -->
    <section class="header-section">
      <h1 class="page-title">커뮤니티</h1>
      
      <!-- 영화 정보 -->
      <div v-if="movieLoading" class="movie-info-loading">
        영화 정보를 불러오는 중...
      </div>
      
      <div v-else-if="movie" class="movie-info-card">
        <div class="movie-poster">
          <img v-if="movie.poster_path" :src="posterUrl(movie.poster_path)" alt="poster" />
          <div v-else class="no-poster">No Image</div>
        </div>
        
        <div class="movie-details">
          <h2 class="movie-title">{{ movie.title }}</h2>
          <p class="movie-meta" v-if="movie.original_title">{{ movie.original_title }}</p>
          <div class="movie-stats">
            <span>⭐ {{ movie.vote_average }}</span>
            <span>💬 리뷰 {{ reviews.length }}개</span>
          </div>
          
          <button @click="goCreate" class="write-review-btn">
            ✍️ 리뷰 작성하기
          </button>
        </div>
      </div>
    </section>

    <!-- 리뷰 목록 섹션 -->
    <section class="reviews-section">
      <h3 class="section-title">리뷰 목록</h3>
      
      <p v-if="loading" class="loading-text">리뷰를 불러오는 중...</p>

      <div v-if="reviews.length" class="reviews-list">
        <div v-for="r in reviews" :key="r.id" class="review-card">
          <div class="review-header">
            <div class="user-info">
              <span class="username">{{ r.username }}</span>
              <span class="rating">⭐ {{ r.rating }}</span>
            </div>
            <button @click="goDetail(r.id)" class="detail-btn">
              상세보기
            </button>
          </div>
          
          <div class="review-content">{{ r.content }}</div>
          
          <div class="review-date">{{ r.created_at }}</div>
        </div>
      </div>

      <div v-else-if="!loading" class="empty-state">
        <div class="empty-icon">💭</div>
        <p>아직 리뷰가 없어요.</p>
        <p class="empty-subtitle">첫 리뷰를 작성해보세요!</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.community-container {
  width: 100%;
  min-height: 100vh;
  background-color: #000000;
  padding-bottom: 60px;
}

/* 헤더 섹션 */
.header-section {
  padding: 40px 50px;
  background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%);
  border-bottom: 1px solid #222;
}

.page-title {
  font-size: 42px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 30px;
  text-align: center;
}

/* 영화 정보 카드 */
.movie-info-card {
  display: flex;
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
  background: #141414;
  border-radius: 16px;
  padding: 30px;
  border: 1px solid #282828;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
}

.movie-poster {
  flex-shrink: 0;
  width: 200px;
  height: 300px;
  border-radius: 12px;
  overflow: hidden;
  background: #222;
  display: flex;
  align-items: center;
  justify-content: center;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-poster {
  color: #666;
  font-size: 14px;
}

.movie-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.movie-title {
  font-size: 32px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 10px;
}

.movie-meta {
  font-size: 16px;
  color: #888;
  margin-bottom: 20px;
}

.movie-stats {
  display: flex;
  gap: 20px;
  font-size: 16px;
  color: #e5e5e5;
  margin-bottom: 30px;
}

.write-review-btn {
  align-self: flex-start;
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

.write-review-btn:hover {
  background-color: #1ed760;
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(29, 185, 84, 0.6);
}

.movie-info-loading {
  text-align: center;
  padding: 40px;
  color: #888;
  font-size: 16px;
}

/* 리뷰 섹션 */
.reviews-section {
  max-width: 1200px;
  margin: 0 auto;
  padding: 40px 50px;
}

.section-title {
  font-size: 28px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 2px solid #1DB954;
}

.loading-text {
  text-align: center;
  padding: 60px 20px;
  color: #888;
  font-size: 16px;
}

/* 리뷰 리스트 */
.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-card {
  background: #000000;
  border: 1px solid #282828;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
}

.review-card:hover {
  border-color: #1DB954;
  box-shadow: 0 4px 20px rgba(29, 185, 84, 0.2);
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.user-info {
  display: flex;
  gap: 12px;
  align-items: center;
}

.username {
  font-weight: 700;
  font-size: 18px;
  color: #ffffff;
}

.rating {
  color: #1DB954;
  font-weight: 600;
  font-size: 16px;
}

.detail-btn {
  padding: 8px 16px;
  background-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.detail-btn:hover {
  background-color: #1DB954;
  color: #000000;
  border-color: #1DB954;
}

.review-content {
  color: #cccccc;
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 12px;
}

.review-date {
  color: #777;
  font-size: 13px;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
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
}

/* 반응형 */
@media (max-width: 768px) {
  .header-section {
    padding: 30px 20px;
  }

  .page-title {
    font-size: 32px;
  }

  .movie-info-card {
    flex-direction: column;
    padding: 20px;
  }

  .movie-poster {
    width: 100%;
    max-width: 300px;
    margin: 0 auto;
  }

  .movie-title {
    font-size: 24px;
    text-align: center;
  }

  .movie-meta {
    text-align: center;
  }

  .movie-stats {
    justify-content: center;
  }

  .write-review-btn {
    align-self: center;
  }

  .reviews-section {
    padding: 30px 20px;
  }

  .section-title {
    font-size: 24px;
  }

  .review-card {
    padding: 16px;
  }
}
</style>
