<script setup>
import { RouterView, RouterLink } from 'vue-router'
</script>

<template>
  <header class="nav">
    <RouterLink class="link" to="/">Home</RouterLink>
    <RouterLink class="link" to="/movies">Movies</RouterLink>
    <RouterLink class="link" to="/profile">Profile</RouterLink>
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
