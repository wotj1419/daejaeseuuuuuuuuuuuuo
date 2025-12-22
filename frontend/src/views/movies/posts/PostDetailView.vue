<script setup>
import { onMounted, ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reviewsApi } from '@/api/reviews'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const id = Number(route.params.id)

const review = ref(null)
const editMode = ref(false)
const content = ref('')
const rating = ref(5)

// 작성자 본인 확인
const isAuthor = computed(() => {
  return authStore.user?.username && review.value?.username === authStore.user.username
})

async function load() {
  try {
    const { data } = await reviewsApi.detail(id)
    review.value = data
    content.value = data.content
    rating.value = data.rating
  } catch (e) {
    console.error(e)
    alert('리뷰 상세 불러오기 실패')
    router.push('/')
  }
}

async function save() {
  try {
    await reviewsApi.update(id, { content: content.value, rating: Number(rating.value) })
    editMode.value = false
    await load()
  } catch (e) {
    console.error(e)
    alert('수정 실패: 권한이 없거나 오류가 발생했습니다.')
  }
}

async function removeReview() {
  if (!confirm('정말 삭제하시겠습니까? 삭제된 리뷰는 복구할 수 없습니다.')) return
  try {
    await reviewsApi.remove(id)
    alert('리뷰가 삭제되었습니다.')
    router.back() // 또는 router.push('/')
  } catch (e) {
    console.error(e)
    alert('삭제 실패: 권한이 없거나 오류가 발생했습니다.')
  }
}

// 별점 표시용 로직
function getStars(score) {
  return '⭐'.repeat(Math.round(score))
}

onMounted(load)
</script>

<template>
  <div class="detail-container">
    <div v-if="review" class="content-wrapper">
      
      <!-- Header Section -->
      <section class="review-header">
        <div class="movie-info">
          <span class="movie-label">REVIEW FOR</span>
          <h1 class="movie-title">{{ review.movie_title || 'Unknown Movie' }}</h1>
        </div>
        
        <div class="author-meta">
          <div class="avatar">
            {{ review.username?.charAt(0).toUpperCase() }}
          </div>
          <div class="meta-text">
            <span class="username">{{ review.username }}</span>
            <span class="date">{{ new Date(review.created_at).toLocaleDateString('ko-KR') }}</span>
          </div>
          <div class="rating-display">
            <span class="star-icon">⭐</span>
            <span class="score">{{ review.rating }}</span>
            <span class="score-max">/ 10</span>
          </div>
        </div>
      </section>

      <!-- Content Section -->
      <section class="review-body">
        <div v-if="!editMode" class="view-mode">
          <div class="review-text">{{ review.content }}</div>
          
          <div class="action-buttons" v-if="isAuthor">
            <button @click="editMode = true" class="btn btn-edit">수정</button>
            <button @click="removeReview" class="btn btn-delete">삭제</button>
          </div>
        </div>

        <!-- Edit Mode -->
        <div v-else class="edit-mode card">
          <div class="form-group">
            <label>평점</label>
            <div class="rating-input-wrapper">
              <input v-model="rating" type="range" min="1" max="10" step="1" class="rating-slider" />
              <span class="rating-value">{{ rating }}</span>
            </div>
          </div>
          
          <div class="form-group">
            <label>내용</label>
            <textarea v-model="content" class="edit-textarea"></textarea>
          </div>

          <div class="edit-actions">
            <button @click="editMode = false" class="btn btn-cancel">취소</button>
            <button @click="save" class="btn btn-save">저장하기</button>
          </div>
        </div>
      </section>
      
      <!-- Footer -->
      <section class="review-footer">
        <button @click="router.back()" class="btn-back">
          ← 목록으로 돌아가기
        </button>
      </section>

    </div>
    
    <div v-else class="loading">
      <div class="spinner"></div>
    </div>
  </div>
</template>

<style scoped>
.detail-container {
  min-height: 100vh;
  background-color: #000000;
  padding: 60px 20px;
  display: flex;
  justify-content: center;
}

.content-wrapper {
  width: 100%;
  max-width: 800px;
  animation: fadeIn 0.5s ease;
}

/* Header */
.review-header {
  margin-bottom: 40px;
  border-bottom: 1px solid #333;
  padding-bottom: 30px;
}

.movie-label {
  color: #1DB954;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 8px;
  display: block;
}

.movie-title {
  font-size: 42px;
  font-weight: 800;
  color: white;
  margin: 0 0 24px 0;
  line-height: 1.2;
}

.author-meta {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #333 0%, #555 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 20px;
}

.meta-text {
  display: flex;
  flex-direction: column;
}

.username {
  color: white;
  font-weight: 600;
  font-size: 16px;
}

.date {
  color: #888;
  font-size: 13px;
}

.rating-display {
  margin-left: auto;
  background: rgba(29, 185, 84, 0.1);
  padding: 8px 16px;
  border-radius: 20px;
  display: flex;
  align-items: baseline;
  gap: 4px;
  border: 1px solid rgba(29, 185, 84, 0.3);
}

.star-icon {
  font-size: 18px;
}

.score {
  font-size: 24px;
  font-weight: 800;
  color: #1DB954;
}

.score-max {
  font-size: 14px;
  color: #888;
}

/* Body */
.review-body {
  margin-bottom: 60px;
  min-height: 200px;
}

.review-text {
  font-size: 18px;
  line-height: 1.8;
  color: #e5e5e5;
  white-space: pre-wrap;
  margin-bottom: 40px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #222;
}

.btn {
  padding: 10px 24px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-edit {
  background-color: #333;
  color: white;
}
.btn-edit:hover {
  background-color: #444;
}

.btn-delete {
  background-color: transparent;
  color: #ff4444;
  border: 1px solid #ff4444;
}
.btn-delete:hover {
  background-color: rgba(255, 68, 68, 0.1);
}

/* Edit Mode */
.edit-mode.card {
  background: #141414;
  padding: 30px;
  border-radius: 12px;
  border: 1px solid #333;
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  color: #888;
  font-size: 14px;
  margin-bottom: 10px;
}

.rating-input-wrapper {
  display: flex;
  align-items: center;
  gap: 20px;
}

.rating-slider {
  flex: 1;
  height: 6px;
  background: #333;
  border-radius: 3px;
  appearance: none;
  outline: none;
}

.rating-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  background: #1DB954;
  border-radius: 50%;
  cursor: pointer;
}

.rating-value {
  font-size: 24px;
  font-weight: 700;
  color: #1DB954;
  min-width: 40px;
  text-align: center;
}

.edit-textarea {
  width: 100%;
  min-height: 200px;
  background: #000;
  border: 1px solid #333;
  border-radius: 8px;
  padding: 16px;
  color: white;
  font-size: 16px;
  line-height: 1.6;
  resize: vertical;
}

.edit-textarea:focus {
  border-color: #1DB954;
  outline: none;
}

.edit-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn-save {
  background-color: #1DB954;
  color: black;
}
.btn-save:hover {
  background-color: #1ed760;
  transform: scale(1.02);
}

.btn-cancel {
  background-color: transparent;
  color: #aaa;
}
.btn-cancel:hover {
  color: white;
}

/* Footer */
.btn-back {
  background: transparent;
  border: none;
  color: #888;
  font-size: 15px;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-back:hover {
  color: #1DB954;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 50vh;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: #1DB954;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 768px) {
  .movie-title {
    font-size: 32px;
  }
  .review-text {
    font-size: 16px;
  }
  .detail-container {
    padding: 40px 20px;
  }
}
</style>
