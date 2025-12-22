<script setup>
import { RouterView, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ref, onMounted, onBeforeUnmount } from 'vue'

const authStore = useAuthStore()
const showDropdown = ref(false)

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

function closeDropdown() {
  showDropdown.value = false
}

// 외부 클릭 감지
function handleClickOutside(event) {
  const dropdown = document.querySelector('.profile-dropdown')
  const profileBtn = document.querySelector('.profile-btn')

  if (!profileBtn) return
  if (dropdown && !dropdown.contains(event.target) && !profileBtn.contains(event.target)) {
    closeDropdown()
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

    <!-- 로그인 상태 -->
    <div v-if="authStore.isAuthenticated" class="auth-links">
      <a href="#" class="logout-link" @click.prevent="authStore.logout">로그아웃</a>

      <div class="profile-wrapper">
        <button type="button" class="profile-btn" @click="toggleDropdown">
          <div class="avatar">
            {{ authStore.user?.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <span class="username-text">{{ authStore.user?.username }}</span>
        </button>

        <div v-if="showDropdown" class="profile-dropdown">
          <RouterLink class="dropdown-item" to="/my-movies" @click="closeDropdown">
            내 영화
          </RouterLink>
          <RouterLink class="dropdown-item" to="/my-reviews" @click="closeDropdown">
            내 리뷰
          </RouterLink>

          <div class="dropdown-divider"></div>

          <RouterLink class="dropdown-item" to="/profile" @click="closeDropdown">
            프로필 수정
          </RouterLink>
        </div>
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

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  background-color: #000000;
  color: #ffffff;
  font-family: 'Noto Sans KR', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
  background-color: #000000;
}
</style>

<style scoped>
.nav {
  display: flex;
  gap: 24px;
  padding: 16px 50px;
  background-color: #000000;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
  border-bottom: 1px solid #222;
}

.logo {
  font-size: 28px;
  font-weight: 700;
  color: #1DB954;
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
  color: #e5e5e5;
  font-size: 15px;
  font-weight: 500;
  transition: color 0.3s ease;
}

.link:hover,
.logout-link:hover {
  color: #1DB954;
}

.link.router-link-active {
  color: #1DB954;
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
