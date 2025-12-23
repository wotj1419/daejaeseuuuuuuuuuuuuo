<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { boardsApi } from '@/api/boards'
import { useAuthStore } from '@/stores/auth'

const freePosts = ref([])
const loading = ref(false)
const searchQuery = ref('')
const searchInput = ref('')

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

function goToDetail(postId) {
  router.push({ name: 'freeBoardDetail', params: { id: postId } })
}

function applySearch() {
  const normalized = searchInput.value.trim()
  searchInput.value = normalized
  searchQuery.value = normalized
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

      <div class="search-controls">
        <div class="search-field">
          <input
            v-model="searchInput"
            @keyup.enter="applySearch"
            type="text"
            placeholder="영화 제목이나 내용으로 검색"
          />
          <button class="search-btn" @click="applySearch" :disabled="loading">검색</button>
        </div>
        <button class="write-btn ghost" @click="goToCreate">글쓰기</button>
      </div>

      <div v-if="loading" class="loading">불러오는 중...</div>

      <div v-else-if="filteredPosts.length" class="post-table">
        <div class="table-head">
          <span class="col number">번호</span>
          <span class="col title">제목</span>
          <span class="col author">글쓴이</span>
          <span class="col date">작성일</span>
          <span class="col metric">조회</span>
          <span class="col metric">추천</span>
        </div>
        <div class="table-body">
          <article
            v-for="post in filteredPosts"
            :key="post.id"
            class="table-row"
            @click="goToDetail(post.id)"
            @keyup.enter="goToDetail(post.id)"
            tabindex="0"
            role="button"
            :aria-label="`자유게시글 ${post.title} 보기`"
          >
            <span class="col number">{{ post.id }}</span>
            <div class="col title">
              <p class="title-text">{{ post.title }}</p>
              <p v-if="post.movie_title" class="movie">영화 · {{ post.movie_title }}</p>
              <p class="content-snippet">{{ post.content }}</p>
            </div>
            <span class="col author">{{ post.author_username }}</span>
            <span class="col date">{{ formatDate(post.created_at) }}</span>
            <span class="col metric">{{ post.view_count ?? '-' }}</span>
            <span class="col metric">{{ post.recommendation_count ?? '-' }}</span>
          </article>
        </div>
      </div>

      <p v-else class="empty">아직 공유된 글이 없습니다.</p>
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

.search-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.search-field {
  flex: 1;
  display: flex;
  gap: 10px;
  min-width: 240px;
}

.search-field input {
  flex: 1;
  padding: 12px 16px;
  border-radius: 999px;
  border: 1px solid #2d2d2d;
  background: #0a0a0a;
  color: #fff;
}

.search-field input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-btn {
  border: 1px solid #4f9171;
  padding: 12px 26px;
  border-radius: 999px;
  background: #4f9171;
  color: #f3f7f3;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 110px;
}

.search-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.search-btn:not(:disabled):hover {
  background: #5da57f;
  border-color: #5da57f;
}

.post-table {
  border-radius: 12px;
  border: 1px solid #222;
  overflow-x: auto;
  background: #090909;
}

.table-head {
  display: grid;
  grid-template-columns: 72px minmax(220px, 1fr) 120px 150px 90px 90px;
  gap: 12px;
  padding: 14px 20px;
  border-bottom: 1px solid #222;
  text-transform: uppercase;
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  color: #aaa;
}

.table-body {
  display: flex;
  flex-direction: column;
}

.table-row {
  display: grid;
  grid-template-columns: 72px minmax(220px, 1fr) 120px 150px 90px 90px;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  background: #0b0b0b;
  align-items: center;
  transition: border-color 0.2s ease, transform 0.2s ease;
  cursor: pointer;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  border-color: #4f9171;
  transform: translateY(-2px);
}

.table-row:focus-visible {
  outline: 2px solid #4f9171;
  outline-offset: 2px;
}

.col {
  font-size: 0.95rem;
  color: #e3e3e3;
  display: flex;
  align-items: center;
}

.col.number,
.col.metric {
  justify-content: center;
}

.col.metric {
  font-weight: 600;
}

.col.title {
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}

.title-text {
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.movie {
  margin: 0;
  color: #4f9171;
  font-size: 0.85rem;
}

.content-snippet {
  margin: 0;
  color: #bdbdbd;
  font-size: 0.85rem;
  line-height: 1.4;
  max-height: 42px;
  overflow: hidden;
  text-overflow: ellipsis;
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

@media (max-width: 768px) {
  .hero {
    padding: 40px 20px;
  }

  .panel {
    margin: 20px;
    padding: 20px;
  }

  .search-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .search-field {
    width: 100%;
  }

  .table-head,
  .table-row {
    grid-template-columns: 64px minmax(180px, 1fr) 120px;
  }

  .col.metric {
    display: none;
  }

  .table-head {
    font-size: 0.65rem;
  }
}
</style>
