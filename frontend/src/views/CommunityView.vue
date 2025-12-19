<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { reviewsApi } from '@/api/reviews'

const route = useRoute()
const router = useRouter()
const movieId = computed(() => Number(route.params.movieId))

const reviews = ref([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const { data } = await reviewsApi.listByMovie(movieId.value)
    reviews.value = data
  } catch (e) {
    console.error(e)
    alert('리뷰 목록 불러오기 실패')
  } finally {
    loading.value = false
  }
}

function goCreate() {
  router.push({ name: 'postCreate', params: { movieId: movieId.value } })
}

function goDetail(id) {
  router.push({ name: 'postDetail', params: { id } })
}

onMounted(load)
</script>

<template>
  <div>
    <h2>커뮤니티 (movie_id: {{ movieId }})</h2>

    <button @click="goCreate" style="padding:10px 14px; cursor:pointer; margin:10px 0;">
      리뷰 작성
    </button>

    <p v-if="loading">불러오는 중...</p>

    <div v-if="reviews.length" style="display:flex; flex-direction:column; gap:10px;">
      <div v-for="r in reviews" :key="r.id" style="border:1px solid #eee; border-radius:12px; padding:12px;">
        <div style="display:flex; gap:12px; align-items:center;">
          <b>{{ r.username }}</b>
          <span>평점: {{ r.rating }}</span>
          <button @click="goDetail(r.id)" style="margin-left:auto; padding:6px 10px; cursor:pointer;">
            상세
          </button>
        </div>
        <div style="margin-top:8px;">{{ r.content }}</div>
        <div style="margin-top:8px; color:#777; font-size:13px;">{{ r.created_at }}</div>
      </div>
    </div>

    <p v-else-if="!loading">아직 리뷰가 없어요. 첫 리뷰를 작성해보자!</p>
  </div>
</template>
