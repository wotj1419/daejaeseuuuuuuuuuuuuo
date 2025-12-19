<template>
  <div>
    <h2>추천 영화</h2>
    <p class="muted">클릭/좋아요 기록으로 자동 추천이 바뀝니다.</p>

    <div class="grid">
      <div v-for="m in recommended" :key="m.id" class="card" @click="openDetail(m)">
        <img :src="posterUrl(m)" class="poster" />
        <div class="meta">
          <div class="title">{{ m.title }}</div>
          <div class="sub">평점: {{ m.vote_average ?? '-' }}</div>
        </div>
      </div>
    </div>

    <hr class="sep" />

    <h3>탐색(인기 영화)</h3>
    <div class="grid">
      <div v-for="m in trending" :key="'t-' + m.id" class="card" @click="openDetail(m)">
        <img :src="posterUrl(m)" class="poster" />
        <div class="meta">
          <div class="title">{{ m.title }}</div>
          <div class="sub">인기도: {{ Math.round(m.popularity ?? 0) }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useRecommendationStore } from '../stores/recommendation'

const router = useRouter()
const rec = useRecommendationStore()
const movies = ref([])

onMounted(async () => {
  const base = import.meta.env.VITE_API_BASE_URL
  const res = await axios.get(`${base}/api/movies/`)
  movies.value = res.data
})

const recommended = computed(() => rec.recommend(movies.value, { limit: 20, exploreRate: 0.2 }))
const trending = computed(() =>
  [...movies.value].sort((a, b) => (b.popularity ?? 0) - (a.popularity ?? 0)).slice(0, 8),
)

function openDetail(movie) {
  rec.trackEvent({ type: 'view', movie })
  router.push({ name: 'movieDetail', params: { id: movie.id } })
}

function posterUrl(m) {
  return m.poster_url ?? m.posterPath ?? 'https://via.placeholder.com/300x450?text=No+Poster'
}
</script>

<style scoped>
.muted {
  color: #666;
  margin-bottom: 12px;
}
.sep {
  margin: 20px 0;
  border: none;
  border-top: 1px solid #eee;
}
.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}
.card {
  border: 1px solid #eee;
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
}
.poster {
  width: 100%;
  height: 220px;
  object-fit: cover;
  background: #f6f6f6;
}
.meta {
  padding: 10px;
}
.title {
  font-weight: 800;
}
.sub {
  color: #666;
  font-size: 12px;
  margin-top: 4px;
}
@media (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
