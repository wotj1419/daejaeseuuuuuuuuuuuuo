<template>
  <div v-if="movie">
    <div class="row">
      <img :src="posterUrl(movie)" class="detailPoster" />
      <div class="info">
        <h2>{{ movie.title }}</h2>
        <div class="muted">평점 {{ movie.vote_average ?? '-' }}</div>

        <div class="btns">
          <button class="btn" @click="likeMovie">좋아요</button>
          <button class="btn primary" @click="autoNext">자동으로 다음 보기</button>
        </div>

        <div v-if="movie.trailer_youtube_id" class="ytWrap">
          <iframe
            :src="`https://www.youtube.com/embed/${movie.trailer_youtube_id}`"
            width="100%"
            height="320"
            frameborder="0"
            allow="encrypted-media"
            allowfullscreen
          />
        </div>
      </div>
    </div>

    <hr class="sep" />

    <h3>다음 추천</h3>
    <div class="grid">
      <div v-for="m in nextList" :key="m.id" class="card" @click="goMovie(m)">
        <img :src="posterUrl(m)" class="poster" />
        <div class="meta">
          <div class="title">{{ m.title }}</div>
          <div class="sub">추천 기반</div>
        </div>
      </div>
    </div>
  </div>

  <div v-else class="muted">로딩중...</div>
</template>

<script setup>
import axios from 'axios'
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecommendationStore } from '../stores/recommendation'

const route = useRoute()
const router = useRouter()
const rec = useRecommendationStore()

const movie = ref(null)
const allMovies = ref([])
const enterTs = Date.now()

onMounted(async () => {
  const base = import.meta.env.VITE_API_BASE_URL
  const [mRes, listRes] = await Promise.all([
    axios.get(`${base}/api/movies/${route.params.id}/`),
    axios.get(`${base}/api/movies/`),
  ])
  movie.value = mRes.data
  allMovies.value = listRes.data

  // 상세 진입 view
  rec.trackEvent({ type: 'view', movie: movie.value })
})

onBeforeUnmount(() => {
  if (!movie.value) return
  const dwellSeconds = Math.floor((Date.now() - enterTs) / 1000)
  // 체류시간 반영
  rec.trackEvent({ type: 'view', movie: movie.value, dwellSeconds })
})

const nextList = computed(() => {
  const candidates = allMovies.value.filter((m) => m.id !== movie.value?.id)
  return rec.recommend(candidates, { limit: 8, exploreRate: 0.15 })
})

function likeMovie() {
  rec.trackEvent({ type: 'like', movie: movie.value })
}

function autoNext() {
  const next = nextList.value[0]
  if (!next) return
  goMovie(next)
}

function goMovie(m) {
  rec.trackEvent({ type: 'view', movie: m })
  router.push({ name: 'movieDetail', params: { id: m.id } })
}

function posterUrl(m) {
  return m.poster_url ?? m.posterPath ?? 'https://via.placeholder.com/300x450?text=No+Poster'
}
</script>

<style scoped>
.row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}
.detailPoster {
  width: 220px;
  height: 330px;
  object-fit: cover;
  border-radius: 12px;
  background: #f6f6f6;
}
.info {
  flex: 1;
}
.muted {
  color: #666;
}
.btns {
  margin: 12px 0;
  display: flex;
  gap: 8px;
}
.btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
}
.btn.primary {
  background: #111;
  color: white;
  border-color: #111;
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
  height: 200px;
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
.ytWrap {
  margin-top: 12px;
}
@media (max-width: 900px) {
  .row {
    flex-direction: column;
  }
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
