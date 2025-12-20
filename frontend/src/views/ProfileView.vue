<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { moviesApi } from '@/api/movies'

const router = useRouter()

// 로컬 프로필(임시) - 백엔드 accounts API 붙이면 여기만 교체하면 됨
const nickname = ref(localStorage.getItem('profile_nickname') || 'Guest')
const bio = ref(localStorage.getItem('profile_bio') || '')
const favoriteMovieName = ref(localStorage.getItem('profile_fav_movieName') || '')

const savedMessage = ref('')
const searchLoading = ref(false)

function saveProfile() {
  localStorage.setItem('profile_nickname', nickname.value)
  localStorage.setItem('profile_bio', bio.value)
  localStorage.setItem('profile_fav_movieName', favoriteMovieName.value)
  savedMessage.value = '저장 완료!'
  setTimeout(() => (savedMessage.value = ''), 1200)
}

// 영화 이름으로 검색하여 tmdb_id를 찾는 함수
async function searchMovieByName(movieName) {
  if (!movieName || !movieName.trim()) {
    alert('관심 영화 이름을 입력해주세요!')
    return null
  }

  try {
    searchLoading.value = true
    const { data } = await moviesApi.search(movieName.trim())
    
    if (data.results && data.results.length > 0) {
      // 첫 번째 검색 결과 사용
      return data.results[0].tmdb_id
    } else {
      alert(`"${movieName}" 영화를 찾을 수 없습니다. 다른 이름으로 시도해주세요.`)
      return null
    }
  } catch (error) {
    console.error('영화 검색 오류:', error)
    alert('영화 검색 중 오류가 발생했습니다.')
    return null
  } finally {
    searchLoading.value = false
  }
}

async function goFavMovie() {
  const tmdbId = await searchMovieByName(favoriteMovieName.value)
  if (tmdbId) {
    router.push({ name: 'movieDetail', params: { movieId: tmdbId } })
  }
}

async function goFavCommunity() {
  const tmdbId = await searchMovieByName(favoriteMovieName.value)
  if (tmdbId) {
    router.push({ name: 'community', params: { movieId: tmdbId } })
  }
}

const displayName = computed(() => (nickname.value?.trim() ? nickname.value : 'Guest'))
</script>

<template>
  <div>
    <h2>프로필</h2>
    

    <section class="card">
      <h3>기본 정보</h3>

      <div class="row">
        <label>닉네임</label>
        <input v-model="nickname" placeholder="예: pak" />
      </div>

      <div class="row">
        <label>소개</label>
        <textarea v-model="bio" placeholder="한 줄 소개를 적어보세요." />
      </div>

      <div class="row">
        <label>관심 영화 (영화 이름)</label>
        <input v-model="favoriteMovieName" placeholder="예: 인터스텔라" />
        <p style="font-size: 12px; color: #666; margin-top: 4px;">
          영화의 한글 제목 또는 영문 제목을 입력하세요.
        </p>
      </div>

      <div class="actions">
        <button @click="saveProfile">저장</button>
        <span class="saved" v-if="savedMessage">{{ savedMessage }}</span>
      </div>
    </section>

    <section class="card">
      <h3>{{ displayName }}님의 바로가기</h3>
      <p style="color:#666; margin-top:6px;">
        관심 영화 이름을 입력해두면, 추천/리뷰 페이지로 빠르게 이동할 수 있어요.
      </p>

      <div class="actions">
        <button @click="goFavMovie" :disabled="searchLoading">
          {{ searchLoading ? '검색 중...' : '관심 영화 허브' }}
        </button>
        <button @click="goFavCommunity" :disabled="searchLoading">
          {{ searchLoading ? '검색 중...' : '관심 영화 커뮤니티' }}
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.card {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 14px;
  margin-top: 14px;
}
.row {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 12px;
}
label {
  font-weight: 700;
  color: #333;
}
input, textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 10px;
  font-size: 14px;
}
textarea {
  min-height: 90px;
  resize: vertical;
}
.actions {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: 14px;
}
button {
  padding: 10px 14px;
  cursor: pointer;
}
button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.saved {
  color: #2d7a2d;
  font-weight: 700;
}
</style>
