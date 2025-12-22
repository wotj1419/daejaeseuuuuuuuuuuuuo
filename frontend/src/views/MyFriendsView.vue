<script setup>
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { accountsApi } from '@/api/accounts'
import { useAuthStore } from '@/stores/auth'

const friends = ref([])
const users = ref([])
const loadingFriends = ref(false)
const loadingUsers = ref(false)
const errorMessage = ref('')
const toggling = ref({})
const router = useRouter()
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const setToggling = (username, status) => {
  toggling.value = { ...toggling.value, [username]: status }
}

const isToggling = (username) => !!toggling.value[username]

async function loadFriends() {
  loadingFriends.value = true
  try {
    if (!isAuthenticated.value) return
    const { data } = await accountsApi.getFriends()
    friends.value = data
  } catch (error) {
    console.error('친구 목록을 불러오는 중 오류가 발생했습니다.', error)
    errorMessage.value = '친구 목록을 불러오는 중 오류가 발생했습니다.'
  } finally {
    loadingFriends.value = false
  }
}

async function loadUsers() {
  loadingUsers.value = true
  try {
    if (!isAuthenticated.value) return
    const { data } = await accountsApi.getUsers()
    users.value = data
  } catch (error) {
    console.error('사용자 목록을 불러오는 중 오류가 발생했습니다.', error)
    errorMessage.value = '사용자 목록을 불러오는 중 오류가 발생했습니다.'
  } finally {
    loadingUsers.value = false
  }
}

async function refreshLists() {
  errorMessage.value = ''
  if (!isAuthenticated.value) return
  await Promise.all([loadFriends(), loadUsers()])
}

async function handleToggleFriend(username) {
  errorMessage.value = ''
  setToggling(username, true)
  try {
    if (!isAuthenticated.value) {
      errorMessage.value = '로그인 후 친구를 추가할 수 있습니다.'
      return
    }
    await accountsApi.toggleFriend(username)
    await refreshLists()
  } catch (error) {
    console.error('친구 토글에 실패했습니다.', error)
    errorMessage.value = error.response?.data?.error || '친구 처리를 하는 중 오류가 발생했습니다.'
  } finally {
    setToggling(username, false)
  }
}

watch(
  isAuthenticated,
  (authenticated) => {
    if (authenticated) {
      refreshLists()
    } else {
      friends.value = []
      users.value = []
      errorMessage.value = ''
    }
  },
  { immediate: true }
)

const goToLogin = () => router.push({ name: 'login' })
</script>

<template>
  <div class="friends-page">
    <section class="header-section">
      <p class="header-label">Friend Space</p>
      <h1 class="page-title">내 친구</h1>
      <p class="page-subtitle">
        친구들과 영화 취향을 공유하고 대화를 나눌 수 있는 나만의 방을 만들어보세요.
      </p>
    </section>

    <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>

    <div v-if="!isAuthenticated" class="auth-warning">
      <p>친구 기능은 로그인한 사용자만 이용할 수 있어요.</p>
      <button class="login-cta" @click="goToLogin">로그인하러 가기</button>
      <p class="auth-tip">닉네임을 기반으로 친구를 추가할 수 있습니다.</p>
    </div>

    <section v-if="isAuthenticated" class="content-section">
      <div class="section-heading">
        <div>
          <p class="section-label">Friends</p>
          <h2>친구 목록</h2>
          <p class="section-description">자주 소통하는 친구들과 영화 이야기를 나눠보세요.</p>
        </div>
        <span class="count-chip">{{ friends.length }}명</span>
      </div>

      <div v-if="loadingFriends" class="loading-panel">
        <div class="loading-spinner"></div>
        <p>친구 목록을 불러오는 중...</p>
      </div>

      <div v-else-if="friends.length" class="friend-grid">
        <article v-for="friend in friends" :key="friend.username" class="friend-card">
          <div class="friend-card-top">
            <div class="friend-avatar">{{ friend.username.charAt(0).toUpperCase() }}</div>
            <div>
              <p class="friend-name">{{ friend.username }}</p>
              <p class="friend-bio">{{ friend.bio || '간단한 자기소개가 없습니다.' }}</p>
            </div>
          </div>
          <div class="friend-meta">
            <span>좋아하는 영화</span>
            <strong>{{ friend.favorite_movie_name || '등록된 영화 없음' }}</strong>
          </div>
        </article>
      </div>

      <div v-else class="empty-panel">
        <p>아직 친구가 없습니다.</p>
        <p>하단의 사용자 목록에서 친구를 추가해보세요.</p>
      </div>
    </section>

    <section v-if="isAuthenticated" class="content-section">
      <div class="section-heading">
        <div>
          <p class="section-label">Suggestions</p>
          <h2>친구 추천</h2>
          <p class="section-description">새로운 친구를 추가하고 나만의 감상 방으로 초대해보세요.</p>
        </div>
        <span class="count-chip">{{ users.length }}명</span>
      </div>

      <div v-if="loadingUsers" class="loading-panel">
        <div class="loading-spinner"></div>
        <p>사용자 목록을 불러오는 중...</p>
      </div>

      <div v-else-if="users.length" class="user-grid">
        <article v-for="user in users" :key="user.username" class="user-card">
          <div>
            <p class="user-name">{{ user.username }}</p>
            <p class="user-bio">{{ user.bio || '소개가 없습니다.' }}</p>
          </div>
          <div class="favorite-row">
            <span>최애 영화</span>
            <strong>{{ user.favorite_movie_name || '정보 없음' }}</strong>
          </div>
          <button
            class="friend-action-btn"
            :class="{ secondary: user.is_friend }"
            :disabled="isToggling(user.username)"
            @click="handleToggleFriend(user.username)"
          >
            <span v-if="isToggling(user.username)">처리 중...</span>
            <span v-else>{{ user.is_friend ? '친구 삭제' : '친구 추가' }}</span>
          </button>
        </article>
      </div>

      <div v-else class="empty-panel">
        <p>새로운 사용자가 없습니다.</p>
        <p>잠시 후 다시 확인해주세요.</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.friends-page {
  min-height: 100vh;
  background: var(--base-background);
  color: var(--text-color);
  padding-bottom: 60px;
}

.header-section {
  padding: 60px 50px 40px;
  text-align: center;
  border-bottom: 1px solid var(--base-border);
}

.header-label {
  font-size: 13px;
  letter-spacing: 0.4em;
  text-transform: uppercase;
  color: var(--base-color);
  margin-bottom: 12px;
}

.page-title {
  font-size: 48px;
  font-weight: 800;
  margin-bottom: 12px;
}

.page-subtitle {
  font-size: 16px;
  color: #aaa;
  max-width: 720px;
  margin: 0 auto;
}

.error-message {
  max-width: 960px;
  margin: 20px auto;
  padding: 12px 16px;
  border: 1px solid #4c4c4c;
  border-radius: 12px;
  background: rgba(255, 68, 68, 0.1);
  color: #ff6b6b;
}

.auth-warning {
  max-width: 700px;
  margin: 20px auto;
  padding: 26px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.03);
  text-align: center;
}

.auth-warning p {
  margin-bottom: 14px;
  color: #ccc;
}

.login-cta {
  border: none;
  padding: 12px 32px;
  border-radius: 999px;
  background: linear-gradient(135deg, var(--base-color), var(--base-color-light));
  color: #000;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.login-cta:hover {
  transform: translateY(-2px);
}

.auth-tip {
  font-size: 13px;
  color: #888;
  margin-top: 10px;
}

.content-section {
  max-width: 1100px;
  margin: 40px auto;
  padding: 0 50px;
}

.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 28px;
}

.section-label {
  font-size: 12px;
  letter-spacing: 0.25em;
  color: var(--base-color);
  text-transform: uppercase;
  margin-bottom: 6px;
}

.section-heading h2 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
}

.section-description {
  color: #888;
  margin-top: 6px;
}

.count-chip {
  padding: 6px 14px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  font-size: 14px;
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.loading-panel,
.empty-panel {
  text-align: center;
  border: 1px solid #222;
  border-radius: 18px;
  padding: 32px;
  background: rgba(255, 255, 255, 0.02);
  color: #aaa;
}

.loading-spinner {
  width: 52px;
  height: 52px;
  border: 5px solid rgba(29, 185, 84, 0.2);
  border-top-color: #1db954;
  border-radius: 50%;
  margin: 0 auto 16px;
  animation: spin 1s linear infinite;
}

.friend-grid,
.user-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
}

.friend-card,
.user-card {
  background: #111;
  border: 1px solid #222;
  border-radius: 18px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 180px;
}

.friend-card-top,
.user-card > div {
  display: flex;
  gap: 16px;
}

.friend-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--base-color), var(--base-color-light));
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 20px;
}

.friend-name,
.user-name {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}

.friend-bio,
.user-bio {
  font-size: 14px;
  color: #bbb;
  margin: 4px 0 0;
}

.friend-meta {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--base-border);
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: #999;
}

.favorite-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding-top: 10px;
  font-size: 14px;
  color: #aaa;
}

.favorite-row strong {
  color: #fff;
  font-size: 15px;
}

.friend-action-btn {
  margin-top: 18px;
  padding: 12px 16px;
  font-weight: 700;
  border-radius: 14px;
  border: 1px solid transparent;
  background: linear-gradient(135deg, var(--base-color), var(--base-color-light));
  color: #000;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.friend-action-btn.secondary {
  background: transparent;
  color: #fff;
  border-color: rgba(255, 255, 255, 0.25);
}

.friend-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.friend-action-btn:not(:disabled):hover {
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .header-section,
  .content-section {
    padding: 0 20px;
  }

  .section-heading {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .friend-grid,
  .user-grid {
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }
}
</style>
