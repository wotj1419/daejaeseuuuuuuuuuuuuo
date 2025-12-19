<template>
  <div>
    <h2>글 작성</h2>

    <form class="form" @submit.prevent="save">
      <label>제목</label>
      <input v-model="title" placeholder="제목을 입력하세요" />

      <label>내용</label>
      <textarea v-model="content" rows="6" placeholder="내용을 입력하세요"></textarea>

      <button class="btn primary" type="submit">등록</button>
      <button class="btn" type="button" @click="$router.push('/community')">취소</button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const title = ref('')
const content = ref('')

const LS_POSTS = 'moviemate_posts_v1'

function loadPosts() {
  try {
    return JSON.parse(localStorage.getItem(LS_POSTS)) ?? []
  } catch {
    return []
  }
}

function save() {
  const t = title.value.trim()
  const c = content.value.trim()
  if (!t || !c) return alert('제목/내용을 입력하세요.')

  const posts = loadPosts()
  const newPost = {
    id: (posts[0]?.id ?? 0) + 1,
    title: t,
    content: c,
    createdAt: new Date().toLocaleString(),
  }
  localStorage.setItem(LS_POSTS, JSON.stringify([newPost, ...posts]))
  router.push('/community')
}
</script>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-width: 520px;
}
input,
textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
}
.btn {
  padding: 10px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
}
.btn.primary {
  background: #111;
  color: white;
  border-color: #111;
}
</style>
