<template>
  <div class="wrap">
    <h2>404</h2>
    <p class="muted">페이지를 찾을 수 없습니다.</p>
    <button class="btn" @click="goHome">홈으로</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
function goHome() {
  router.push('/')
}
</script>

<style scoped>
.wrap {
  padding: 16px;
}
.muted {
  color: #666;
  margin: 8px 0 16px;
}
.btn {
  padding: 10px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
}
</style>
