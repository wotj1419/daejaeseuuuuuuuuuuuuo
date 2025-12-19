<template>
  <div v-if="post">
    <h2>{{ post.title }}</h2>
    <div class="muted">{{ post.createdAt }}</div>

    <div class="box">{{ post.content }}</div>

    <button class="btn" @click="$router.push('/community')">목록</button>
  </div>

  <div v-else class="muted">글을 찾을 수 없습니다.</div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const LS_POSTS = 'moviemate_posts_v1'

function loadPosts() {
  try {
    return JSON.parse(localStorage.getItem(LS_POSTS)) ?? []
  } catch {
    return []
  }
}

const post = computed(() => {
  const id = Number(route.params.id)
  return loadPosts().find((p) => p.id === id) ?? null
})
</script>

<style scoped>
.muted {
  color: #666;
  margin: 8px 0 16px;
}
.box {
  border: 1px solid #eee;
  border-radius: 10px;
  padding: 12px;
  min-height: 120px;
  white-space: pre-wrap;
}
.btn {
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
}
</style>
