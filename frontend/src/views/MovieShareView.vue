<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { favoritesApi } from '@/api/favorites'

const router = useRouter()
const route = useRoute()
const searchUsername = ref(route.query.username || '')
const favorites = ref([])
const loading = ref(false)
const error = ref('')
const infoMessage = ref('')

function posterUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w500${path}`
}

function goToMovieDetail(tmdbId) {
  router.push({ name: 'movieDetail', params: { movieId: tmdbId } })
}

async function searchFavorites({ updateQuery = true } = {}) {
  const username = searchUsername.value.trim()
  if (!username) {
    error.value = '사용자 아이디를 입력해 주세요.'
    favorites.value = []
    infoMessage.value = ''
    return
  }

  if (updateQuery) {
    router.replace({ query: { username } })
  }

  loading.value = true
  error.value = ''
  infoMessage.value = ''
  favorites.value = []

  try {
    const { data } = await favoritesApi.getUserFavorites(username)
    favorites.value = data
    if (!data.length) {
      infoMessage.value = '좋아요한 영화가 아직 없습니다.'
    }
  } catch (err) {
    console.error('유저 좋아요 목록 조회 실패:', err)
    if (err.response?.status === 404) {
      error.value = '해당 사용자를 찾을 수 없습니다.'
    } else {
      error.value = '좋아요한 영화 목록을 불러오는 중 오류가 발생했습니다.'
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  if (searchUsername.value) {
    searchFavorites({ updateQuery: false })
  }
})
</script>

<template>
  <div class="share-page">
    <section class="share-intro">
      <div>
        <h1>영화 공유</h1>
        <p>관심 있는 유저의 좋아요 목록을 확인하고, 함께 감상할 영화를 발견해보세요.</p>
      </div>
      <div class="share-search">
        <input
          v-model="searchUsername"
          @keyup.enter="searchFavorites"
          placeholder="예) movielover123"
        />
        <button @click="searchFavorites" :disabled="loading">
          {{ loading ? '조회 중…' : '검색' }}
        </button>
      </div>
    </section>

    <div v-if="error" class="error-message">{{ error }}</div>
    <div v-else-if="infoMessage" class="info-message">{{ infoMessage }}</div>

    <div v-if="loading" class="loading-row">
      <span>좋아요한 영화 목록을 불러오는 중입니다…</span>
    </div>

    <div v-if="favorites.length" class="movies-grid">
      <div
        v-for="movie in favorites"
        :key="movie.tmdb_id"
        class="movie-card"
        @click="goToMovieDetail(movie.tmdb_id)"
      >
        <div class="poster">
          <img v-if="movie.poster_path" :src="posterUrl(movie.poster_path)" alt="poster" />
          <div v-else class="noimg">No Image</div>
        </div>
        <div class="movie-info">
          <div class="title">{{ movie.title }}</div>
          <div class="meta">
            <span>★ {{ movie.vote_average?.toFixed(1) || '-' }}</span>
            <span>{{ movie.release_date?.substring(0, 4) || '-' }}</span>
          </div>
          <p v-if="movie.ai_reason" class="reason">「{{ movie.ai_reason }}」</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.share-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 120px 40px 80px;
  color: #fff;
}

.share-intro {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 40px;
}

.share-intro h1 {
  font-size: 2.4rem;
  font-weight: 800;
}

.share-intro p {
  color: #bbb;
  max-width: 540px;
}

.share-search {
  display: flex;
  gap: 12px;
}

.share-search input {
  padding: 14px 18px;
  border-radius: 999px;
  border: 1px solid #555;
  background-color: rgba(255, 255, 255, 0.04);
  color: #fff;
  min-width: 280px;
}

.share-search button {
  border: none;
  border-radius: 999px;
  padding: 0 32px;
  background: #1db954;
  color: #000;
  font-weight: 700;
  cursor: pointer;
}

.share-search button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message,
.info-message {
  color: #ff6b6b;
  text-align: center;
  margin-bottom: 20px;
}

.info-message {
  color: #bbb;
}

.loading-row {
  text-align: center;
  color: #ccc;
  margin-bottom: 20px;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 24px;
}

.movie-card {
  background: #151515;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid #222;
}

.movie-card:hover {
  transform: translateY(-6px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
  border-color: #1db954;
}

.poster {
  aspect-ratio: 2 / 3;
  background: #222;
  overflow: hidden;
}

.poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.noimg {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
}

.movie-info {
  padding: 16px;
}

.title {
  font-weight: 700;
  margin-bottom: 10px;
}

.meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
  color: #999;
  margin-bottom: 10px;
}

.reason {
  font-size: 0.85rem;
  color: #a8e8ff;
}

@media (max-width: 768px) {
  .share-page {
    padding: 100px 20px 60px;
  }

  .share-intro {
    justify-content: flex-start;
  }

  .share-search input {
    flex: 1;
    min-width: 0;
  }
}
</style>
