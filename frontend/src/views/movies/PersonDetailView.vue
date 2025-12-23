<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { moviesApi } from '@/api/movies'

const route = useRoute()
const router = useRouter()

const personId = ref(route.params.personId)
const person = ref(null)
const movies = ref([])
const loading = ref(false)
const error = ref(null)

async function loadPersonDetail() {
  loading.value = true
  error.value = null
  try {
    const { data } = await moviesApi.personDetail(personId.value)
    person.value = data.person
    movies.value = data.movies
  } catch (err) {
    console.error(err)
    error.value = '인물 정보를 불러올 수 없습니다.'
  } finally {
    loading.value = false
  }
}

function imageUrl(path, type = 'profile') {
  if (!path) return ''
  const size = type === 'profile' ? 'w300' : 'w185'
  return `https://image.tmdb.org/t/p/${size}${path}`
}

onMounted(() => {
  loadPersonDetail()
})

watch(() => route.params.personId, (newId) => {
  if (newId) {
    personId.value = newId
    loadPersonDetail()
    window.scrollTo(0, 0)
  }
})

function goBack() {
  router.back()
}
</script>

<template>
  <div class="person-detail-container">
    <button @click="goBack" class="back-btn">
      <span class="arrow">←</span> 뒤로가기
    </button>
    <div v-if="loading" class="loading">정보를 불러오는 중...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="person" class="content">
      <div class="profile-header">
        <div class="profile-photo">
          <img v-if="person.profile_path" :src="imageUrl(person.profile_path)" :alt="person.name" />
          <div v-else class="no-photo">👤</div>
        </div>
        <div class="profile-info">
          <h1>{{ person.name }}</h1>
          <div class="meta">
            <p v-if="person.birthday">🎂 생일: {{ person.birthday }}</p>
            <p v-if="person.place_of_birth">📍 출생지: {{ person.place_of_birth }}</p>
          </div>
          <div class="biography" v-if="person.biography">
            <h3>주요 생애</h3>
            <p>{{ person.biography }}</p>
          </div>
        </div>
      </div>

      <section class="movies-section">
        <h2 class="section-title">🎬 출연 영화</h2>
        <div v-if="movies.length" class="movies-grid">
          <div 
            v-for="movie in movies" 
            :key="movie.id" 
            class="movie-card"
            @click="router.push({ name: 'movieDetail', params: { movieId: movie.id } })"
          >
            <div class="movie-poster">
              <img v-if="movie.poster_path" :src="imageUrl(movie.poster_path, 'poster')" alt="poster" />
              <div v-else class="no-poster">No Image</div>
            </div>
            <div class="movie-info">
              <div class="movie-title">{{ movie.title }}</div>
              <div class="movie-character" v-if="movie.character">as {{ movie.character }}</div>
              <div class="movie-meta">
                 <span>⭐ {{ movie.vote_average?.toFixed(1) }}</span>
                 <span>📅 {{ movie.release_date?.split('-')[0] }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="no-data">출연 영화 정보가 없습니다.</div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.person-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 20px;
}

.profile-header {
  display: flex;
  gap: 50px;
  margin-bottom: 80px;
  flex-wrap: wrap;
}

.profile-photo {
  flex-shrink: 0;
  width: 300px;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
  background: #222;
  display: flex;
  align-items: center;
  justify-content: center;
}

.profile-photo img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-photo {
  font-size: 8rem;
  color: #444;
}

.profile-info {
  flex: 1;
  min-width: 300px;
}

.profile-info h1 {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 20px;
  color: #fff;
}

.meta {
  margin-bottom: 30px;
  font-size: 1.1rem;
  color: #aaa;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.biography h3 {
  font-size: 1.5rem;
  color: #fff;
  margin-bottom: 15px;
}

.biography p {
  line-height: 1.8;
  color: #ccc;
  font-size: 1.1rem;
  white-space: pre-wrap;
}

.movies-section {
  margin-top: 40px;
}

.section-title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 40px;
  color: #fff;
}

.movies-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 30px;
}

.movie-card {
  background: #181818;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid #282828;
}

.movie-card:hover {
  transform: translateY(-10px);
  border-color: #1db954;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}

.movie-poster {
  width: 100%;
  aspect-ratio: 2 / 3;
  background: #222;
  overflow: hidden;
}

.movie-poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.movie-card:hover .movie-poster img {
  transform: scale(1.1);
}

.movie-info {
  padding: 15px;
}

.movie-title {
  font-size: 1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.movie-character {
  font-size: 0.85rem;
  color: #1db954;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.movie-meta {
  display: flex;
  justify-content: space-between;
  font-size: 0.85rem;
  color: #888;
}

.back-btn {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  padding: 10px 20px;
  border-radius: 30px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  margin-bottom: 30px;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: #1db954;
  color: #1db954;
  transform: translateX(-5px);
}

.arrow {
  font-size: 1.2rem;
}

.loading { text-align: center; padding: 100px; font-size: 1.5rem; color: #1db954; }
.error { text-align: center; padding: 100px; color: #ff4444; }
.no-data { text-align: center; color: #888; padding: 40px; }

@media (max-width: 768px) {
  .profile-header { flex-direction: column; align-items: center; text-align: center; }
  .profile-photo { width: 220px; }
  .profile-info h1 { font-size: 2.5rem; }
}
</style>
