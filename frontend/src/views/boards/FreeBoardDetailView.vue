<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { boardsApi } from '@/api/boards'
import { moviesApi } from '@/api/movies'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const postId = computed(() => Number(route.params.id))

const post = ref(null)
const loading = ref(false)
const error = ref('')
const posterPath = ref('')
const comments = ref([])
const commentsLoading = ref(false)
const commentInput = ref('')
const commentStatus = ref('')
const editStatus = ref('')
const deleteStatus = ref('')
const editingCommentId = ref(null)
const editingContent = ref('')
const deleteTargetId = ref(null)
const recommendStatus = ref('')
const isEditingPost = ref(false)
const postEditForm = ref({
  title: '',
  content: '',
})
const postDeleteModalOpen = ref(false)
const isOwnPost = computed(() => {
  return currentUsername.value && post.value && post.value.author_username === currentUsername.value
})

const formatDateTime = (iso) => {
  if (!iso) return ''
  return new Date(iso).toLocaleString('ko-KR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  })
}

const posterUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `https://image.tmdb.org/t/p/w500${path}`
}

async function fetchMoviePoster(query) {
  if (!query?.trim()) {
    posterPath.value = ''
    return
  }
  try {
    const { data } = await moviesApi.search(query.trim())
    const movie = (data?.results || [])[0]
    posterPath.value = movie?.poster_path || ''
  } catch (err) {
    console.error('Movie poster load failed', err)
    posterPath.value = ''
  }
}

const isAuthenticated = computed(() => authStore.isAuthenticated)
const currentUsername = computed(() => authStore.user?.username || '')

const isOwnComment = (comment) =>
  currentUsername.value && comment.author_username === currentUsername.value

async function loadComments() {
  if (!postId.value) return
  commentsLoading.value = true
  try {
    const { data } = await boardsApi.listComments(postId.value)
    comments.value = data
  } catch (err) {
    console.error('댓글 로드 실패', err)
  } finally {
    commentsLoading.value = false
  }
}

async function loadPost() {
  if (!postId.value) return
  loading.value = true
  error.value = ''
  post.value = null
  posterPath.value = ''
  commentStatus.value = ''
  recommendStatus.value = ''
  editStatus.value = ''
  deleteStatus.value = ''
  editingCommentId.value = null
  editingContent.value = ''
  deleteTargetId.value = null
  try {
    const { data } = await boardsApi.detail(postId.value)
    post.value = data
    await fetchMoviePoster(data.movie_title)
    await loadComments()
  } catch (err) {
    console.error('Free board detail error', err)
    error.value = err.response?.data?.detail || '글을 불러오는 데 실패했습니다.'
  } finally {
    loading.value = false
  }
}

watch(
  postId,
  () => {
    loadPost()
  },
  { immediate: true }
)

async function handleRecommend() {
  if (!postId.value) return
  recommendStatus.value = ''
  if (!isAuthenticated.value) {
    recommendStatus.value = '추천하려면 로그인해 주세요.'
    return
  }
  try {
    const { data } = await boardsApi.recommend(postId.value)
    post.value = data
    recommendStatus.value = '추천이 반영되었습니다.'
  } catch (err) {
    console.error('Recommendation error', err)
    recommendStatus.value = err.response?.data?.detail || '추천 중 오류가 발생했습니다.'
  }
}

async function submitComment() {
  if (!postId.value) return
  if (!isAuthenticated.value) {
    commentStatus.value = '댓글을 작성하려면 로그인해야 합니다.'
    return
  }
  if (!commentInput.value.trim()) return
  try {
    await boardsApi.createComment(postId.value, { content: commentInput.value.trim() })
    commentInput.value = ''
    commentStatus.value = '댓글이 등록되었습니다.'
    await loadComments()
    post.value.comment_count = (post.value.comment_count || 0) + 1
  } catch (err) {
    console.error('Comment submit error', err)
    commentStatus.value = err.response?.data?.detail || '댓글 등록 중 오류가 발생했습니다.'
  }
}

function startEditing(comment) {
  editingCommentId.value = comment.id
  editingContent.value = comment.content || ''
  editStatus.value = ''
}

function cancelEditing() {
  editingCommentId.value = null
  editingContent.value = ''
  editStatus.value = ''
}

async function submitCommentEdit(commentId) {
  if (!commentId) return
  if (!editingContent.value.trim()) {
    editStatus.value = '댓글 내용을 입력해주세요.'
    return
  }
  try {
    await boardsApi.updateComment(commentId, { content: editingContent.value.trim() })
    editStatus.value = '댓글이 수정되었습니다.'
    await loadComments()
    editingCommentId.value = null
    editingContent.value = ''
  } catch (err) {
    console.error('Comment edit error', err)
    editStatus.value = err.response?.data?.detail || '댓글 수정 중 오류가 발생했습니다.'
  }
}

function promptDeleteComment(commentId) {
  deleteTargetId.value = commentId
  deleteStatus.value = ''
}

function cancelDelete() {
  deleteTargetId.value = null
  deleteStatus.value = ''
}

async function confirmDeleteComment() {
  if (!deleteTargetId.value) return
  try {
    await boardsApi.deleteComment(deleteTargetId.value)
    commentStatus.value = '댓글이 삭제되었습니다.'
    await loadComments()
    if (post.value) {
      post.value.comment_count = Math.max(0, (post.value.comment_count || 1) - 1)
    }
    cancelDelete()
  } catch (err) {
    console.error('Comment delete error', err)
    deleteStatus.value = err.response?.data?.detail || '댓글 삭제 중 오류가 발생했습니다.'
  }
}

function goBack() {
  router.back()
}

function startEditingPost() {
  if (!post.value) return
  postEditForm.value = {
    title: post.value.title,
    content: post.value.content,
  }
  isEditingPost.value = true
}

function cancelEditingPost() {
  isEditingPost.value = false
  editStatus.value = ''
}

async function submitPostEdit() {
  if (!postId.value) return
  if (!postEditForm.value.title.trim() || !postEditForm.value.content.trim()) {
    editStatus.value = '제목과 내용을 모두 입력해주세요.'
    return
  }
  try {
    const { data } = await boardsApi.updatePost(postId.value, {
      title: postEditForm.value.title.trim(),
      content: postEditForm.value.content.trim(),
    })
    post.value = data
    isEditingPost.value = false
    editStatus.value = '게시글이 성공적으로 수정되었습니다.'
  } catch (err) {
    console.error('Post edit error', err)
    editStatus.value = err.response?.data?.detail || '게시글 수정 중 오류가 발생했습니다.'
  }
}

function promptDeletePost() {
  postDeleteModalOpen.value = true
}

function closeDeleteModal() {
  postDeleteModalOpen.value = false
}

async function confirmDeletePost() {
  if (!postId.value) return
  try {
    await boardsApi.deletePost(postId.value)
    router.replace({ name: 'freeBoard' })
  } catch (err) {
    console.error('Post delete error', err)
    alert(err.response?.data?.detail || '게시글 삭제 중 오류가 발생했습니다.')
    closeDeleteModal()
  }
}
</script>

<template>
  <div class="detail-page">
    <section v-if="loading" class="status-msg">페이지를 불러오는 중입니다...</section>
    <section v-else-if="error" class="status-msg error">{{ error }}</section>
    <section v-else-if="post" class="detail-layout">
      <header class="detail-header">
        <div class="header-title">
          <div v-if="isOwnPost && !isEditingPost" class="post-actions">
            <button type="button" @click="startEditingPost">수정</button>
            <button type="button" class="danger" @click="promptDeletePost">삭제</button>
          </div>
          <p v-if="post.movie_title" class="movie-chip">영화 · {{ post.movie_title }}</p>
          <input
            v-if="isEditingPost"
            v-model="postEditForm.title"
            class="edit-title-input"
            placeholder="제목을 입력하세요."
          />
          <h1 v-else>{{ post.title }}</h1>
          <div class="meta-row">
            <span class="meta-author">{{ post.author_username }}</span>
            <span class="meta-divider">·</span>
            <span class="meta-date">{{ formatDateTime(post.created_at) }}</span>
          </div>
        </div>
        <div class="header-meta">
          <div class="stats-bar">
            <div class="stat">
              <span>조회</span>
              <strong>{{ post.view_count ?? '-' }}</strong>
            </div>
            <div class="stat">
              <span>추천</span>
              <strong>{{ post.recommendation_count ?? '-' }}</strong>
            </div>
            <div class="stat">
              <span>댓글</span>
              <strong>{{ post.comment_count ?? '-' }}</strong>
            </div>
          </div>
          <div class="recommend-group">
            <button class="recommend-btn" type="button" @click="handleRecommend">
              추천하기
            </button>
            <p v-if="recommendStatus" class="status recommend-status">{{ recommendStatus }}</p>
          </div>
        </div>
      </header>

      <section class="post-content">
        <div class="poster-card">
          <img v-if="posterUrl(posterPath)" :src="posterUrl(posterPath)" alt="poster" />
          <div v-else class="poster-placeholder">No Image</div>
        </div>
        <div v-if="isEditingPost" class="post-edit-body">
          <textarea
            v-model="postEditForm.content"
            rows="15"
            placeholder="내용을 입력하세요."
          ></textarea>
          <div class="edit-actions">
            <button type="button" @click="submitPostEdit">저장</button>
            <button type="button" class="ghost" @click="cancelEditingPost">취소</button>
          </div>
          <p v-if="editStatus" class="status edit-status">{{ editStatus }}</p>
        </div>
        <article v-else class="text-card">
          <p>{{ post.content }}</p>
        </article>
      </section>

      <section class="comments-section">
        <div class="comments-header">
          <h3>댓글</h3>
          <span v-if="commentsLoading">댓글을 불러오는 중입니다...</span>
        </div>
        <div v-if="comments.length" class="comments-list">
          <article
            v-for="comment in comments"
            :key="comment.id"
            class="comment-card"
          >
            <header>
              <strong>{{ comment.author_username }}</strong>
              <span>{{ formatDateTime(comment.created_at) }}</span>
            </header>
            <div v-if="editingCommentId === comment.id" class="comment-edit-area">
              <textarea
                v-model="editingContent"
                rows="3"
                placeholder="수정할 내용을 입력하세요."
              ></textarea>
              <div class="edit-actions">
                <button type="button" @click="submitCommentEdit(comment.id)">
                  저장
                </button>
                <button type="button" class="ghost" @click="cancelEditing">
                  취소
                </button>
              </div>
              <p v-if="editStatus" class="status edit-status">{{ editStatus }}</p>
            </div>
            <p v-else class="comment-body">{{ comment.content }}</p>
            <div v-if="isOwnComment(comment)" class="comment-actions">
              <button type="button" @click="startEditing(comment)">수정</button>
              <button type="button" class="ghost" @click="promptDeleteComment(comment.id)">
                삭제
              </button>
            </div>
          </article>
        </div>
        <div v-else class="empty-comments">등록된 댓글이 없습니다.</div>

        <div class="comment-form">
          <label class="comment-label" for="comment-input">댓글 남기기</label>
          <textarea
            id="comment-input"
            v-model="commentInput"
            rows="3"
            placeholder="댓글을 남겨보세요."
            :disabled="!isAuthenticated"
          ></textarea>
          <button type="button" @click="submitComment" :disabled="!isAuthenticated || !commentInput.trim()">
            댓글 등록
          </button>
          <p v-if="!isAuthenticated" class="comment-hint">로그인 후 댓글을 작성할 수 있습니다.</p>
          <p v-if="commentStatus" class="status comment-status">{{ commentStatus }}</p>
        </div>
        <div v-if="deleteTargetId" class="delete-modal-backdrop">
          <div class="delete-modal">
            <p class="delete-title">댓글을 삭제하시겠습니까?</p>
            <div class="delete-actions">
              <button type="button" class="ghost" @click="cancelDelete">취소</button>
              <button type="button" @click="confirmDeleteComment">삭제</button>
            </div>
            <p v-if="deleteStatus" class="status delete-status">{{ deleteStatus }}</p>
          </div>
        </div>
      </section>

      <button class="back-btn" type="button" @click="goBack">목록으로 돌아가기</button>

      <div v-if="postDeleteModalOpen" class="delete-modal-backdrop">
        <div class="delete-modal">
          <p class="delete-title">게시글을 삭제하시겠습니까?</p>
          <p class="delete-desc">삭제 후에는 복구할 수 없습니다.</p>
          <div class="delete-actions">
            <button type="button" class="ghost" @click="closeDeleteModal">취소</button>
            <button type="button" class="danger-btn" @click="confirmDeletePost">삭제</button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #030303;
  padding-bottom: 60px;
}

.detail-layout {
  max-width: 1200px;
  margin: 0 auto;
  padding: 60px 30px 80px;
  color: #f5f5f5;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  gap: 32px;
  background: #0e0e0e;
  border: 1px solid #222;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.4);
}

.header-title {
  flex: 1;
}

.header-title h1 {
  margin: 0;
  font-size: 30px;
  font-weight: 700;
}

.movie-chip {
  margin: 0 0 8px;
  font-size: 14px;
  color: #9ed3b4;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.meta-row {
  margin-top: 12px;
  display: flex;
  gap: 6px;
  font-size: 14px;
  color: #b7b7b7;
}

.header-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
}

.stats-bar {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
}

.stat {
  min-width: 90px;
  background: #050505;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 12px 16px;
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.stat strong {
  font-size: 20px;
  font-weight: 800;
  color: #fff;
}

.recommend-group {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
}

.recommend-btn {
  padding: 12px 24px;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #1db954, #0fbc70);
  color: #030303;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.recommend-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  box-shadow: none;
}

.recommend-status {
  font-size: 12px;
}

.post-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.post-actions button {
  padding: 8px 18px;
  font-size: 13px;
  font-weight: 600;
  border-radius: 999px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #ccc;
  backdrop-filter: blur(8px);
}

.post-actions button:hover {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
}

.post-actions button.danger {
  background: rgba(255, 71, 87, 0.1);
  border-color: rgba(255, 71, 87, 0.2);
  color: #ff4757;
}

.post-actions button.danger:hover {
  background: #ff4757;
  border-color: #ff4757;
  color: #fff;
  box-shadow: 0 4px 15px rgba(255, 71, 87, 0.3);
}

.edit-title-input {
  width: 100%;
  background: #000;
  border: 1px solid #1db954;
  color: #fff;
  font-size: 24px;
  font-weight: 700;
  padding: 8px 12px;
  border-radius: 8px;
}

.post-edit-body textarea {
  width: 100%;
  background: #000;
  border: 1px solid #333;
  color: #fff;
  padding: 16px;
  border-radius: 8px;
  resize: vertical;
  margin-bottom: 16px;
}

.post-edit-body textarea:focus {
  border-color: #1db954;
}

.danger-btn {
  background: #ff4444 !important;
  color: #fff !important;
}

.status.error {
  color: #ff4444;
}

.post-content {
  margin-top: 30px;
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 28px;
}

.poster-card {
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid #222;
  background: #090909;
  min-height: 420px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.poster-card img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder {
  color: #777;
  font-size: 14px;
}

.text-card {
  background: #0c0c0c;
  border-radius: 16px;
  border: 1px solid #222;
  padding: 28px;
  font-size: 16px;
  line-height: 1.8;
  white-space: pre-line;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.35);
}

.comments-section {
  margin-top: 40px;
  background: #0c0c0c;
  border-radius: 16px;
  border: 1px solid #222;
  padding: 28px;
  box-shadow: inset 0 0 40px rgba(0, 0, 0, 0.35);
}

.comments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.comments-header h3 {
  margin: 0;
  font-size: 18px;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.comment-card {
  border-radius: 12px;
  border: 1px solid #1d1d1d;
  padding: 12px 14px;
  background: #090909;
}

.comment-card header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #b6b6b6;
  margin-bottom: 6px;
}

.comment-body {
  margin: 0;
  color: #e3e3e3;
  line-height: 1.5;
}

.comment-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  width: 100%;
}

.comment-actions button {
  border-radius: 999px;
  padding: 6px 18px;
  background: #1d1d1d;
  color: #fff;
  border: 1px solid transparent;
  cursor: pointer;
}

.comment-actions button.ghost {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.2);
}

.empty-comments {
  color: #888;
  font-size: 14px;
  margin-bottom: 20px;
}

.comment-edit-area textarea {
  width: 100%;
  border-radius: 12px;
  border: 1px solid #1d1d1d;
  background: #040404;
  color: #f4f4f4;
  font-size: 14px;
  padding: 10px 14px;
  resize: vertical;
}

.edit-actions {
  margin-top: 10px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.edit-actions button {
  border-radius: 999px;
  padding: 6px 20px;
  border: none;
  background: linear-gradient(135deg, #1db954, #0fbc70);
  color: #030303;
  font-weight: 700;
  cursor: pointer;
}

.edit-actions button.ghost {
  background: transparent;
  color: #cfd0d0;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.comment-label {
  font-size: 14px;
  color: #b2b2b2;
}

.comment-form textarea {
  width: 100%;
  border-radius: 12px;
  border: 1px solid #1d1d1d;
  background: #040404;
  color: #f4f4f4;
  font-size: 14px;
  padding: 12px 14px;
  resize: vertical;
  min-height: 100px;
}

.comment-form button {
  width: fit-content;
  border-radius: 999px;
  border: none;
  background: linear-gradient(135deg, #1db954, #0fbc70);
  color: #030303;
  font-weight: 700;
  padding: 10px 28px;
  cursor: pointer;
  align-self: flex-end;
}

.comment-form button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.comment-hint {
  font-size: 13px;
  color: #b7b7b7;
}

.status {
  font-size: 13px;
  color: #9ed3b4;
}

.comment-status {
  margin-top: 0;
}

.delete-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 120;
}

.delete-modal {
  background: #0b0b0b;
  border-radius: 16px;
  border: 1px solid #1d1d1d;
  padding: 24px;
  width: min(360px, 90%);
  display: flex;
  flex-direction: column;
  gap: 12px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
}

.delete-title {
  margin: 0;
  font-weight: 600;
}

.delete-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.delete-actions button {
  border-radius: 999px;
  padding: 8px 22px;
  border: none;
  background: linear-gradient(135deg, #1db954, #0fbc70);
  color: #030303;
  font-weight: 700;
  cursor: pointer;
}

.delete-actions button.ghost {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #e0e0e0;
}

.delete-status {
  color: #ff6b6b;
}

.delete-desc {
  font-size: 14px;
  color: #888;
  margin: 0 0 10px;
}

.back-btn {
  margin-top: 30px;
  padding: 12px 24px;
  border-radius: 999px;
  border: 1px solid #4f9171;
  background: transparent;
  color: #4f9171;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: #4f9171;
  color: #030303;
}

.status-msg {
  max-width: 800px;
  margin: 120px auto;
  text-align: center;
  color: #bbb;
  font-size: 18px;
}

.status-msg.error {
  color: #ff6b6b;
}

@media (max-width: 960px) {
  .detail-layout {
    padding: 50px 20px 70px;
  }

  .detail-header {
    flex-direction: column;
  }

  .header-meta {
    align-items: flex-start;
  }

  .post-content {
    grid-template-columns: 1fr;
  }

  .poster-card {
    min-height: 360px;
  }
}

@media (max-width: 600px) {
  .detail-header,
  .text-card,
  .post-content {
    padding: 24px;
  }

  .stats-bar {
    gap: 12px;
  }
}
</style>
