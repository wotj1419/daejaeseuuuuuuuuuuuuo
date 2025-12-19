<script setup>
import { RouterView, RouterLink } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
</script>

<template>
  <header class="nav">
    <RouterLink class="link" to="/">Home</RouterLink>
    <RouterLink class="link" to="/movies">Movies</RouterLink>
    
    <div v-if="authStore.isAuthenticated" class="auth-links">
      <RouterLink class="link" to="/profile">Profile</RouterLink>
      <a href="#" class="link" @click.prevent="authStore.logout">Logout</a>
    </div>
    <div v-else class="auth-links">
       <RouterLink class="link" to="/login">Login</RouterLink>
       <RouterLink class="link" to="/signup">Sign Up</RouterLink>
    </div>
  </header>

  <main class="wrap">
    <RouterView />
  </main>
</template>

<style scoped>
.nav {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid #eee;
  align-items: center;
}
.auth-links {
  margin-left: auto;
  display: flex;
  gap: 12px;
}
.link {
  text-decoration: none;
  color: #333;
}
.wrap {
  max-width: 1100px;
  margin: 0 auto;
  padding: 16px;
}
</style>
