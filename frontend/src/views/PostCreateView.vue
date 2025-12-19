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
</script>

<template>
  <div>
    <h2>리뷰 작성 (movie_id: {{ movieId }})</h2>

    <textarea v-model="content" placeholder="리뷰 내용" style="width:100%; min-height:140px; padding:10px;"></textarea>

    <div style="display:flex; gap:10px; align-items:center; margin-top:10px;">
      <label>평점</label>
      <input v-model="rating" type="number" min="1" max="10" style="width:80px; padding:8px;" />
      <button @click="submit" :disabled="saving" style="padding:10px 14px; cursor:pointer;">
        {{ saving ? '저장 중...' : '작성' }}
      </button>
    </div>
  </div>
</template>
