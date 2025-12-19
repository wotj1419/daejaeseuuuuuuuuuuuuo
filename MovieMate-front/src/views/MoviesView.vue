<script setup>
import { computed, onMounted, ref } from 'vue'
import { moviesApi } from '@/api/movies'

const loading = ref(false)
const error = ref(null)
const allMovies = ref([])

const q = ref('')

// TMDB poster_path가 상대경로일 때 보정
function posterUrl(poster_path) {
  if (!poster_path) return ''
  if (poster_path.startsWith('http')) return poster_path
  return `https://image.tmdb.org/t/p/w500${poster_path}`
}

const movies = computed(() => {
  const query = q.value.trim().toLowerCase()
  if (!query) return allMovies.value

  return allMovies.value.filter((m) => {
    const title = (m.title || '').toLowerCase()
    const overview = (m.overview || '').toLowerCase()
    return title.includes(query) || overview.includes(query)
  })
})

async function loadMovies() {
  loading.value = true
  error.value = null
  try {
    // ✅ 백엔드 영화목록 API 호출
    const { data } = await moviesApi.list()

    // DRF pagination 쓰는 경우 { results: [...] } 형태일 수 있어서 둘 다 처리
    allMovies.value = Array.isArray(data) ? data : (data.results || [])
  } catch (e) {
    console.error(e)
    error.value = '영화 목록 API를 불러오지 못했어요. (엔드포인트/서버/CORS 확인)'
  } finally {
    loading.value = false
  }
}

onMounted(loadMovies)
</script>

<template>
  <div>
    <h2>영화 목록</h2>
    <p style="color:#666;">
      
    </p>

    <div class="search">
      <input v-model="q" placeholder="제목/줄거리로 검색" />
    
 
    </div>

    <p v-if="loading">불러오는 중...</p>
    <p v-if="error" style="color:#c00;">{{ error }}</p>

    <div class="grid" v-if="!loading && movies.length">
      <div v-for="m in movies" :key="m.id" class="card">
        <div class="poster">
          <img v-if="m.poster_path" :src="posterUrl(m.poster_path)" alt="poster" />
          <div v-else class="noimg">No Image</div>
        </div>

        <div class="title">{{ m.title }}</div>

        <div class="meta">
          <span>⭐ {{ m.vote_average ?? '-' }}</span>
          <span>🔥 {{ m.popularity ?? '-' }}</span>
        </div>

        <p class="overview" v-if="m.overview">{{ m.overview }}</p>

        <!-- 너 기존 구조로 연결(원하면) -->
        <div class="actions">
          <RouterLink :to="{ name: 'movieDetail', params: { movieId: m.id } }">상세 정보</RouterLink>
          <RouterLink :to="{ name: 'community', params: { movieId: m.id } }">리뷰</RouterLink>
        </div>
      </div>
    </div>

    <p v-else-if="!loading && !error">영화 데이터가 비어있어요.</p>
  </div>
</template>

<style scoped>
.search { display:flex; gap:10px; align-items:center; margin:12px 0; flex-wrap:wrap; }
.search input { padding:10px; width:320px; border:1px solid #ddd; border-radius:10px; }
.count { color:#666; font-size:14px; }
button { padding:10px 14px; cursor:pointer; }

.grid { display:grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap:12px; margin-top:12px; }
.card { border:1px solid #eee; border-radius:12px; padding:10px; }
.poster { width:100%; height:280px; border-radius:10px; overflow:hidden; background:#f4f4f4; display:flex; align-items:center; justify-content:center; }
.poster img { width:100%; height:100%; object-fit:cover; }
.noimg { color:#777; font-size:14px; }
.title { margin-top:10px; font-weight:800; }
.meta { margin-top:6px; color:#555; font-size:14px; display:flex; justify-content:space-between; }
.overview { margin-top:8px; color:#666; font-size:13px; line-height:1.35; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden; }
.actions { display:flex; gap:10px; margin-top:10px; }
.actions a { text-decoration:none; color:#333; border:1px solid #ddd; padding:6px 10px; border-radius:10px; }
</style>
