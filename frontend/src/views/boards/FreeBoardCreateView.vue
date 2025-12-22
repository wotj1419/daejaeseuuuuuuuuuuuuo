<script setup>
import { computed, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { boardsApi } from '@/api/boards'
import { useAuthStore } from '@/stores/auth'

const form = reactive({
  title: '',
  content: '',
  movie_title: '',
})

const status = ref('')
const creating = ref(false)

const router = useRouter()
const authStore = useAuthStore()
const isAuthenticated = computed(() => authStore.isAuthenticated)

async function submitPost() {
  status.value = ''
  if (!form.title.trim() || !form.content.trim()) {
    status.value = '제목과 내용은 모두 입력해주세요.'
    return
  }
  if (!isAuthenticated.value) {
    status.value = '로그인 후에 글을 쓸 수 있습니다.'
    return
  }

  creating.value = true
  try {
    await boardsApi.createFree({
      title: form.title.trim(),
      content: form.content.trim(),
      movie_title: form.movie_title.trim(),
    })
    router.push({ name: 'freeBoard' })
  } catch (error) {
    console.error('글 등록 실패', error)
    status.value = error.response?.data?.detail || '글 등록에 실패했습니다.'
  } finally {
    creating.value = false
  }
}
</script>

<template>
  <div class="create-page">
    <section class="hero">
      <p class="hero-label">Board</p>
      <h1>자유게시판 글쓰기</h1>
      <p class="hero-sub">영화 이야기를 자유롭게 남겨보세요.</p>
    </section>

    <section class="panel">
      <form class="form" @submit.prevent="submitPost">
        <label>영화 제목 (선택)</label>
        <input v-model="form.movie_title" type="text" placeholder="공유할 영화 제목" />

        <label>제목</label>
        <input v-model="form.title" type="text" placeholder="제목을 입력하세요" required />

        <label>내용</label>
        <textarea
          v-model="form.content"
          rows="6"
          placeholder="감상이나 추천을 자유롭게 작성해주세요"
          required
        />

        <div class="actions">
          <button type="button" class="ghost" @click="router.push({ name: 'freeBoard' })">
            취소
          </button>
          <button type="submit" :disabled="creating">
            {{ creating ? '등록 중...' : '등록하기' }}
          </button>
        </div>
        <p v-if="status" class="status">{{ status }}</p>
      </form>
    </section>
  </div>
</template>

<style scoped>
.create-page {
  background: #030303;
  min-height: 100vh;
  padding-bottom: 60px;
  color: #fff;
}

.hero {
  background: linear-gradient(135deg, rgba(55, 102, 75, 0.25), rgba(25, 25, 25, 0.9));
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
  margin: 0;
  font-size: 38px;
  font-weight: 800;
}

.hero-sub {
  margin-top: 8px;
  color: rgba(255, 255, 255, 0.75);
}

.panel {
  max-width: 900px;
  margin: 32px auto;
  background: #111;
  border-radius: 16px;
  border: 1px solid #222;
  padding: 24px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
}

.form {
  display: grid;
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

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}

button {
  padding: 10px 18px;
  border-radius: 10px;
  border: 1px solid #4f9171;
  background: #37664b;
  color: #f3f7f3;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

button:hover {
  background: #4f9171;
  border-color: #4f9171;
}

button.ghost {
  background: transparent;
  color: #4f9171;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.status {
  color: #9ed3b4;
  font-size: 13px;
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
