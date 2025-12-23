<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { accountsApi } from '@/api/accounts'
import { favoritesApi } from '@/api/favorites'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const summary = ref(null)
const activeTab = ref('movies')
const loading = reactive({
  summary: false,
  movies: false,
  reviews: false,
  follows: false,
  suggestions: false,
  savingProfile: false,
})

const movies = ref([])
const reviews = ref([])
const followings = ref([])
const followers = ref([])
const suggestions = ref([])

const bio = ref('')
const favoriteMovieName = ref('')
const profileImage = ref('')
const statusMessage = ref('')
const errorMessage = ref('')

const posterUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w342${path}`
}

function setActiveTab(tab) {
  activeTab.value = tab
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

const displayName = computed(() => summary.value?.username || authStore.user?.username || '게스트')

async function loadSummary() {
  if (!isAuthenticated.value) return
  loading.summary = true
  try {
    const { data } = await accountsApi.getProfileSummary()
    summary.value = data
    bio.value = data.bio || ''
    favoriteMovieName.value = data.favorite_movie_name || ''
    profileImage.value = data.profile_image || ''
  } catch (error) {
    console.error('프로필 요약 불러오기 실패', error)
    errorMessage.value = '내 정보를 불러오는 중 문제가 발생했습니다.'
  } finally {
    loading.summary = false
  }
}

async function loadMovies() {
  if (!isAuthenticated.value || loading.movies) return
  loading.movies = true
  try {
    const { data } = await favoritesApi.getMyMovies()
    movies.value = data
  } catch (error) {
    console.error('내 영화 불러오기 실패', error)
  } finally {
    loading.movies = false
  }
}

async function loadReviews() {
  if (!isAuthenticated.value || loading.reviews) return
  loading.reviews = true
  try {
    const { data } = await favoritesApi.getMyReviews()
    reviews.value = data
  } catch (error) {
    console.error('내 글 불러오기 실패', error)
  } finally {
    loading.reviews = false
  }
}

async function loadFollowData() {
  if (!isAuthenticated.value || loading.follows) return
  loading.follows = true
  try {
    const [followingRes, followerRes] = await Promise.all([
      accountsApi.getFollowings(),
      accountsApi.getFollowers(),
    ])
    followings.value = followingRes.data
    followers.value = followerRes.data
  } catch (error) {
    console.error('팔로우 정보 불러오기 실패', error)
  } finally {
    loading.follows = false
  }
}

async function loadSuggestions() {
  if (!isAuthenticated.value || loading.suggestions) return
  loading.suggestions = true
  try {
    const { data } = await accountsApi.getUsers()
    suggestions.value = data
  } catch (error) {
    console.error('사용자 목록 불러오기 실패', error)
  } finally {
    loading.suggestions = false
  }
}

async function toggleFollow(username) {
  if (!isAuthenticated.value) {
    router.push({ name: 'login' })
    return
  }
  try {
    await accountsApi.toggleFollow(username)
    await Promise.all([loadFollowData(), loadSuggestions(), loadSummary()])
  } catch (error) {
    console.error('팔로우 토글 실패', error)
    alert(error.response?.data?.error || '팔로우 처리 중 오류가 발생했습니다.')
  }
}

async function removeMovie(tmdbId, event) {
  event?.stopPropagation()
  try {
    await favoritesApi.toggleFavorite(tmdbId)
    movies.value = movies.value.filter((m) => m.tmdb_id !== tmdbId)
  } catch (error) {
    console.error('영화 제거 실패', error)
  }
}

async function saveProfile() {
  if (!isAuthenticated.value) {
    router.push({ name: 'login' })
    return
  }
  loading.savingProfile = true
  statusMessage.value = ''
  try {
    await accountsApi.updateProfile({
      bio: bio.value,
      favorite_movie_name: favoriteMovieName.value,
      profile_image: profileImage.value,
    })
    statusMessage.value = '저장 완료!'
    await loadSummary()
  } catch (error) {
    console.error('프로필 저장 실패', error)
    alert('프로필 저장 중 문제가 발생했습니다.')
  } finally {
    loading.savingProfile = false
    setTimeout(() => (statusMessage.value = ''), 1200)
  }
}

function handleImageChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const maxSize = 2 * 1024 * 1024 // 2MB
  if (file.size > maxSize) {
    alert('이미지 크기는 2MB를 넘길 수 없습니다.')
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

function goLogin() {
  router.push({ name: 'login' })
}

function goToMovieDetail(movieId) {
  if (!movieId) return
  router.push({ name: 'movieDetail', params: { movieId } })
}

watch(
  isAuthenticated,
  (authed) => {
    if (authed) {
      loadSummary()
      loadMovies()
      loadReviews()
      loadFollowData()
      loadSuggestions()
    } else {
      summary.value = null
      movies.value = []
      reviews.value = []
      followings.value = []
      followers.value = []
      suggestions.value = []
    }
  },
  { immediate: true }
)

onMounted(() => {
  if (isAuthenticated.value) {
    loadSummary()
    loadMovies()
    loadReviews()
    loadFollowData()
    loadSuggestions()
  }
})
</script>

<template>
  <div class="hub">
    <section class="hero">
      <div class="avatar">
        <img v-if="profileImage" :src="profileImage" alt="profile" />
        <span v-else>{{ displayName.charAt(0).toUpperCase() || 'U' }}</span>
      </div>
      <p class="eyebrow">My Page</p>
      <h1>{{ displayName }}님의 큐레이션</h1>
      <p class="muted hero-desc">
        좋아한 영화, 남긴 글, 그리고 연결된 사람들을 한눈에 관리하세요.
      </p>
      <div class="stats">
        <div class="stat">
          <span class="label">팔로워</span>
          <strong>{{ summary?.follower_count ?? 0 }}</strong>
        </div>
        <div class="stat">
          <span class="label">팔로잉</span>
          <strong>{{ summary?.following_count ?? 0 }}</strong>
        </div>
      </div>
      <div v-if="!isAuthenticated" class="hero-cta">
        <p>로그인 후 내 페이지를 사용할 수 있습니다.</p>
        <button class="primary" @click="goLogin">로그인하기</button>
      </div>
    </section>

    <div class="tabbar">
      <button
        :class="{ active: activeTab === 'movies' }"
        @click="setActiveTab('movies')"
      >
        내 영화
      </button>
      <button
        :class="{ active: activeTab === 'reviews' }"
        @click="setActiveTab('reviews')"
      >
        내 글
      </button>
      <button
        :class="{ active: activeTab === 'follows' }"
        @click="setActiveTab('follows')"
      >
        내 친구
      </button>
      <button
        :class="{ active: activeTab === 'profile' }"
        @click="setActiveTab('profile')"
      >
        프로필 수정
      </button>
    </div>

    <section v-show="activeTab === 'movies'" id="section-movies" class="panel">
      <header class="panel-heading">
        <div>
          <p class="eyebrow">Collection</p>
          <h2>내 영화</h2>
          <p class="muted">좋아요한 영화들을 한 번에 모아봤어요.</p>
        </div>
        <span class="chip">{{ movies.length }}</span>
      </header>

      <div v-if="loading.movies" class="loading">영화를 불러오는 중...</div>
      <div v-else-if="movies.length" class="grid">
        <article
          v-for="movie in movies"
          :key="movie.tmdb_id"
          class="card movie-card"
          @click="router.push({ name: 'movieDetail', params: { movieId: movie.tmdb_id } })"
        >
          <div class="poster">
            <img v-if="movie.poster_path" :src="posterUrl(movie.poster_path)" alt="" />
            <div v-else class="no-poster">No Image</div>
            <button class="remove" @click="removeMovie(movie.tmdb_id, $event)">✕</button>
          </div>
          <div class="card-body">
            <p class="title">{{ movie.title }}</p>
            <p class="muted line">{{ movie.overview || '설명이 없습니다.' }}</p>
          </div>
        </article>
      </div>
      <div v-else class="empty">
        <p>아직 좋아요한 영화가 없어요.</p>
        <button class="ghost" @click="router.push({ name: 'movies' })">영화 보러가기</button>
      </div>
    </section>

    <section v-show="activeTab === 'reviews'" id="section-reviews" class="panel">
      <header class="panel-heading">
        <div>
          <p class="eyebrow">Writing</p>
          <h2>내 글</h2>
          <p class="muted">작성한 리뷰와 글을 모았습니다.</p>
        </div>
        <span class="chip">{{ reviews.length }}</span>
      </header>

      <div v-if="loading.reviews" class="loading">글을 불러오는 중...</div>
      <div v-else-if="reviews.length" class="list">
        <article v-for="review in reviews" :key="review.id" class="card review-card">
          <div class="review-flex">
            <div class="poster thumb" @click="goToMovieDetail(review.movie_tmdb_id)">
              <img
                v-if="review.movie_poster_path"
                :src="posterUrl(review.movie_poster_path)"
                alt="poster"
              />
              <div v-else class="no-poster">No Image</div>
            </div>

            <div class="review-main">
              <div class="card-head">
                <h3 class="title-link" @click="goToMovieDetail(review.movie_tmdb_id)">
                  {{ review.movie_title || '제목 없음' }}
                </h3>
                <span class="badge">★ {{ review.rating ?? '-' }}</span>
              </div>
              <p class="muted small">
                {{ review.created_at ? new Date(review.created_at).toLocaleDateString('ko-KR') : '' }}
              </p>
              <p class="line">{{ review.content }}</p>
              <div class="card-actions">
                <button class="ghost" @click="router.push({ name: 'postDetail', params: { id: review.id } })">
                  리뷰 보기 
                </button>
                
                <button class="primary ghost-outline" @click="goToMovieDetail(review.movie_tmdb_id)">
                  영화 정보
                </button>
              </div>
            </div>
          </div>
        </article>
      </div>
      <div v-else class="empty">
        <p>아직 작성한 글이 없어요.</p>
        <button class="ghost" @click="router.push({ name: 'movies' })">첫 글 남기기</button>
      </div>
    </section>

    <section v-show="activeTab === 'follows'" id="section-follows" class="panel">
      <header class="panel-heading">
        <div>
          <p class="eyebrow">Social</p>
          <h2>내 친구</h2>
          <p class="muted">팔로잉과 팔로워를 한 곳에서 관리하세요.</p>
        </div>
      </header>

      <div class="follow-columns">
        <div class="follow-box">
          <div class="box-head">
            <h3>팔로잉</h3>
            <span class="chip">{{ followings.length }}</span>
          </div>
          <div v-if="loading.follows" class="loading small">로딩 중...</div>
          <ul v-else-if="followings.length" class="people">
            <li v-for="user in followings" :key="user.username">
              <div>
                <p class="title">{{ user.username }}</p>
                <p class="muted small">{{ user.bio || '소개가 없습니다.' }}</p>
              </div>
              <button class="ghost" @click="toggleFollow(user.username)">팔로우 취소</button>
            </li>
          </ul>
          <p v-else class="muted">아직 팔로잉한 사람이 없습니다.</p>
        </div>

        <div class="follow-box">
          <div class="box-head">
            <h3>팔로워</h3>
            <span class="chip">{{ followers.length }}</span>
          </div>
          <div v-if="loading.follows" class="loading small">로딩 중...</div>
          <ul v-else-if="followers.length" class="people">
            <li v-for="user in followers" :key="user.username">
              <div>
                <p class="title">{{ user.username }}</p>
                <p class="muted small">{{ user.bio || '소개가 없습니다.' }}</p>
              </div>
              <button class="ghost" @click="toggleFollow(user.username)">
                {{ user.is_following ? '팔로우 취소' : '맞팔하기' }}
              </button>
            </li>
          </ul>
          <p v-else class="muted">아직 팔로워가 없습니다.</p>
        </div>
      </div>

      <div class="suggestions">
        <div class="box-head">
          <h3>팔로우 추천</h3>
          <span class="chip">{{ suggestions.length }}</span>
        </div>
        <div v-if="loading.suggestions" class="loading small">추천 로딩 중...</div>
        <div v-else-if="suggestions.length" class="grid users">
          <article v-for="user in suggestions" :key="user.username" class="card user-card">
            <p class="title">{{ user.username }}</p>
            <p class="muted small">{{ user.bio || '소개가 없습니다.' }}</p>
            <p class="muted small">최애 영화: {{ user.favorite_movie_name || '정보 없음' }}</p>
            <button
              class="primary full"
              :class="{ ghost: user.is_following }"
              @click="toggleFollow(user.username)"
            >
              {{ user.is_following ? '팔로우 취소' : '팔로우' }}
            </button>
          </article>
        </div>
        <p v-else class="muted">표시할 사용자가 없습니다.</p>
      </div>
    </section>

    <section v-show="activeTab === 'profile'" id="section-profile" class="panel">
      <header class="panel-heading">
        <div>
          <p class="eyebrow">Profile</p>
          <h2>프로필 수정</h2>
          <p class="muted">간단한 자기소개와 최애 영화를 업데이트하세요.</p>
        </div>
      </header>

      <div v-if="errorMessage" class="error">{{ errorMessage }}</div>

      <form class="form" @submit.prevent="saveProfile">
        <label>프로필 이미지</label>
        <div class="avatar-row">
          <div class="avatar-preview">
            <img v-if="profileImage" :src="profileImage" alt="profile preview" />
            <span v-else>{{ displayName.charAt(0).toUpperCase() }}</span>
          </div>
          <div class="avatar-actions">
            <label class="upload-btn">
              <input type="file" accept="image/*" hidden @change="handleImageChange" />
              이미지 선택
            </label>
            <button v-if="profileImage" type="button" class="ghost" @click="clearProfileImage">
              제거
            </button>
            <p class="muted small">2MB 이하 이미지를 업로드하거나 제거할 수 있습니다.</p>
          </div>
        </div>

        <label>소개</label>
        <textarea
          v-model="bio"
          rows="3"
          placeholder="나를 한 줄로 표현해보세요."
        ></textarea>

        <label>최애 영화 제목</label>
        <input v-model="favoriteMovieName" type="text" placeholder="영화 제목" />

        <div class="form-actions">
          <button class="primary" type="submit" :disabled="loading.savingProfile">
            {{ loading.savingProfile ? '저장 중...' : '저장하기' }}
          </button>
          <span class="muted small" v-if="statusMessage">{{ statusMessage }}</span>
        </div>
      </form>
    </section>
  </div>
</template>

<style scoped>
.hub {
  background: #030303;
  color: #fff;
}

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 56px 50px 46px;
  background: linear-gradient(135deg, rgba(29, 185, 84, 0.2), rgba(4, 4, 4, 0.95));
  border-bottom: 1px solid #0f0f0f;
  text-align: center;
}

.hero .avatar {
  overflow: hidden;
}

.hero .avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.hero .avatar span {
  display: inline-flex;
}

.hero-text h1 {
  margin: 4px 0 6px;
  font-size: 32px;
}

.hero h1 {
  font-size: 40px;
  font-weight: 800;
}

.hero-desc {
  max-width: 760px;
  font-size: 16px;
}

.hero-cta {
  background: rgba(0, 0, 0, 0.35);
  padding: 14px 16px;
  border: 1px dashed #1db954;
  border-radius: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1db954, #0ea94b);
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 30px;
  color: #000;
}

.eyebrow {
  letter-spacing: 0.2em;
  text-transform: uppercase;
  font-size: 12px;
  color: #7fe0a7;
}

.muted {
  color: #a0a0a0;
}

.muted.small {
  font-size: 13px;
}

.stats {
  margin-top: 8px;
  display: flex;
  gap: 16px;
}

.stat {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px 18px;
}

.stat .label {
  display: block;
  font-size: 12px;
  color: #9ddbb3;
}

.tabbar {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  padding: 16px 50px;
  background: #0d0d0d;
  border-bottom: 1px solid #0f0f0f;
  position: sticky;
  top: 70px;
  z-index: 10;
}

.tabbar button {
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: #111;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tabbar button.active {
  border-color: #1db954;
  box-shadow: 0 6px 20px rgba(29, 185, 84, 0.2);
}

.panel {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 50px 20px;
}

.panel-heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.chip {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.06);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.list {
  display: grid;
  gap: 14px;
}

.card {
  background: #0d0d0d;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 14px;
}

.movie-card {
  padding: 0;
  overflow: hidden;
}

.poster {
  position: relative;
  width: 100%;
  height: 280px;
  background: #111;
}

.poster img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-poster {
  display: grid;
  place-items: center;
  height: 100%;
  color: #777;
}

.remove {
  position: absolute;
  top: 8px;
  right: 8px;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  cursor: pointer;
}

.card-body {
  padding: 12px;
}

.title {
  font-weight: 700;
  margin-bottom: 4px;
}

.line {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.badge {
  background: rgba(255, 255, 255, 0.06);
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 13px;
}

.card-actions {
  margin-top: 10px;
}

.review-card .review-flex {
  display: grid;
  grid-template-columns: 120px 1fr;
  gap: 16px;
  align-items: start;
}

.thumb {
  cursor: pointer;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.08);
  height: 120px;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.title-link {
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 4px;
  font-size: 18px;
  line-height: 1.3;
  display: inline-block;
}

.ghost-outline {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
}

.review-main .line {
  font-size: 14px;
  line-height: 1.5;
}

.follow-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.follow-box {
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 14px;
  background: #0c0c0c;
}

.box-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.people {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
}

.people li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 10px 12px;
}

.suggestions .users {
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
}

.form {
  display: grid;
  gap: 10px;
  max-width: 520px;
}

.avatar-row {
  display: flex;
  align-items: center;
  gap: 14px;
}

.avatar-preview {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1db954, #1ed760);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 800;
  color: #000;
  overflow: hidden;
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
  gap: 6px;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.12);
  transition: all 0.2s ease;
}

.upload-btn:hover {
  background: rgba(255, 255, 255, 0.16);
}

.form input,
.form textarea {
  background: #0f0f0f;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 12px;
  color: #fff;
}

.form-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 6px;
}

.loading {
  padding: 18px 0;
  color: #a0a0a0;
}

.loading.small {
  padding: 6px 0;
}

.empty {
  padding: 20px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  text-align: center;
  color: #a0a0a0;
}

.primary {
  background: linear-gradient(135deg, #1db954, #15a54c);
  border: none;
  color: #000;
  padding: 10px 16px;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 700;
}

.primary.full {
  width: 100%;
}

.ghost {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
}

.error {
  border: 1px solid #ff6b6b;
  background: rgba(255, 107, 107, 0.08);
  padding: 10px 12px;
  border-radius: 10px;
  color: #ff9b9b;
  margin-bottom: 10px;
}

@media (max-width: 800px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .tabbar {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    top: 60px;
  }

  .panel {
    padding: 24px 20px;
  }

  .review-card .review-flex {
    grid-template-columns: 1fr;
  }
}
</style>
