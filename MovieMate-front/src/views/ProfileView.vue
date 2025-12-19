<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 로컬 프로필(임시) - 백엔드 accounts API 붙이면 여기만 교체하면 됨
const nickname = ref(localStorage.getItem('profile_nickname') || 'Guest')
const bio = ref(localStorage.getItem('profile_bio') || '')
const favoriteMovieId = ref(localStorage.getItem('profile_fav_movieId') || '')

const savedMessage = ref('')

function saveProfile() {
  localStorage.setItem('profile_nickname', nickname.value)
  localStorage.setItem('profile_bio', bio.value)
  localStorage.setItem('profile_fav_movieId', favoriteMovieId.value)
  savedMessage.value = '저장 완료!'
  setTimeout(() => (savedMessage.value = ''), 1200)
}

function goFavMovie() {
  const id = Number(favoriteMovieId.value)
  if (!id) return alert('관심 movie_id를 숫자로 입력해줘!')
  router.push({ name: 'movieDetail', params: { movieId: id } })
}

function goFavCommunity() {
  const id = Number(favoriteMovieId.value)
  if (!id) return alert('관심 movie_id를 숫자로 입력해줘!')
  router.push({ name: 'community', params: { movieId: id } })
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
        <label>관심 영화(movie_id)</label>
        <input v-model="favoriteMovieId" placeholder="예: 1" />
      </div>

      <div class="actions">
        <button @click="saveProfile">저장</button>
        <span class="saved" v-if="savedMessage">{{ savedMessage }}</span>
      </div>
    </section>

    <section class="card">
      <h3>{{ displayName }}님의 바로가기</h3>
      <p style="color:#666; margin-top:6px;">
        관심 영화 ID를 입력해두면, 추천/리뷰 페이지로 빠르게 이동할 수 있어요.
      </p>

      <div class="actions">
        <button @click="goFavMovie">관심 영화 허브</button>
        <button @click="goFavCommunity">관심 영화 커뮤니티</button>
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
.saved {
  color: #2d7a2d;
  font-weight: 700;
}
</style>
