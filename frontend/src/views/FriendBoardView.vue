<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { boardsApi } from '@/api/boards'
import { accountsApi } from '@/api/accounts'
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()
const router = useRouter()

const friendPosts = ref([])
const friends = ref([])
const loading = ref(false)
const creating = ref(false)
const status = ref('')
const form = reactive({
  title: '',
  content: '',
  movie_title: '',
  invited_usernames: [],
})

const isAuthenticated = computed(() => authStore.isAuthenticated)

const formatDate = (value) => {
  if (!value) return ''
  return new Date(value).toLocaleString('ko-KR', { dateStyle: 'medium', timeStyle: 'short' })
}

async function loadFriendPosts() {
  if (!isAuthenticated.value) {
    friendPosts.value = []
    return
  }
  loading.value = true
  try {
    const { data } = await boardsApi.listFriends()
    friendPosts.value = data
  } catch (error) {
    console.error(error)
    status.value = '친구게시판을 불러오는 중 문제가 발생했습니다.'
  } finally {
    loading.value = false
  }
}

async function loadFriends() {
  if (!isAuthenticated.value) return
  try {
    const { data } = await accountsApi.getFriends()
    friends.value = data
  } catch (error) {
    console.error(error)
  }
}

function goLogin() {
  router.push({ name: 'login' })
}

async function createFriendPost() {
  status.value = ''
  if (!form.title.trim() || !form.content.trim()) {
    status.value = '제목과 내용을 모두 입력해주세요.'
    return
  }
  if (!isAuthenticated.value) {
    status.value = '로그인 후 친구게시판에 글을 쓸 수 있습니다.'
    return
  }
  if (!form.invited_usernames.length) {
    status.value = '초대할 친구를 선택해주세요.'
    return
  }

  creating.value = true
  try {
    await boardsApi.createFriend({
      title: form.title.trim(),
      content: form.content.trim(),
      movie_title: form.movie_title.trim(),
      invited_usernames: [...form.invited_usernames],
    })
    status.value = '친구들에게 공유했습니다.'
    form.title = ''
    form.content = ''
    form.movie_title = ''
    form.invited_usernames = []
    await loadFriendPosts()
  } catch (error) {
    console.error(error)
    status.value = error.response?.data?.detail || '글을 등록하는 동안 오류가 발생했습니다.'
  } finally {
    creating.value = false
  }
}

onMounted(() => {
  loadFriendPosts()
  loadFriends()
})

watch(isAuthenticated, (auth) => {
  if (auth) {
    loadFriendPosts()
    loadFriends()
  } else {
    friendPosts.value = []
    friends.value = []
    form.invited_usernames = []
    status.value = ''
  }
})
</script>

<template>
  <div class="friend-board">
    <section class="hero">
      <p class="hero-label">Board Space</p>
      <h1>친구게시판</h1>
      <p>초대한 친구들과 자신의 취향을 나눠보세요.</p>
    </section>

    <section class="panel">
      <div class="panel-heading">
        <h2>초대 대상 선택</h2>
        <span class="chip">{{ friends.length }}명</span>
      </div>
      <div v-if="!isAuthenticated" class="auth-gate">
        <p>로그인 후 친구를 초대하세요.</p>
        <button class="login-btn" @click="goLogin">로그인하러 가기</button>
      </div>
      <div v-else>
        <div v-if="friends.length" class="friends-list">
          <label v-for="friend in friends" :key="friend.username" class="friend-pill">
            <input type="checkbox" :value="friend.username" v-model="form.invited_usernames" />
            {{ friend.username }}
          </label>
        </div>
        <p v-else class="hint">친구를 추가하면 자동으로 초대 목록에 표시됩니다.</p>
      </div>

      <form class="form" @submit.prevent="createFriendPost">
        <input v-model="form.movie_title" type="text" placeholder="공유할 영화 제목 (선택)" />
        <input v-model="form.title" type="text" placeholder="제목" required />
        <textarea v-model="form.content" rows="4" placeholder="친구들과 나눌 감상을 적어보세요" required />
        <button type="submit" :disabled="creating">
          {{ creating ? '초대 중...' : '친구들과 공유하기' }}
        </button>
        <p v-if="status" class="status">{{ status }}</p>
      </form>
    </section>

    <section class="panel">
      <div class="panel-heading">
        <h2>친구 공유 피드</h2>
        <span>{{ friendPosts.length }}개 제목</span>
      </div>
      <div v-if="loading" class="loading">친구 게시판 글을 불러오는 중...</div>
      <div v-else-if="friendPosts.length" class="posts">
        <article v-for="post in friendPosts" :key="post.id" class="card">
          <div class="card-header">
            <span>{{ post.author_username }}</span>
            <span class="time">{{ formatDate(post.created_at) }}</span>
          </div>
          <h3>{{ post.title }}</h3>
          <p v-if="post.movie_title" class="movie">🎬 {{ post.movie_title }}</p>
          <p class="content">{{ post.content }}</p>
          <p v-if="post.invited.length" class="invited">
            초대한 친구: {{ post.invited.join(', ') }}
          </p>
        </article>
      </div>
      <p v-else class="empty">친구들이 아직 공유한 글이 없습니다.</p>
    </section>
  </div>
</template>

<style scoped>
 .friend-board {
  min-height: 100vh;
  background: #020202;
  padding-bottom: 60px;
}

.hero {
  padding: 60px 50px;
  background: linear-gradient(135deg, rgba(29, 185, 84, 0.1), rgba(6, 6, 6, 0.95));
  color: #fff;
  border-bottom: 1px solid #111;
}

.hero-label {
  font-size: 12px;
  letter-spacing: 0.6em;
  text-transform: uppercase;
  margin-bottom: 10px;
  color: rgba(255, 255, 255, 0.6);
}

.hero h1 {
  font-size: 42px;
  margin-bottom: 8px;
}

.hero p {
  color: rgba(255, 255, 255, 0.8);
  max-width: 640px;
}

.panel {
  max-width: 1100px;
  margin: 30px auto;
  background: #0e0e0e;
  border-radius: 16px;
  padding: 26px;
  border: 1px solid #222;
  box-shadow: 0 20px 35px rgba(0, 0, 0, 0.6);
}

.panel-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  color: #e0e0e0;
}

.chip {
  padding: 4px 14px;
  border-radius: 20px;
  border: 1px solid rgba(29, 185, 84, 0.6);
  color: #1db954;
  font-size: 12px;
}

.auth-gate {
  text-align: center;
  padding: 24px;
  border: 1px dashed rgba(29, 185, 84, 0.6);
  border-radius: 12px;
  margin-bottom: 12px;
  color: #b1f0c9;
}

.login-btn {
  margin-top: 12px;
  border: none;
  background: transparent;
  color: #1db954;
  border-radius: 999px;
  padding: 10px 24px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.friends-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 12px;
}

.friend-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.02);
  font-size: 13px;
  color: #f0f0f0;
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
  border-radius: 999px;
  border: none;
  padding: 10px 28px;
  cursor: pointer;
  font-weight: 700;
  background: linear-gradient(135deg, #1db954, #0fbc70);
  color: #000;
  align-self: flex-end;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4);
}

.status {
  color: rgba(29, 185, 84, 0.9);
  font-size: 13px;
}

.posts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}

.card {
  border: 1px solid #222;
  border-radius: 14px;
  padding: 16px;
  background: #0b0b0b;
}

.card-header {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #aaa;
  margin-bottom: 8px;
}

.card h3 {
  margin: 0 0 6px;
  color: #fff;
}

.movie {
  color: #1db954;
  margin: 0 0 6px;
}

.content {
  font-size: 14px;
  color: #dcdcdc;
}

.invited {
  font-size: 12px;
  color: #9ea9a3;
  margin-top: 8px;
}

.empty {
  text-align: center;
  color: #777;
}

.loading {
  text-align: center;
  color: #777;
}

@media (max-width: 768px) {
  .hero {
    padding: 40px 20px;
  }

  .panel {
    margin: 18px;
    padding: 20px;
  }
}
</style>
