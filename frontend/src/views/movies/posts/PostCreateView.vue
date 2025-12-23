<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reviewsApi } from '@/api/reviews'

const route = useRoute()
const router = useRouter()

const movieId = computed(() => Number(route.params.movieId))
const content = ref('')
const rating = ref(5)
const saving = ref(false)

async function submit() {
  if (!content.value.trim()) return alert('내용을 입력해줘!')
  if (rating.value < 1 || rating.value > 10) {
    return alert('평점은 1점에서 10점 사이여야 해!')
  }
  saving.value = true
  try {
    await reviewsApi.createByMovie(movieId.value, {
      content: content.value,
      rating: Number(rating.value),
    })
    router.push({ name: 'community', params: { movieId: movieId.value } })
  } catch (e) {
    console.error(e)
    alert('리뷰 작성 실패 (로그인/권한이 필요할 수 있어)')
  } finally {
    saving.value = false
  }
}

function cancel() {
  router.push({ name: 'community', params: { movieId: movieId.value } })
}
</script>

<template>
  <div class="create-container">
    <div class="create-card">
      <h1 class="page-title">✍️ 리뷰 작성</h1>
      
      <div class="form-section">
        <div class="form-group">
          <label class="form-label">리뷰 내용</label>
          <textarea 
            v-model="content" 
            placeholder="영화에 대한 생각을 자유롭게 작성해주세요..."
            class="review-textarea"
          ></textarea>
        </div>

        <div class="form-group">
          <label class="form-label">평점</label>
          <div class="rating-container">
            <select v-model="rating" class="rating-select">
              <option v-for="n in 10" :key="n" :value="n">{{ n }}점</option>
            </select>
            <span class="rating-display">/ 10</span>
            <div class="star-display">⭐ {{ rating }}</div>
          </div>
        </div>

        <div class="button-group">
          <button 
            @click="submit" 
            :disabled="saving" 
            class="submit-btn"
          >
            {{ saving ? '저장 중...' : '✨ 작성 완료' }}
          </button>
          <button 
            @click="cancel" 
            :disabled="saving"
            class="cancel-btn"
          >
            취소
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.create-container {
  width: 100%;
  min-height: 100vh;
  background-color: #000000;
  padding: 60px 20px;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.create-card {
  width: 100%;
  max-width: 800px;
  background: #141414;
  border: 1px solid #282828;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
}

.page-title {
  font-size: 36px;
  font-weight: 700;
  color: #ffffff;
  margin-bottom: 40px;
  text-align: center;
  padding-bottom: 20px;
  border-bottom: 2px solid #1DB954;
}

.form-section {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-label {
  font-size: 18px;
  font-weight: 700;
  color: #e5e5e5;
  letter-spacing: -0.3px;
}

.review-textarea {
  width: 100%;
  min-height: 200px;
  padding: 16px;
  background-color: #000000;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  font-size: 16px;
  color: #ffffff;
  font-family: 'Noto Sans KR', sans-serif;
  line-height: 1.6;
  resize: vertical;
  transition: all 0.3s ease;
}

.review-textarea::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.review-textarea:focus {
  outline: none;
  border-color: #1DB954;
  background-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 20px rgba(29, 185, 84, 0.2);
}

.rating-container {
  display: flex;
  align-items: center;
  gap: 16px;
}

.rating-select {
  width: 120px;
  padding: 14px;
  background-color: #000000;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  font-size: 18px;
  color: #ffffff;
  text-align: center;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 14px center;
  background-size: 16px;
}

.rating-select option {
  background-color: #000000;
  color: #ffffff;
}

.rating-select:focus {
  outline: none;
  border-color: #1DB954;
  background-color: rgba(255, 255, 255, 0.08);
  box-shadow: 0 0 15px rgba(29, 185, 84, 0.2);
}

.rating-display {
  font-size: 18px;
  color: #888;
  font-weight: 500;
}

.star-display {
  padding: 8px 16px;
  background: linear-gradient(135deg, #1DB954 0%, #169B43 100%);
  color: #000000;
  border-radius: 20px;
  font-size: 16px;
  font-weight: 700;
  box-shadow: 0 2px 10px rgba(29, 185, 84, 0.3);
}

.button-group {
  display: flex;
  gap: 16px;
  margin-top: 20px;
  padding-top: 30px;
  border-top: 1px solid #282828;
}

.submit-btn {
  flex: 1;
  padding: 16px 32px;
  background-color: #1DB954;
  color: #000000;
  border: none;
  border-radius: 50px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 20px rgba(29, 185, 84, 0.4);
}

.submit-btn:hover:not(:disabled) {
  background-color: #1ed760;
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(29, 185, 84, 0.6);
}

.submit-btn:active:not(:disabled) {
  transform: translateY(0);
}

.submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.cancel-btn {
  padding: 16px 32px;
  background-color: rgba(255, 255, 255, 0.05);
  color: #e5e5e5;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-radius: 50px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #ffffff;
}

.cancel-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* 반응형 */
@media (max-width: 768px) {
  .create-container {
    padding: 30px 15px;
  }

  .create-card {
    padding: 24px;
  }

  .page-title {
    font-size: 28px;
    margin-bottom: 30px;
  }

  .form-label {
    font-size: 16px;
  }

  .review-textarea {
    min-height: 160px;
    font-size: 15px;
  }

  .rating-container {
    flex-wrap: wrap;
  }

  .button-group {
    flex-direction: column;
  }

  .submit-btn,
  .cancel-btn {
    width: 100%;
    font-size: 16px;
  }
}
</style>
