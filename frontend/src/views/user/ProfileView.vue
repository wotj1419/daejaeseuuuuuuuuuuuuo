<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { moviesApi } from '@/api/movies'
import { useAuthStore } from '@/stores/auth'
import { accountsApi } from '@/api/accounts'

const router = useRouter()
const authStore = useAuthStore()

const bio = ref('')
const favoriteMovieName = ref('')
const profileImage = ref('')
const savedMessage = ref('')
const profileError = ref('')
const searchLoading = ref(false)
const taste = ref(null)
const tasteLoading = ref(false)
const tasteError = ref('')
const similarUsers = ref([])
const similarLoading = ref(false)
const similarError = ref('')
const similarInfo = ref('')

async function loadProfile() {
  if (!authStore.isAuthenticated) {
    bio.value = ''
    favoriteMovieName.value = ''
    profileImage.value = ''
    profileError.value = ''
    return
  }

  try {
    const { data } = await accountsApi.getProfile()
    bio.value = data.bio || ''
    favoriteMovieName.value = data.favorite_movie_name || ''
    profileImage.value = data.profile_image || ''
    profileError.value = ''
  } catch (error) {
    console.error('프로필 데이터를 불러오지 못했습니다', error)
    profileError.value = '프로필 정보를 불러오는 중 오류가 발생했습니다.'
    bio.value = ''
    favoriteMovieName.value = ''
    profileImage.value = ''
  }
}

watch(
  () => authStore.user?.username,
  async () => {
    await loadProfile()
    await loadTaste()
    await loadSimilarUsers()
  },
  { immediate: true }
)

async function loadTaste() {
  if (!authStore.isAuthenticated) {
    taste.value = null
    tasteError.value = ''
    return
  }
  tasteLoading.value = true
  tasteError.value = ''
  try {
    const { data } = await accountsApi.getMyTaste()
    taste.value = data
  } catch (error) {
    console.error('취향 요약 불러오기 실패', error)
    tasteError.value = '취향 정보를 불러오지 못했습니다.'
    taste.value = null
  } finally {
    tasteLoading.value = false
  }
}

async function loadSimilarUsers(k = 6) {
  if (!authStore.isAuthenticated) {
    similarUsers.value = []
    similarError.value = ''
    similarInfo.value = '로그인하면 비슷한 취향의 사용자를 보여드릴게요.'
    return
  }
  similarLoading.value = true
  similarError.value = ''
  similarInfo.value = ''
  try {
    const { data } = await accountsApi.getSimilarUsers({ k: 3 })
    similarUsers.value = (data.results || []).slice(0, 3)
    if (data.reason === 'not_enough_likes') {
      similarInfo.value = '좋아요한 영화가 5개 이상이어야 취향을 분석할 수 있어요.'
      similarUsers.value = []
    } else if (!similarUsers.value.length) {
      similarInfo.value = '비슷한 취향을 가진 사용자를 아직 찾지 못했어요.'
    }
  } catch (error) {
    console.error('유사 취향 유저 불러오기 실패', error)
    similarError.value = '비슷한 취향 유저를 불러오지 못했습니다.'
    similarInfo.value = ''
    similarUsers.value = []
  } finally {
    similarLoading.value = false
  }
}

async function saveProfile() {
  if (!authStore.isAuthenticated) {
    alert('로그인 후에 프로필 정보를 저장할 수 있습니다.')
    return
  }

  try {
    await accountsApi.updateProfile({
      bio: bio.value,
      favorite_movie_name: favoriteMovieName.value,
      profile_image: profileImage.value,
    })
    savedMessage.value = '저장 완료!'
    setTimeout(() => (savedMessage.value = ''), 1200)
    profileError.value = ''
  } catch (error) {
    console.error('프로필 저장 오류', error)
    profileError.value = '프로필 저장에 실패했습니다. 다시 시도해주세요.'
  }
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

const displayName = computed(() => authStore.user?.username || 'Guest')

function handleImageChange(event) {
  const file = event.target.files?.[0]
  if (!file) return

  const maxSize = 2 * 1024 * 1024 // 2MB
  if (file.size > maxSize) {
    alert('이미지 크기가 2MB를 초과할 수 없습니다.')
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    profileImage.value = reader.result
  }
  reader.readAsDataURL(file)
}

function clearProfileImage() {
  profileImage.value = ''
}

function formatDate(value) {
  if (!value) return ''
  return new Date(value).toLocaleString('ko-KR', { dateStyle: 'medium', timeStyle: 'short' })
}

function posterUrl(path) {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w500${path}`
}

function formatGenreText(genres) {
  const names = (genres || [])
    .map((genre) => genre?.name)
    .filter(Boolean)
    .slice(0, 5)
  return names.join(', ')
}
</script>

<template>
  <div class="profile-container">
    <div class="profile-header">
      <div class="profile-avatar">
        <img v-if="profileImage" :src="profileImage" alt="profile" />
        <span v-else>{{ displayName.charAt(0).toUpperCase() }}</span>
      </div>
      <h1 class="profile-name">{{ displayName }}님의 공간</h1>
      <p class="profile-welcome">취향을 담은 나만의 프로필을 꾸며보세요 🎞️</p>
    </div>

    <div v-if="profileError" class="error-message">{{ profileError }}</div>

    <div class="profile-grid">
      <!-- ✏️ 기본 정보 설정 섹션 -->
      <section class="profile-card settings-card">
        <div class="card-header">
          <span class="card-icon">🧩</span>
          <h3>기본 정보</h3>
        </div>

        <div class="form-group avatar-group">
          <label>프로필 이미지</label>
          <div class="avatar-row">
            <div class="avatar-preview">
              <img v-if="profileImage" :src="profileImage" alt="profile preview" />
              <span v-else>{{ displayName.charAt(0).toUpperCase() }}</span>
            </div>
            <div class="avatar-actions">
              <label class="upload-btn">
                <input type="file" accept="image/*" @change="handleImageChange" hidden />
                이미지 선택
              </label>
              <button v-if="profileImage" type="button" class="ghost-btn" @click="clearProfileImage">
                제거
              </button>
              <p class="input-hint">2MB 이하 이미지를 업로드하거나 기존 이미지를 제거할 수 있습니다.</p>
            </div>
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

    <section class="profile-card taste-card">
      <div class="card-header">
        <span class="card-icon">??</span>
        <h3>?? ?? & ??? ??</h3>
      </div>

      <div v-if="tasteLoading" class="info-message">?? ??? ???? ?????</div>
      <div v-else-if="tasteError" class="error-message">{{ tasteError }}</div>
      <div v-else-if="taste?.reason === 'not_enough_likes'">
        ???? ??? ?? ???? ?? ?? ??? ?? ? ???. ???? 5? ?? ??????.
      </div>
      <div v-else-if="taste">
        <p class="taste-summary">{{ taste.taste_summary }}</p>
        <div class="chip-row" v-if="taste.top_genres?.length">
          <span v-for="g in taste.top_genres" :key="g.name" class="genre-chip">
            {{ g.name }} ? {{ ((g.score || 0) * 100).toFixed(0) }}%
          </span>
        </div>
        <p class="taste-meta">
          ??? {{ taste.liked_movies_count }}? ? ???? {{ formatDate(taste.updated_at) }}
        </p>
      </div>

      <div class="similar-block">
        <div class="similar-header-row">
          <h4>비슷한 취향을 가진 사용자</h4>
          <span class="mini-text" v-if="similarUsers.length">총 {{ similarUsers.length }}명</span>
        </div>
        <div v-if="similarLoading" class="info-message">비슷한 유저를 찾는 중입니다…</div>
        <div v-else-if="similarError" class="error-message">{{ similarError }}</div>
        <div v-else-if="similarInfo" class="info-message">{{ similarInfo }}</div>
        <div v-else class="similar-list">
          <button
            v-for="u in similarUsers"
            :key="u.username"
            type="button"
            class="similar-card"
            @click="router.push({ name: 'movieShare', query: { username: u.username } })"
          >
            <div class="card-top-row">
              <div class="similar-avatar" v-if="u.profile_image">
                <img :src="u.profile_image" alt="profile" />
              </div>
              <div class="similar-avatar placeholder" v-else>
                {{ (u.username || 'U').charAt(0).toUpperCase() }}
              </div>
              <div class="card-meta">
                <div class="card-title-row">
                  <strong>{{ u.username }}</strong>
                  <span v-if="u.favorite_movie_name" class="mini-text">{{ u.favorite_movie_name }}</span>
                </div>
                <div class="card-score-row">
                  <span class="score-pill">유사도 {{ Math.round((u.similarity || 0) * 100) }}%</span>
                  <span class="info-pill">공통 좋아요 {{ u.common_likes_count || 0 }}개</span>
                  <span class="info-pill">좋아요 {{ u.liked_movies_count || 0 }}개</span>
                </div>
                <p class="mini-text" v-if="u.bio">{{ u.bio }}</p>
              </div>
            </div>
            <p class="genre-line" v-if="u.top_genres?.length">주요 장르: {{ formatGenreText(u.top_genres) }}</p>
            <p class="summary-text" v-if="u.taste_summary">{{ u.taste_summary }}</p>
            <div v-if="u.sample_titles?.length" class="sample-chip-row">
              <span v-for="title in u.sample_titles" :key="title" class="sample-chip">{{ title }}</span>
            </div>
            <div v-if="u.recommendations?.length" class="recommendations">
              <p class="recommend-label">이 사용자가 좋아했지만 내가 아직 보지 않은 영화</p>
              <div class="recommendation-row">
                <article
                  v-for="movie in u.recommendations"
                  :key="movie.tmdb_id || movie.id"
                  class="recommend-card"
                >
                  <div class="poster-wrapper">
                    <img
                      v-if="posterUrl(movie.poster_path)"
                      :src="posterUrl(movie.poster_path)"
                      :alt="movie.title"
                    />
                    <div v-else class="poster-placeholder">No Image</div>
                  </div>
                  <p>{{ movie.title }}</p>
                </article>
              </div>
            </div>
          </button>
        </div>
      </div>
    </section>

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
  overflow: hidden;
}

.profile-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-avatar span {
  display: inline-flex;
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

.avatar-group .avatar-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.avatar-preview {
  width: 90px;
  height: 90px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1db954, #1ed760);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: 800;
  color: #000;
  overflow: hidden;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  cursor: pointer;
  font-weight: 700;
  transition: all 0.2s ease;
}

.upload-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.ghost-btn {
  background: transparent;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.25);
  padding: 10px 14px;
  border-radius: 12px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.ghost-btn:hover {
  border-color: #1db954;
  color: #1db954;
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

.taste-card {
  margin-top: 20px;
}

.taste-summary {
  font-size: 1.05rem;
  color: #e8f5ed;
  line-height: 1.5;
  margin-bottom: 12px;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}

.genre-chip {
  padding: 8px 12px;
  border-radius: 12px;
  background: rgba(29, 185, 84, 0.12);
  color: #c6f3d7;
  font-size: 0.9rem;
  border: 1px solid rgba(29, 185, 84, 0.2);
}

.taste-meta {
  color: #9bb2a4;
  font-size: 0.9rem;
}

.similar-block {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.similar-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.similar-list {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}

.similar-card {
  width: 100%;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 20px;
  color: #f7f7f7;
  display: flex;
  flex-direction: column;
  gap: 14px;
  text-align: left;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.similar-card:hover {
  border-color: #1db954;
  transform: translateY(-2px);
  box-shadow: 0 12px 30px rgba(13, 88, 48, 0.25);
}

.card-top-row {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.similar-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1db954, #1ed760);
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  overflow: hidden;
  flex-shrink: 0;
}

.similar-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.similar-avatar.placeholder {
  font-size: 22px;
}

.card-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.card-title-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.card-title-row strong {
  font-size: 1.2rem;
}

.card-score-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.score-pill,
.info-pill {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(29, 185, 84, 0.15);
  color: #8ff7d6;
}

.info-pill {
  background: rgba(255, 255, 255, 0.08);
  color: #b2d8c0;
}

.genre-line,
.summary-text {
  margin: 0;
  color: #cfe2d0;
  font-size: 0.9rem;
  line-height: 1.4;
}

.sample-chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.sample-chip {
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: #e9f5ea;
  font-size: 0.85rem;
}

.recommendations {
  margin-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recommend-label {
  margin: 0;
  font-size: 0.85rem;
  color: #9cc6b5;
}

.recommendation-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}

.recommend-card {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 12px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  text-align: center;
  font-size: 0.8rem;
  color: #f4f7f2;
}

.recommend-card p {
  margin: 0;
}

.poster-wrapper {
  width: 100%;
  aspect-ratio: 2 / 3;
  border-radius: 10px;
  overflow: hidden;
  background: #111;
}

.poster-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #aaa;
  font-size: 0.75rem;
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
