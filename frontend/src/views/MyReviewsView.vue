<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { favoritesApi } from '@/api/favorites'
import { reviewsApi } from '@/api/reviews'

const router = useRouter()
const loading = ref(false)
const reviews = ref([])
const searchQuery = ref('')
const sortOption = ref('date_desc')

const filteredReviews = computed(() => {
  let result = [...reviews.value]

  // 1) 검색 (영화 제목)
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter((r) =>
      String(r.movie_title || '').toLowerCase().includes(query)
    )
  }

  // 2) 정렬
  result.sort((a, b) => {
    if (sortOption.value === 'rating_desc') return (b.rating ?? 0) - (a.rating ?? 0)
    if (sortOption.value === 'rating_asc') return (a.rating ?? 0) - (b.rating ?? 0)
    if (sortOption.value === 'title_asc') return String(a.movie_title || '').localeCompare(String(b.movie_title || ''))
    if (sortOption.value === 'title_desc') return String(b.movie_title || '').localeCompare(String(a.movie_title || ''))
    // 기본: 최신순
    return new Date(b.created_at) - new Date(a.created_at)
  })

  return result
})

async function loadMyReviews() {
  loading.value = true
  try {
    const { data } = await favoritesApi.getMyReviews()
    reviews.value = data
  } catch (e) {
    console.error('내 리뷰 목록 로드 실패:', e)
  } finally {
    loading.value = false
  }
}

function goToMovieDetail(movieId) {
  router.push({ name: 'movieDetail', params: { movieId } })
}

// NOTE: 네 라우터가 postDetail을 어떤 params로 받는지에 맞춰야 함.
// 지금은 params: { id } 로 되어있었는데, 네 코드에서 review.id를 넣고 있어서 우선 유지.
function goToPostDetail(id) {
  router.push({ name: 'postDetail', params: { id } })
}

async function deleteReview(reviewId) {
  if (!confirm('정말 삭제하시겠습니까?')) return
  try {
    await reviewsApi.remove(reviewId)
    reviews.value = reviews.value.filter((r) => r.id !== reviewId)
  } catch (e) {
    console.error('삭제 실패:', e)
    alert('삭제 실패: 오류가 발생했습니다.')
  }
}

onMounted(loadMyReviews)
</script>

<template>
  <div class="my-reviews-container">
    <section class="header-section">
      <h1 class="page-title">📝 내 글</h1>
      <p class="page-subtitle">내가 작성한 리뷰 목록</p>

      <div class="toolbar">
        <div class="search-sort-wrapper">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="영화 제목 검색..."
            class="search-input"
          />
          <select v-model="sortOption" class="sort-select">
            <option value="date_desc">최신순</option>
            <option value="rating_desc">별점 높은순</option>
            <option value="rating_asc">별점 낮은순</option>
            <option value="title_asc">이름순 (ㄱ-ㅎ)</option>
            <option value="title_desc">이름순 (ㅎ-ㄱ)</option>
          </select>
        </div>
      </div>
    </section>

    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>리뷰를 불러오는 중...</p>
    </div>

    <section v-else-if="filteredReviews.length > 0" class="reviews-section">
      <div class="reviews-list">
        <div v-for="review in filteredReviews" :key="review.id" class="review-card">
          <div class="review-header">
            <h3 class="movie-title">{{ review.movie_title }}</h3>
            <div class="review-meta">
              <span class="rating-badge">⭐ {{ review.rating ?? '-' }}</span>
              <span class="review-date">
                {{ review.created_at ? new Date(review.created_at).toLocaleDateString('ko-KR') : '-' }}
              </span>
            </div>
          </div>

          <div class="review-content">{{ review.content }}</div>

          <div class="review-footer">
            <!-- 필요하면 영화 상세로 이동 버튼도 살릴 수 있어 -->
            <!-- <button @click="goToMovieDetail(review.movie_id)" class="btn btn-detail">영화</button> -->

            <button @click="goToPostDetail(review.id)" class="btn btn-edit">수정</button>
            <button @click="deleteReview(review.id)" class="btn btn-delete">삭제</button>
            <button @click="goToPostDetail(review.id)" class="btn btn-detail">상세보기</button>
          </div>
        </div>
      </div>
    </section>

    <div v-else class="empty-state">
      <div class="empty-icon">✍️</div>
      <p>아직 작성한 리뷰가 없어요.</p>
      <p class="empty-subtitle">영화를 보고 첫 리뷰를 작성해보세요!</p>
      <button @click="router.push({ name: 'movies' })" class="go-movies-btn">
        영화 목록 보러가기
      </button>
    </div>
  </div>
</template>

<style scoped>
.my-reviews-container {
  width: 100%;
  min-height: 100vh;
  background-color: #000000;
  padding-bottom: 60px;
}

.header-section {
  padding: 60px 50px 20px;
  background: linear-gradient(180deg, #0a0a0a 0%, #000000 100%);
  border-bottom: 1px solid #222;
}

.toolbar {
  display: flex;
  justify-content: flex-end;
  margin-top: 30px;
}

.search-sort-wrapper {
  display: flex;
  gap: 12px;
}

.search-input {
  background: #141414;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 8px 12px;
  color: #fff;
  font-size: 14px;
  width: 200px;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #1DB954;
  background: #1a1a1a;
}

.sort-select {
  background: #141414;
  border: 1px solid #333;
  border-radius: 6px;
  padding: 8px 12px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  outline: none;
}

.sort-select:focus {
  border-color: #1DB954;
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

.reviews-section {
  max-width: 1000px;
  margin: 0 auto;
  padding: 40px 50px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-card {
  background: #141414;
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
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
  border-bottom: 1px solid #333;
  padding-bottom: 16px;
}

.movie-title {
  font-size: 20px;
  font-weight: 700;
  color: #ffffff;
  margin: 0;
}

.review-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rating-badge {
  display: inline-block;
  color: #FFD700;
  font-size: 16px;
  font-weight: 700;
}

.review-date {
  color: #666;
  font-size: 13px;
}

.review-content {
  color: #cccccc;
  font-size: 16px;
  line-height: 1.6;
  margin-bottom: 20px;
  white-space: pre-wrap;
}

.review-footer {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-detail {
  background-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.2);
}
.btn-detail:hover {
  background-color: #1DB954;
  color: #000;
  border-color: #1DB954;
}

.btn-edit {
  background-color: #333;
  color: #fff;
  border-color: #555;
}
.btn-edit:hover {
  background-color: #444;
  border-color: #666;
}

.btn-delete {
  background-color: transparent;
  color: #ff4444;
  border-color: #ff4444;
}
.btn-delete:hover {
  background-color: rgba(255, 68, 68, 0.1);
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

  .reviews-section {  
    padding: 30px 20px;
  }

  .review-card {
    padding: 16px;
  }
}
</style>
