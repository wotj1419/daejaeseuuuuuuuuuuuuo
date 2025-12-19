<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useRecommendationStore } from '@/stores/recommendation'
import { moviesApi } from '@/api/movies'

const route = useRoute()
const router = useRouter()
const store = useRecommendationStore()

// movie id
const movieId = computed(() => Number(route.params.movieId))

// trailer
const trailerUrl = ref(null)
const trailerError = ref(null)
const trailerLoading = ref(false)

function goCommunity() {
  router.push({ name: 'community', params: { movieId: movieId.value } })
}

async function loadTrailer() {
  trailerLoading.value = true
  trailerError.value = null
  trailerUrl.value = null
  
  try {
    const { data } = await moviesApi.trailer(movieId.value)
    if (data.trailer) {
      trailerUrl.value = data.trailer
    } else {
      trailerError.value = '예고편이 없습니다.'
    }
  } catch (err) {
    console.error('예고편 로딩 오류:', err)
    trailerError.value = '예고편을 불러오지 못했습니다.'
  } finally {
    trailerLoading.value = false
  }
}

onMounted(async () => {
  // 추천 영화(F01)
  store.fetchRecommend(movieId.value)

  // 예고편(F)
  await loadTrailer()
})
</script>

<template>
  <div>
    <h2>Movie Hub (movie_id: {{ movieId }})</h2>
    <p>
      이 페이지는
      <strong>영화 추천(F01)</strong>,
      <strong>예고편(F)</strong>,
      <strong>커뮤니티(G)</strong>
      기능을 제공합니다.
    </p>

    <!-- 커뮤니티 이동 -->
    <button
      @click="goCommunity"
      style="padding:10px 14px; cursor:pointer; margin:10px 0;"
    >
      이 영화 리뷰 커뮤니티로 가기
    </button>

    <!-- 🎬 예고편 -->
    <section style="margin:24px 0;">
      <h3>🎬 예고편</h3>

      <div v-if="trailerLoading" style="text-align:center; padding:40px; color:#666;">
        예고편을 불러오는 중...
      </div>

      <div v-else-if="trailerUrl" class="trailer-container">
        <iframe
          :src="trailerUrl"
          width="100%"
          height="420"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
          class="trailer-iframe"
        />
      </div>

      <div v-else-if="trailerError" class="trailer-error">
        {{ trailerError }}
      </div>

      <div v-else class="trailer-error">
        예고편이 없습니다.
      </div>
    </section>

    <!-- ⭐ 추천 영화 -->
    <h3>추천 영화</h3>
    <p v-if="store.loading">불러오는 중...</p>
    <p v-if="store.error">{{ store.error }}</p>

    <div
      v-if="store.items.length"
      style="display:grid; grid-template-columns: repeat(auto-fill, minmax(190px, 1fr)); gap:12px; margin-top:12px;"
    >
      <div
        v-for="m in store.items"
        :key="m.id"
        style="border:1px solid #eee; border-radius:12px; padding:10px;"
      >
        <img
          v-if="m.poster_path"
          :src="m.poster_path"
          alt="poster"
          style="width:100%; height:260px; object-fit:cover; border-radius:10px; background:#f4f4f4;"
        />
        <div style="margin-top:10px; font-weight:700;">
          {{ m.title }}
        </div>
        <div style="margin-top:6px; color:#555; font-size:14px;">
          ⭐ {{ m.vote_average }} · 🔥 {{ m.popularity }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.trailer-container {
  position: relative;
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.trailer-iframe {
  width: 100%;
  height: 420px;
  border: none;
  border-radius: 12px;
  background: #000;
}

.trailer-error {
  text-align: center;
  padding: 40px;
  color: #666;
  background: #f5f5f5;
  border-radius: 12px;
  margin: 20px 0;
}
</style>
