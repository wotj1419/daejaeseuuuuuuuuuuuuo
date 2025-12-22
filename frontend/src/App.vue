<script setup>
import { RouterView, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ref, onMounted, onBeforeUnmount } from 'vue'

const authStore = useAuthStore()
const showBoardMenu = ref(false)

// 외부 클릭 감지
function toggleBoardMenu(event) {
  event.stopPropagation()
  showBoardMenu.value = !showBoardMenu.value
}

function closeBoardMenu() {
  showBoardMenu.value = false
}

function handleClickOutside(event) {
  const boardDropdown = document.querySelector('.board-dropdown')
  const boardBtn = document.querySelector('.board-link')

  if (boardDropdown && boardBtn && showBoardMenu.value) {
    if (!boardDropdown.contains(event.target) && !boardBtn.contains(event.target)) {
      closeBoardMenu()
    }
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <header class="nav">
    <RouterLink class="logo" to="/">MovieMate</RouterLink>
    <RouterLink class="link" to="/">홈</RouterLink>
    <RouterLink class="link" to="/movies">영화</RouterLink>
    <RouterLink class="link" to="/movie-share">프로필 공유</RouterLink>
    <div class="board-wrapper">
      <button type="button" class="board-link" @click="toggleBoardMenu">
        게시판
      </button>
      <div v-if="showBoardMenu" class="board-dropdown profile-dropdown">
        <RouterLink class="dropdown-item" to="/boards/free" @click="closeBoardMenu">
          자유게시판
        </RouterLink>
        <RouterLink class="dropdown-item" to="/boards/friend" @click="closeBoardMenu">
          친구게시판
        </RouterLink>
      </div>
    </div>

    <!-- 로그인 상태 -->
    <div v-if="authStore.isAuthenticated" class="auth-links">
      <a href="#" class="logout-link" @click.prevent="authStore.logout">로그아웃</a>

      <div class="profile-wrapper">
        <RouterLink class="profile-btn" to="/me">
          <div class="avatar">
            {{ authStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <span class="username-text">{{ authStore.user?.username }}</span>
        </RouterLink>
      </div>
    </div>

    <!-- 비로그인 상태 -->
    <div v-else class="auth-links">
      <RouterLink class="link" to="/login">로그인</RouterLink>
      <RouterLink class="link" to="/signup">회원가입</RouterLink>
    </div>
  </header>

  <main class="wrap">
    <RouterView />
  </main>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&display=swap');

:root {
  --base-color: #37664b;
  --base-color-dark: #273a34;
  --base-color-light: #4f9171;
  --base-background: #030303;
  --base-card: #0d0d0d;
  --base-border: #1c1c1c;
  --text-color: #ffffff;
  --muted-text: rgba(255, 255, 255, 0.7);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: var(--base-background);
  color: var(--text-color);
  font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  background-color: var(--base-background);
}
</style>

<style scoped>
.nav {
  display: flex;
  gap: 24px;
  padding: 16px 50px;
  background-color: var(--base-card);
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid var(--base-border);
}

.logo {
  font-size: 28px;
  font-weight: 700;
  color: var(--base-color);
  margin-right: 20px;
  letter-spacing: -0.5px;
  text-decoration: none;
}

.auth-links {
  margin-left: auto;
  display: flex;
  gap: 24px;
  align-items: center;
}

.link,
.logout-link {
  text-decoration: none;
  color: var(--muted-text);
  font-size: 15px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.board-wrapper {
  position: relative;
}

.board-link {
  background: transparent;
  border: none;
  color: var(--muted-text);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
}

.board-link:hover {
  color: var(--base-color-light);
}

.board-dropdown {
  right: 0;
  top: calc(100% + 12px);
  width: 160px;
  padding: 8px 0;
}

.link:hover,
.logout-link:hover {
  color: var(--base-color-light);
}

.link.router-link-active {
  color: var(--base-color);
  font-weight: 700;
}

.wrap {
  min-height: calc(100vh - 70px);
}

/* 프로필 드롭다운 */
.profile-wrapper {
  position: relative;
}

.profile-btn {
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 8px;
  border-radius: 30px;
}

.profile-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #1DB954 0%, #169B43 100%);
  color: #000;
  font-weight: 700;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.username-text {
  font-size: 15px;
  font-weight: 600;
  color: #fff;
}

.profile-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 12px;
  background-color: #1a1a1a;
  border: 1px solid #333;
  border-radius: 12px;
  width: 200px;
  padding: 8px 0;
  z-index: 1000;
}

.dropdown-item {
  display: block;
  padding: 12px 20px;
  color: #e5e5e5;
  text-decoration: none;
  font-size: 14px;
}

.dropdown-item:hover {
  background-color: #333;
  color: #1DB954;
}

.dropdown-divider {
  height: 1px;
  background-color: #333;
  margin: 8px 0;
}
</style>
