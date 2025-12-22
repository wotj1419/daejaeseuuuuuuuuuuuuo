<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { boardsApi } from '@/api/boards'
import { useAuthStore } from '@/stores/auth'

const freePosts = ref([])
const loading = ref(false)
const searchQuery = ref('')

const router = useRouter()
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const formatDate = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString('ko-KR', { dateStyle: 'medium', timeStyle: 'short' })
}

const filteredPosts = computed(() => {
  if (!searchQuery.value.trim()) return freePosts.value
  const q = searchQuery.value.toLowerCase()
  return freePosts.value.filter((post) => {
    const title = (post.title || '').toLowerCase()
    const content = (post.content || '').toLowerCase()
    const movieTitle = (post.movie_title || '').toLowerCase()
    return title.includes(q) || content.includes(q) || movieTitle.includes(q)
  })
})

async function loadFreePosts() {
  loading.value = true
  try {
    const { data } = await boardsApi.listFree()
    freePosts.value = data
  } catch (error) {
    console.error('자유게시판 로드 실패', error)
  } finally {
    loading.value = false
  }
}

function goToCreate() {
  if (!isAuthenticated.value) {
    router.push({ name: 'login' })
    return
  }
  router.push({ name: 'freeBoardCreate' })
}

onMounted(loadFreePosts)
</script>

<template>
  <div class="free-board">
    <section class="hero">
      <p class="hero-label">Board</p>
      <div class="hero-row">
        <h1>자유게시판</h1>
      </div>
      <p class="hero-sub">모든 사용자와 자유롭게 생각을 나누세요.</p>
    </section>

    <section class="panel">
      <div class="panel-heading">
        <h2>전체 게시글</h2>
        <span>{{ filteredPosts.length }}개의 글</span>
      </div>

      <div v-if="loading" class="loading">불러오는 중...</div>

      <div v-else-if="filteredPosts.length" class="post-list">
        <article v-for="post in filteredPosts" :key="post.id" class="row-card">
          <div class="row-main">
            <div class="row-title">
              <h3>{{ post.title }}</h3>
              <span class="time">{{ formatDate(post.created_at) }}</span>
            </div>
            <p v-if="post.movie_title" class="movie">🎬 {{ post.movie_title }}</p>
            <p class="content">{{ post.content }}</p>
          </div>
          <div class="row-meta">
            <span class="author">{{ post.author_username }}</span>
          </div>
        </article>
      </div>

      <p v-else class="empty">아직 공유된 글이 없습니다.</p>

      <div class="search-bar">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="영화 제목이나 내용으로 검색"
        />
        <button class="write-btn ghost" @click="goToCreate">글쓰기</button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.free-board {
  padding-bottom: 60px;
  background: #030303;
  min-height: 100vh;
}

.hero {
  background: linear-gradient(135deg, rgba(55, 102, 75, 0.25), rgba(25, 25, 25, 0.9));
  color: #fff;
  padding: 60px 50px;
  border-bottom: 1px solid #111;
}

.hero-label {
  font-size: 12px;
  letter-spacing: 0.6em;
  text-transform: uppercase;
  margin-bottom: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.hero-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.hero h1 {
  font-size: 42px;
  font-weight: 800;
  margin: 0;
}

.hero-sub {
  margin-top: 12px;
  color: rgba(255, 255, 255, 0.75);
}

.write-btn {
  padding: 10px 18px;
  border-radius: 10px;
  border: 1px solid #4f9171;
  background: #37664b;
  color: #f3f7f3;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.write-btn:hover {
  background: #4f9171;
  border-color: #4f9171;
}

.write-btn.ghost {
  background: transparent;
  color: #4f9171;
}

.panel {
  max-width: 1100px;
  margin: 32px auto;
  background: #111;
  border-radius: 16px;
  border: 1px solid #222;
  padding: 24px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
}

.panel-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  color: #e5e5e5;
}

.post-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.row-card {
  border: 1px solid #222;
  border-radius: 12px;
  padding: 14px 16px;
  background: #0c0c0c;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
}

.row-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.row-title h3 {
  margin: 0;
  color: #fff;
  font-size: 18px;
}

.row-main .content {
  color: #dcdcdc;
  font-size: 14px;
  line-height: 1.6;
  margin: 6px 0 0;
}

.movie {
  color: #4f9171;
  font-size: 14px;
  margin: 6px 0 0;
}

.time {
  color: #888;
  font-size: 12px;
  white-space: nowrap;
}

.author {
  color: #b7d9c3;
  font-weight: 700;
}

.row-meta {
  display: flex;
  align-items: flex-start;
}

.loading {
  text-align: center;
  color: #ccc;
}

.empty {
  text-align: center;
  color: #777;
  margin: 12px 0;
}

.search-bar {
  margin-top: 18px;
  display: flex;
  gap: 10px;
}

.search-bar input {
  flex: 1;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid #2d2d2d;
  background: #0a0a0a;
  color: #fff;
}

@media (max-width: 768px) {
  .hero {
    padding: 40px 20px;
  }

  .panel {
    margin: 20px;
    padding: 20px;
  }

  .row-card {
    grid-template-columns: 1fr;
  }
}
</style>
