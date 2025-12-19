<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const movieId = ref('')

function goMovie() {
  const id = Number(movieId.value)
  if (!id) return alert('movie_id를 숫자로 입력해줘!')
  router.push({ name: 'movieDetail', params: { movieId: id } })
}
</script>

<template>
  <div>
    <h1>MovieMate</h1>
    <p>현재 백엔드 API는 movie_id 기반(추천/리뷰)로 동작합니다.</p>

    <div style="display:flex; gap:10px; margin-top:12px;">
      <input v-model="movieId" placeholder="movie_id 예: 1" style="padding:10px; width:220px;" />
      <button @click="goMovie" style="padding:10px 14px; cursor:pointer;">이동</button>
    </div>
  </div>
</template>
