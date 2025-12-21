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
  <div class="profile-container">
    <div class="profile-header">
      <div class="profile-avatar">
        {{ displayName.charAt(0).toUpperCase() }}
      </div>
      <h1 class="profile-name">{{ displayName }}님의 공간</h1>
      <p class="profile-welcome">취향을 담은 나만의 프로필을 꾸며보세요 🎞️</p>
    </div>

    <div class="profile-grid">
      <!-- ✏️ 기본 정보 설정 섹션 -->
      <section class="profile-card settings-card">
        <div class="card-header">
          <span class="card-icon">👤</span>
          <h3>기본 정보</h3>
        </div>

        <div class="form-group">
          <label>닉네임</label>
          <div class="input-wrapper">
            <input v-model="nickname" placeholder="멋진 닉네임을 입력하세요" />
          </div>
        </div>

        <div class="form-group">
          <label>소개</label>
          <div class="input-wrapper">
            <textarea v-model="bio" placeholder="나를 표현하는 한 줄 소개를 적어보세요." />
          </div>
        </div>

        <div class="form-group">
          <label>가장 좋아하는 영화 🪐</label>
          <div class="input-wrapper">
            <input v-model="favoriteMovieName" placeholder="예: 인터스텔라, 인셉션" />
          </div>
          <p class="input-hint">
            영화의 정확한 제목을 입력하면 바로가기 기능을 사용할 수 있습니다.
          </p>
        </div>

        <div class="actions">
          <button @click="saveProfile" class="save-btn">
            저장하기
          </button>
          <transition name="fade">
            <span class="saved-badge" v-if="savedMessage">✨ {{ savedMessage }}</span>
          </transition>
        </div>
      </section>

      <!-- 🚀 영화 허브 바로가기 섹션 -->
      <section class="profile-card shortcuts-card">
        <div class="card-header">
          <span class="card-icon">⚡</span>
          <h3>{{ displayName }}님의 무비 허브</h3>
        </div>
        
        <p class="shortcuts-desc">
          입력하신 <strong>"{{ favoriteMovieName || '인생 영화' }}"</strong>와(과) 관련된 페이지로 빠르게 이동합니다.
        </p>

        <div class="shortcut-actions">
          <button @click="goFavMovie" :disabled="searchLoading || !favoriteMovieName" class="hub-btn">
            <span v-if="searchLoading" class="mini-spinner"></span>
            <span v-else>📍 인생 영화 상세 정보</span>
          </button>
          <button @click="goFavCommunity" :disabled="searchLoading || !favoriteMovieName" class="community-btn">
            <span v-if="searchLoading" class="mini-spinner"></span>
            <span v-else>💬 인생 영화 커뮤니티</span>
          </button>
        </div>
        
        <div v-if="!favoriteMovieName" class="warning-msg">
          먼저 가장 좋아하는 영화를 입력해주세요!
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.profile-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 60px 40px;
  min-height: 100vh;
  background-color: #000;
  color: #fff;
}

/* 프로필 헤더 */
.profile-header {
  text-align: center;
  margin-bottom: 50px;
  animation: fadeInDown 0.8s ease-out;
}

.profile-avatar {
  width: 100px;
  height: 100px;
  background: linear-gradient(135deg, #1db954, #1ed760);
  border-radius: 50%;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: 900;
  color: #000;
  box-shadow: 0 10px 30px rgba(29, 185, 84, 0.3);
}

.profile-name {
  font-size: 32px;
  font-weight: 800;
  margin-bottom: 8px;
}

.profile-welcome {
  color: #888;
  font-size: 16px;
}

/* 레이아웃 그리드 */
.profile-grid {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 30px;
}

/* 카드 공통 스타일 */
.profile-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border-radius: 24px;
  padding: 32px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.profile-card:hover {
  transform: translateY(-5px);
  border-color: rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 30px;
}

.card-icon {
  font-size: 24px;
}

.card-header h3 {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
}

/* 폼 요소 */
.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #aaa;
  margin-bottom: 10px;
  margin-left: 4px;
}

.input-wrapper {
  position: relative;
}

input, textarea {
  width: 100%;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 14px 20px;
  color: #fff;
  font-size: 15px;
  transition: all 0.3s;
}

input:focus, textarea:focus {
  outline: none;
  border-color: #1db954;
  background: rgba(29, 185, 84, 0.05);
  box-shadow: 0 0 15px rgba(29, 185, 84, 0.1);
}

textarea {
  min-height: 120px;
  resize: none;
}

.input-hint {
  font-size: 12px;
  color: #666;
  margin-top: 8px;
  margin-left: 4px;
}

/* 버튼 */
.actions {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-top: 40px;
}

.save-btn {
  padding: 14px 40px;
  background: #fff;
  color: #000;
  border: none;
  border-radius: 16px;
  font-weight: 800;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.save-btn:hover {
  background: #1db954;
  color: #fff;
  transform: translateY(-3px);
  box-shadow: 0 10px 20px rgba(29, 185, 84, 0.3);
}

.saved-badge {
  color: #1ed760;
  font-weight: 700;
  font-size: 14px;
}

/* 바로가기 섹션 */
.shortcuts-desc {
  color: #ccc;
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 30px;
}

.shortcut-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hub-btn, .community-btn {
  padding: 16px;
  border-radius: 16px;
  font-weight: 700;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid rgba(255, 255, 255, 0.1);
  text-align: center;
}

.hub-btn {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.hub-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: #1db954;
  color: #1db954;
}

.community-btn {
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
}

.community-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: #1db954;
  color: #1db954;
}

button:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.warning-msg {
  margin-top: 20px;
  font-size: 13px;
  color: #ff4757;
  text-align: center;
}

/* 애니메이션 */
@keyframes fadeInDown {
  from { opacity: 0; transform: translateY(-20px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.mini-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(29, 185, 84, 0.1);
  border-top-color: #1db954;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 모바일 대응 */
@media (max-width: 900px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
  .profile-container {
    padding: 40px 20px;
  }
}
</style>
