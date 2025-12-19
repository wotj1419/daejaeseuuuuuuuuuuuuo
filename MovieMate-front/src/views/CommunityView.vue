<template>
  <div>
    <div class="top">
      <h2>커뮤니티</h2>
      <button class="btn" @click="$router.push('/community/posts/new')">글 작성</button>
    </div>

    <p class="muted">영화 후기/추천/잡담을 올리는 공간입니다.</p>

    <div v-if="posts.length === 0" class="muted">아직 글이 없습니다. 첫 글을 작성해보세요!</div>

    <div class="list">
      <div class="item" v-for="p in posts" :key="p.id" @click="open(p.id)">
        <div class="title">{{ p.title }}</div>
        <div class="sub">{{ p.createdAt }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const LS_POSTS = 'moviemate_posts_v1'

function loadPosts() {
  try {
    return JSON.parse(localStorage.getItem(LS_POSTS)) ?? []
  } catch {
    return []
  }
}

const posts = computed(() => loadPosts().sort((a, b) => b.id - a.id))

function open(id) {
  window.location.href = `/community/posts/${id}`
}
</script>

<style scoped>
.top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.btn {
  padding: 8px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
}
.muted {
  color: #666;
  margin: 8px 0 16px;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.item {
  border: 1px solid #eee;
  border-radius: 10px;
  padding: 12px;
  cursor: pointer;
}
.title {
  font-weight: 800;
}
.sub {
  color: #666;
  font-size: 12px;
  margin-top: 6px;
}
</style>
