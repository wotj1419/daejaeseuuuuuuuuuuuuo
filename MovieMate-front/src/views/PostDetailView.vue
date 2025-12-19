<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reviewsApi } from '@/api/reviews'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)

const review = ref(null)
const editMode = ref(false)
const content = ref('')
const rating = ref(5)

async function load() {
  try {
    const { data } = await reviewsApi.detail(id)
    review.value = data
    content.value = data.content
    rating.value = data.rating
  } catch (e) {
    console.error(e)
    alert('리뷰 상세 불러오기 실패')
  }
}

async function save() {
  try {
    await reviewsApi.update(id, { content: content.value, rating: Number(rating.value) })
    editMode.value = false
    await load()
  } catch (e) {
    console.error(e)
    alert('수정 실패 (권한/Method 허용 여부 확인)')
  }
}

async function removeReview() {
  if (!confirm('정말 삭제할까요?')) return
  try {
    await reviewsApi.remove(id)
    router.push('/')
  } catch (e) {
    console.error(e)
    alert('삭제 실패 (권한/Method 허용 여부 확인)')
  }
}

onMounted(load)
</script>

<template>
  <div v-if="review">
    <h2>리뷰 상세 #{{ review.id }}</h2>
    <p>작성자: <b>{{ review.username }}</b> / 평점: {{ review.rating }}</p>

    <div style="border:1px solid #eee; border-radius:12px; padding:12px; margin-top:10px;">
      <div v-if="!editMode">
        <p style="white-space: pre-wrap;">{{ review.content }}</p>
        <p style="color:#777; font-size:13px; margin-top:10px;">{{ review.created_at }}</p>

        <div style="display:flex; gap:10px; margin-top:10px;">
          <button @click="editMode = true" style="padding:9px 12px; cursor:pointer;">수정</button>
          <button @click="removeReview" style="padding:9px 12px; cursor:pointer;">삭제</button>
        </div>
      </div>

      <div v-else>
        <textarea v-model="content" style="width:100%; min-height:120px; padding:10px;"></textarea>
        <div style="display:flex; gap:10px; align-items:center; margin-top:10px;">
          <label>평점</label>
          <input v-model="rating" type="number" min="1" max="10" style="width:80px; padding:8px;" />
          <button @click="save" style="padding:9px 12px; cursor:pointer;">저장</button>
          <button @click="editMode = false" style="padding:9px 12px; cursor:pointer;">취소</button>
        </div>
      </div>
    </div>
  </div>
</template>
