<script setup>
import { onMounted, ref } from 'vue'

const emit = defineEmits(['finish'])
const fadeOut = ref(false)
const videoRef = ref(null)

function handleFinish() {
  if (fadeOut.value) return
  fadeOut.value = true
  setTimeout(() => {
    emit('finish')
  }, 1000)
}

function skipIntro() {
  handleFinish()
}

onMounted(() => {
  // 비디오가 로드되지 않거나 중단될 경우를 대비한 세이프트 가드 (8초)
  setTimeout(() => {
    if (!fadeOut.value) {
      handleFinish()
    }
  }, 8000)
})
</script>

<template>
  <div class="intro-overlay" :class="{ 'fade-out': fadeOut }">
    <video
      ref="videoRef"
      class="intro-video"
      autoplay
      muted
      playsinline
      @ended="handleFinish"
    >
      <source src="/videos/movie_intro.mp4" type="video/mp4" />
    </video>
    
    <button class="skip-btn" @click="skipIntro">
      Skip Intro
      <span class="skip-icon">→</span>
    </button>
  </div>
</template>

<style scoped>
.intro-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: #000;
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: opacity 1s ease-out;
  overflow: hidden;
}

.intro-overlay.fade-out {
  opacity: 0;
  pointer-events: none;
}

.intro-video {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: translate(-50%, -50%);
  z-index: 1;
}

.intro-content {
  text-align: center;
  z-index: 2;
  pointer-events: none;
  animation: fade-in-up 1.5s ease-out;
}

.intro-logo {
  font-size: 80px;
  font-weight: 900;
  color: #1DB954;
  margin-bottom: 20px;
  letter-spacing: 6px;
  text-shadow: 
    0 0 40px rgba(0, 0, 0, 0.9),
    0 0 80px rgba(0, 0, 0, 0.5);
}

.intro-tagline {
  font-size: 20px;
  color: #fff;
  letter-spacing: 3px;
  text-transform: uppercase;
  opacity: 0.9;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
}

.skip-btn {
  position: absolute;
  bottom: 40px;
  right: 40px;
  z-index: 3;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 10px 20px;
  border-radius: 30px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.3s ease;
  letter-spacing: 1px;
}

.skip-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: translateX(5px);
  border-color: #1DB954;
}

.skip-icon {
  font-size: 18px;
}

@keyframes fade-in-up {
  0% {
    opacity: 0;
    transform: translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
