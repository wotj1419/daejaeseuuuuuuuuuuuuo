<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { boardsApi } from '@/api/boards'
import { useAuthStore } from '@/stores/auth'

const freePosts = ref([])
const loading = ref(false)
const creating = ref(false)
const status = ref('')
const form = reactive({
  title: '',
  content: '',
  movie_title: '',
})

const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

const formatDate = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString('ko-KR', { dateStyle: 'medium', timeStyle: 'short' })
}

async function loadFreePosts() {
  loading.value = true
  try {
    const { data } = await boardsApi.listFree()
    freePosts.value = data
  } catch (error) {
    status.value = '자유게시판을 불러오던 중 문제가 발생했습니다.'
    console.error(error)
  } finally {
    loading.value = false
  }
}

async function createFreePost() {
  status.value = ''
  if (!form.title.trim() || !form.content.trim()) {
    status.value = '제목과 내용을 모두 입력해주세요.'
    return
  }
  if (!isAuthenticated.value) {
    status.value = '로그인 후 자유게시판에 글을 남길 수 있습니다.'
    return
  }

  creating.value = true
  try {
    await boardsApi.createFree({
      title: form.title.trim(),
      content: form.content.trim(),
      movie_title: form.movie_title.trim(),
    })
    status.value = '글이 등록되었습니다.'
    form.title = ''
    form.content = ''
    form.movie_title = ''
    await loadFreePosts()
  } catch (error) {
    console.error(error)
    status.value = error.response?.data?.detail || '글 등록에 실패했습니다.'
  } finally {
    creating.value = false
  }
}

onMounted(loadFreePosts)
</script>

<template>
  <div class="free-board">
    <section class="hero">
      <p class="hero-label">Board</p>
      <h1>자유게시판</h1>
      <p>깊은 밤 영화 이야기처럼 텍스트가 빛나는 공간에서 감상을 공유해보세요.</p>
    </section>

    <section class="panel">
      <h2>글 쓰기</h2>
      <form class="form" @submit.prevent="createFreePost">
        <input v-model="form.movie_title" type="text" placeholder="공유할 영화 제목 (선택)" />
        <input v-model="form.title" type="text" placeholder="제목" required />
        <textarea v-model="form.content" rows="4" placeholder="감상이나 추천을 자유롭게 작성해보세요" required />
        <button type="submit" :disabled="creating">
          {{ creating ? '등록 중...' : '자유롭게 공유하기' }}
        </button>
        <p v-if="status" class="status">{{ status }}</p>
      </form>
    </section>

    <section class="panel">
      <div class="panel-heading">
        <h2>최신 공유</h2>
        <span>{{ freePosts.length }}개의 글</span>
      </div>
      <div v-if="loading" class="loading">불러오는 중...</div>
      <div v-else-if="freePosts.length" class="posts">
        <article v-for="post in freePosts" :key="post.id" class="card">
          <div class="card-header">
            <span>{{ post.author_username }}</span>
            <span class="time">{{ formatDate(post.created_at) }}</span>
          </div>
          <h3>{{ post.title }}</h3>
          <p v-if="post.movie_title" class="movie">🎬 {{ post.movie_title }}</p>
          <p class="content">{{ post.content }}</p>
        </article>
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
  background: linear-gradient(135deg, rgba(29, 185, 84, 0.2), rgba(25, 25, 25, 0.9));
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

.hero h1 {
  font-size: 42px;
  font-weight: 800;
  margin-bottom: 8px;
}

.hero p {
  color: rgba(255, 255, 255, 0.75);
  max-width: 640px;
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

.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form input,
.form textarea {
  border-radius: 12px;
  border: 1px solid #272727;
  padding: 12px 16px;
  font-size: 14px;
  background: #050505;
  color: #fff;
}

.form button {
  align-self: flex-end;
  padding: 10px 28px;
  border-radius: 50px;
  border: none;
  background: linear-gradient(135deg, #1db954, #0fbc70);
  color: #000;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.5);
}

.status {
  color: rgba(29, 185, 84, 0.9);
  font-size: 13px;
}

.panel-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  color: #e5e5e5;
}

.posts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.card {
  border: 1px solid #222;
  border-radius: 12px;
  padding: 16px;
  background: #0c0c0c;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.03);
}

.card-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #aaa;
  margin-bottom: 6px;
}

.card h3 {
  margin: 0 0 6px;
  color: #fff;
}

.movie {
  color: #1db954;
  font-size: 14px;
}

.content {
  color: #dcdcdc;
  font-size: 14px;
  line-height: 1.6;
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
}
</style>
