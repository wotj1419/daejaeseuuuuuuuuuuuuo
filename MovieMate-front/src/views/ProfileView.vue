<template>
  <div>
    <h2>프로필</h2>
    <p class="muted">추천은 내가 누른 좋아요/클릭 기록을 기반으로 자동 개인화됩니다.</p>

    <div class="box">
      <div><b>저장된 추천 로그</b></div>
      <div class="muted">localStorage에 저장된 이벤트 수: {{ eventCount }}</div>
      <button class="btn" @click="reset">추천 기록 초기화</button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRecommendationStore } from '../stores/recommendation'

const rec = useRecommendationStore()
const eventCount = computed(() => rec.signals.events.length)

function reset() {
  localStorage.removeItem('moviemate_user_signals_v1')
  location.reload()
}
</script>

<style scoped>
.muted {
  color: #666;
  margin: 8px 0 16px;
}
.box {
  border: 1px solid #eee;
  border-radius: 10px;
  padding: 12px;
  max-width: 520px;
}
.btn {
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
}
</style>
