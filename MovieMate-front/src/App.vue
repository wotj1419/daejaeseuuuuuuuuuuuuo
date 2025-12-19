<script setup>
import { RouterView, RouterLink, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { computed } from 'vue'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

const handleLogout = async () => {
  await authStore.logout()
  router.push('/')
}
</script>

<template>
  <header class="nav">
    <div class="nav-left">
      <RouterLink class="logo" to="/">MovieMate</RouterLink>
      <RouterLink class="link" to="/">Home</RouterLink>
      <RouterLink class="link" to="/movies">Movies</RouterLink>
    </div>
    
    <div class="nav-right">
      <template v-if="isAuthenticated">
        <span class="user-name">{{ user?.username }}님</span>
        <RouterLink class="link" to="/profile">Profile</RouterLink>
        <button @click="handleLogout" class="logout-btn">로그아웃</button>
      </template>
      <template v-else>
        <RouterLink class="link" to="/login">로그인</RouterLink>
        <RouterLink class="link register-link" to="/register">회원가입</RouterLink>
      </template>
    </div>
  </header>

  <main class="wrap">
    <RouterView />
  </main>
</template>

<style scoped>
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  border-bottom: 1px solid #eee;
  background: white;
}

.nav-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: #4CAF50;
  text-decoration: none;
}

.link {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  transition: color 0.3s;
}

.link:hover {
  color: #4CAF50;
}

.register-link {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border-radius: 6px;
}

.register-link:hover {
  background-color: #45a049;
  color: white;
}

.user-name {
  color: #666;
  font-size: 14px;
}

.logout-btn {
  padding: 8px 16px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.3s;
}

.logout-btn:hover {
  background-color: #d32f2f;
}

.wrap {
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px;
}
</style>
