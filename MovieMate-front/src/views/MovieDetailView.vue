<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecommendationStore } from '@/stores/recommendation'

const route = useRoute()
const router = useRouter()
const store = useRecommendationStore()

const movieId = computed(() => Number(route.params.movieId))

function goCommunity() {
  router.push({ name: 'community', params: { movieId: movieId.value } })
}

onMounted(() => {
  store.fetchRecommend(movieId.value)
})
</script>

<template>
  <div>
    <h2>Movie Hub (movie_id: {{ movieId }})</h2>
    <p>이 페이지는 “영화 추천(F01)”을 보여주고, “커뮤니티(G)”로 연결합니다.</p>

    <button @click="goCommunity" style="padding:10px 14px; cursor:pointer; margin:10px 0;">
      이 영화 리뷰 커뮤니티로 가기
    </button>

    <h3>추천 영화</h3>
    <p v-if="store.loading">불러오는 중...</p>
    <p v-if="store.error">{{ store.error }}</p>

    <div v-if="store.items.length" style="display:grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap:12px; margin-top:12px;">
      <div v-for="m in store.items" :key="m.id" style="border:1px solid #eee; border-radius:12px; padding:10px;">
        <img v-if="m.poster_path" :src="m.poster_path" alt="poster"
             style="width:100%; height:260px; object-fit:cover; border-radius:10px; background:#f4f4f4;" />
        <div style="margin-top:10px; font-weight:700;">{{ m.title }}</div>
        <div style="margin-top:6px; color:#555; font-size:14px;">
          ⭐ {{ m.vote_average }} · 🔥 {{ m.popularity }}
        </div>
      </div>
    </div>
  </div>
</template>
