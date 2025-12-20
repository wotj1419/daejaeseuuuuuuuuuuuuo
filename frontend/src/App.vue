<script setup>
import { RouterView, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<template>
  <header class="nav">
    <div class="logo">MovieMate</div>
    <RouterLink class="link" to="/">홈</RouterLink>
    <RouterLink class="link" to="/movies">영화</RouterLink>
    
    <div v-if="authStore.isAuthenticated" class="auth-links">
      <RouterLink class="link" to="/profile">프로필</RouterLink>
      <a href="#" class="link" @click.prevent="authStore.logout">로그아웃</a>
    </div>
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
  padding: 20px 50px;
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
}

.auth-links {
  margin-left: auto;
  display: flex;
  gap: 20px;
  align-items: center;
}

.link {
  text-decoration: none;
  color: #e5e5e5;
  font-size: 15px;
  font-weight: 500;
  transition: color 0.3s ease;
  position: relative;
}

.link:hover {
  color: #1DB954;
}

.link.router-link-active {
  color: #1DB954;
  font-weight: 700;
}

.wrap {
  max-width: 100%;
  margin: 0;
  padding: 0;
  background-color: #000000;
  min-height: calc(100vh - 70px);
}
</style>
