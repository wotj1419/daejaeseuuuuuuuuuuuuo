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
const createStatus = ref('')
const chatStatus = ref('')
const sendingMessage = ref(false)
const channelSearch = ref('')
const createModalOpen = ref(false)
const selectedChannel = ref(null)
const messageInput = ref('')
const friendSearch = ref('')
const channelDrafts = reactive({})

const form = reactive({
  title: '',
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
    createStatus.value = '친구게시판을 불러오는 중 문제가 발생했습니다.'
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

const channels = computed(() => {
  const map = new Map()
  const sorted = [...friendPosts.value].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  )
  sorted.forEach((post) => {
    const key = post.title || `room-${post.id}`
    if (!map.has(key)) {
      map.set(key, post)
    }
  })
  return Array.from(map.values())
})

const filteredChannels = computed(() => {
  const query = channelSearch.value.trim().toLowerCase()
  if (!query) return channels.value
  return channels.value.filter((channel) => {
    const title = (channel.title || '').toLowerCase()
    const invited = (channel.invited || []).join(' ').toLowerCase()
    return title.includes(query) || invited.includes(query)
  })
})

const channelMessages = computed(() => {
  if (!selectedChannel.value) return []
  return [...friendPosts.value]
    .filter((post) => post.title === selectedChannel.value.title)
    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
})

const activeChannelKey = computed(() => {
  if (!selectedChannel.value) return ''
  return selectedChannel.value.title || `room-${selectedChannel.value.id}`
})

const filteredFriends = computed(() => {
  const query = friendSearch.value.trim().toLowerCase()
  if (!query) return friends.value
  return friends.value.filter((friend) => {
    const username = (friend.username || '').toLowerCase()
    return username.includes(query)
  })
})

function selectChannel(channel) {
  selectedChannel.value = channel
  chatStatus.value = ''
}

function resetCreateForm() {
  form.title = ''
  form.invited_usernames = []
  friendSearch.value = ''
  createStatus.value = ''
}

function openCreateModal() {
  resetCreateForm()
  createModalOpen.value = true
}

function closeCreateModal() {
  createModalOpen.value = false
  resetCreateForm()
}

function toggleFriendSelection(username) {
  const index = form.invited_usernames.indexOf(username)
  if (index >= 0) {
    form.invited_usernames.splice(index, 1)
  } else {
    form.invited_usernames.push(username)
  }
  friendSearch.value = ''
}

async function createFriendPost() {
  createStatus.value = ''
  if (!form.title.trim()) {
    createStatus.value = '채팅방 제목을 입력해주세요.'
    return
  }
  if (!isAuthenticated.value) {
    createStatus.value = '로그인 후 친구게시판에 글을 쓸 수 있습니다.'
    return
  }
  if (!form.invited_usernames.length) {
    createStatus.value = '초대할 친구를 선택해주세요.'
    return
  }

  creating.value = true
  try {
    await boardsApi.createFriend({
      title: form.title.trim(),
      content: '채팅방이 생성되었습니다.',
      movie_title: '',
      invited_usernames: [...form.invited_usernames],
    })
    createStatus.value = '친구에게 공유했습니다.'
    await loadFriendPosts()
    closeCreateModal()
  } catch (error) {
    console.error(error)
    createStatus.value = error.response?.data?.detail || '글을 등록하는 동안 오류가 발생했습니다.'
  } finally {
    creating.value = false
  }
}

async function sendMessage() {
  chatStatus.value = ''
  if (!messageInput.value.trim()) return
  if (!selectedChannel.value) {
    chatStatus.value = '채팅방을 선택해주세요.'
    return
  }
  sendingMessage.value = true
  try {
    await boardsApi.createFriend({
      title: selectedChannel.value.title || `대화 ${selectedChannel.value.id}`,
      content: messageInput.value.trim(),
      movie_title: selectedChannel.value.movie_title || '',
    })
    messageInput.value = ''
    chatStatus.value = '메시지를 전송했습니다.'
    await loadFriendPosts()
  } catch (error) {
    console.error(error)
    chatStatus.value = error.response?.data?.detail || '메시지 전송에 실패했습니다.'
  } finally {
    sendingMessage.value = false
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
    createStatus.value = ''
    chatStatus.value = ''
    selectedChannel.value = null
    createModalOpen.value = false
  }
})

watch(filteredChannels, (list) => {
  if (!list.length) {
    selectedChannel.value = null
    return
  }
  if (!selectedChannel.value || !list.find((channel) => channel.title === selectedChannel.value.title)) {
    selectedChannel.value = list[0]
  }
})

watch(
  selectedChannel,
  () => {
    const key = activeChannelKey.value
    messageInput.value = key ? channelDrafts[key] || '' : ''
  },
  { immediate: true }
)

watch(messageInput, (value) => {
  const key = activeChannelKey.value
  if (!key) return
  channelDrafts[key] = value
})
</script>

<template>
  <div class="friend-board">
    <section class="hero">
      <p class="hero-label">Board Space</p>
      <h1>소통방</h1>
      <p>초대한 친구들과 자신의 취향을 나눠보세요.</p>
      <div class="hero-extras">
        <router-link class="ghost-btn" :to="{ name: 'nearbyBoard' }">영화관 찾기</router-link>
      </div>
    </section>

    <section class="panel chat-panel">
      <aside class="chat-sidebar">
        <div class="sidebar-header">
          <div>
            <p class="hero-label">CHATING</p>
            <h2>채팅방 탐색</h2>
          </div>
          <button class="icon-btn" type="button" @click="openCreateModal">+</button>
        </div>

        <div class="sidebar-search">
          <input
            v-model="channelSearch"
            type="text"
            placeholder="채팅방 제목 또는 참여자 검색"
          />
        </div>

        <div v-if="!isAuthenticated" class="auth-gate mini">
          <p>로그인 후 채팅룸을 만들고 대화를 나눠보세요.</p>
        </div>
        <div v-else>
          <div v-if="filteredChannels.length" class="channel-list">
            <button
              v-for="channel in filteredChannels"
              :key="channel.title || channel.id"
              type="button"
              class="channel-item"
              :class="{ active: selectedChannel && selectedChannel.title === channel.title }"
              @click="selectChannel(channel)"
            >
              <div>
                <strong>{{ channel.title ? channel.title : '새 채팅방' }}</strong>
                <p class="channel-invited">
                  {{ channel.invited.length ? channel.invited.join(', ') : '초대한 친구 없음' }}
                </p>
              </div>
              <span class="channel-time">{{ formatDate(channel.created_at) }}</span>
            </button>
          </div>
          <p v-else class="empty-list">
            아직 채팅방을 만들지 않았습니다. + 버튼으로 새로운 채팅방을 생성해보세요.
          </p>
        </div>
      </aside>

      <article class="chat-body">
        <div v-if="!isAuthenticated" class="auth-gate">
          <p>로그인 후 친구들과 메시지를 주고받을 수 있습니다.</p>
          <button class="login-btn" @click="goLogin">로그인</button>
        </div>
        <div v-else>
          <div v-if="selectedChannel" class="chat-header">
            <div>
              <p class="channel-label">채팅방</p>
              <h2>{{ selectedChannel.title ? selectedChannel.title : '제목 없음' }}</h2>
              <p class="channel-info">
                {{ selectedChannel.invited.length
                  ? selectedChannel.invited.join(', ')
                  : '초대한 친구 없음' }}
              </p>
            </div>
            <div class="chat-meta">
              <span>{{ channelMessages.length }}개의 메시지</span>
            </div>
          </div>
          <div v-else class="empty-state">
            <p>채팅방을 선택하거나 새 채팅방을 만들어보세요.</p>
          </div>

          <div v-if="selectedChannel" class="message-window">
            <article v-for="msg in channelMessages" :key="msg.id" class="message-card">
              <div class="message-avatar">
                {{ msg.author_username ? msg.author_username.charAt(0).toUpperCase() : 'A' }}
              </div>
              <div class="message-content">
                <header>
                  <strong>{{ msg.author_username ? msg.author_username : '알 수 없음' }}</strong>
                  <span>{{ formatDate(msg.created_at) }}</span>
                </header>
                <p>{{ msg.content }}</p>
              </div>
            </article>
          </div>

          <form class="message-form" @submit.prevent="sendMessage">
            <textarea
              v-model="messageInput"
              rows="2"
              placeholder="메시지를 입력하세요."
              :disabled="!selectedChannel"
            />
            <div class="form-actions">
              <button type="submit" :disabled="sendingMessage || !selectedChannel">
                {{ sendingMessage ? '전송 중...' : '전송' }}
              </button>
            </div>
            <p v-if="chatStatus" class="status chat-status">{{ chatStatus }}</p>
          </form>
        </div>
      </article>
    </section>

    <div v-if="createModalOpen" class="modal-backdrop">
      <div class="modal">
        <header class="modal-header">
          <div>
            <p class="hero-label">Create</p>
            <h3>채팅방 만들기</h3>
          </div>
          <button class="icon-btn" type="button" @click="closeCreateModal">×</button>
        </header>
        <label class="modal-label">채팅방 제목</label>
        <input v-model="form.title" type="text" placeholder="채팅방 제목을 입력하세요" />

        <label class="modal-label">친구 검색</label>
        <input
          v-model="friendSearch"
          type="text"
          placeholder="사용자 이름으로 검색"
        />

        <div v-if="filteredFriends.length" class="friends-checkboxes">
          <label
            v-for="friend in filteredFriends"
            :key="friend.username"
            class="friend-checkbox"
          >
            <input
              type="checkbox"
              :value="friend.username"
              :checked="form.invited_usernames.includes(friend.username)"
              @change="toggleFriendSelection(friend.username)"
            />
            {{ friend.username }}
          </label>
        </div>
        <p v-else class="empty-list">검색 결과가 없습니다.</p>

        <button class="modal-submit" type="button" @click="createFriendPost" :disabled="creating">
          {{ creating ? '생성 중...' : '채팅방 만들기' }}
        </button>
        <p v-if="createStatus" class="status">{{ createStatus }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.friend-board {
  min-height: 100vh;
  background: #020202;
  padding-bottom: 60px;
  color: #fff;
}

.hero {
  padding: 60px 50px;
  background: linear-gradient(135deg, rgba(29, 185, 84, 0.1), rgba(6, 6, 6, 0.95));
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

.hero-extras {
  margin-top: 12px;
}

.hero-extras .ghost-btn {
  border-radius: 999px;
  padding: 10px 18px;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.2);
  text-decoration: none;
  font-weight: 700;
}

.panel {
  width: calc(100% - 40px);
  margin: 20px auto;
  background: #0c0c0c;
  border-radius: 24px;
  border: 1px solid #1e1e1e;
  padding: 0;
  min-height: calc(100vh - 120px);
  box-shadow: 0 25px 45px rgba(0, 0, 0, 0.6);
}

.chat-panel {
  display: grid;
  grid-template-columns: minmax(320px, 420px) 1fr;
  gap: 16px;
  padding: 16px;
  min-height: calc(100vh - 180px);
}

.chat-sidebar {
  background: #0f0f0f;
  border-radius: 16px;
  border: 1px solid #161616;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 24px;
  min-height: calc(100vh - 160px);
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.icon-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: transparent;
  color: #fff;
  font-size: 20px;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s ease;
}

.icon-btn:hover {
  border-color: #1db954;
  color: #1db954;
}

.sidebar-search input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 999px;
  border: 1px solid #222;
  background: #050505;
  color: #f5f5f5;
  font-size: 14px;
}

.channel-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: calc(100vh - 260px);
  overflow-y: auto;
  padding: 8px 4px 4px;
}

.channel-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid transparent;
  background: #090909;
  color: #f0f0f0;
  cursor: pointer;
  transition: border-color 0.2s ease, transform 0.2s ease;
}

.channel-item.active {
  border-color: #1db954;
  box-shadow: 0 10px 20px rgba(29, 185, 84, 0.2);
  transform: translateY(-1px);
}

.channel-invited {
  font-size: 12px;
  color: #9cb7a6;
  margin: 4px 0 0;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.channel-time {
  font-size: 12px;
  color: #888;
  white-space: nowrap;
}

.empty-list {
  color: #888;
  font-size: 13px;
  text-align: center;
}

.chat-body {
  background: #0c0c0c;
  border-radius: 16px;
  border: 1px solid #1b1b1b;
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 18px;
  min-height: 580px;
  min-height: calc(100vh - 200px);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  border-bottom: 1px solid #1c1c1c;
  padding-bottom: 12px;
}

.channel-label {
  font-size: 12px;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #8c8c8c;
  margin-bottom: 6px;
}

.channel-info {
  color: #b7b7b7;
  margin-top: 6px;
  font-size: 14px;
}

.chat-meta {
  font-size: 12px;
  color: #999;
}

.message-window {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  padding-right: 4px;
}

.message-card {
  display: flex;
  gap: 12px;
  border-radius: 14px;
  border: 1px solid #1c1c1c;
  padding: 12px 14px;
  background: #090909;
}

.message-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: #1db954;
  color: #030303;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}

.message-content header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  font-size: 13px;
  color: #b6b6b6;
  margin-bottom: 6px;
}

.message-content p {
  margin: 0;
  color: #f1f1f1;
  line-height: 1.6;
  white-space: pre-wrap;
}

.message-form {
  border-top: 1px solid #1c1c1c;
  padding-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.message-form textarea {
  width: 100%;
  border-radius: 12px;
  border: 1px solid #1d1d1d;
  background: #040404;
  color: #f4f4f4;
  font-size: 14px;
  padding: 12px 14px;
  resize: vertical;
  min-height: 70px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.form-actions button {
  border-radius: 999px;
  background: linear-gradient(135deg, #1db954, #0fbc70);
  color: #000;
  border: none;
  padding: 10px 28px;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.form-actions button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status {
  color: rgba(29, 185, 84, 0.9);
  font-size: 13px;
}

.chat-status {
  margin-bottom: 0;
}

.auth-gate {
  text-align: center;
  padding: 18px;
  border: 1px dashed rgba(29, 185, 84, 0.6);
  border-radius: 12px;
  color: #b1f0c9;
}

.login-btn {
  margin-top: 10px;
  border: none;
  background: transparent;
  color: #1db954;
  border-radius: 999px;
  padding: 8px 20px;
  font-weight: 700;
  cursor: pointer;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 100;
}

.modal {
  background: #0c0c0c;
  border-radius: 20px;
  border: 1px solid #1f1f1f;
  padding: 24px;
  width: min(420px, 100%);
  box-shadow: 0 25px 45px rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-label {
  font-size: 13px;
  color: #b2b2b2;
  margin-bottom: 6px;
}

.modal input {
  border-radius: 10px;
  border: 1px solid #222;
  background: #050505;
  color: #fff;
  padding: 12px 14px;
}

.friends-checkboxes {
  max-height: 180px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-right: 6px;
}

.friend-checkbox {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid #1f1f1f;
  background: #080808;
  cursor: pointer;
}

.friend-checkbox input {
  width: 16px;
  height: 16px;
}

.modal-submit {
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #1db954, #0fbc70);
  color: #000;
  font-weight: 700;
  padding: 10px 28px;
  cursor: pointer;
  margin-top: 6px;
}

@media (max-width: 1024px) {
  .chat-panel {
    grid-template-columns: 280px 1fr;
  }
}

@media (max-width: 900px) {
  .chat-panel {
    grid-template-columns: 1fr;
  }

  .chat-sidebar,
  .chat-body {
    padding: 18px;
  }
}

@media (max-width: 600px) {
  .hero {
    padding: 40px 20px;
  }

  .message-card {
    flex-direction: column;
  }

  .chat-panel {
    grid-template-columns: 1fr;
  }
}
</style>
