<script setup>
import { onMounted, ref } from 'vue'

const emit = defineEmits(['finish'])
const fadeOut = ref(false)

onMounted(() => {
  // 5초 후 자동으로 페이드 아웃
  setTimeout(() => {
    fadeOut.value = true
    setTimeout(() => {
      emit('finish')
    }, 1000)
  }, 5000)
})
</script>

<template>
  <div class="intro-overlay" :class="{ 'fade-out': fadeOut }">
    <div class="intro-content">
      <h1 class="intro-logo">MovieMate</h1>
      <p class="intro-tagline">Your Cinematic Journey Begins</p>
    </div>
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
  background-image: url('/intro-base.png');
  background-size: cover;
  background-position: center;
  z-index: 9999;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: opacity 1s ease-out;
  animation: ken-burns 20s ease-in-out forwards;
}

.intro-overlay.fade-out {
  opacity: 0;
}

.intro-content {
  text-align: center;
  z-index: 2;
  animation: fade-in-up 1.5s ease-out;
}

.intro-logo {
  font-size: 80px;
  font-weight: 900;
  color: #1DB954;
  margin-bottom: 20px;
  letter-spacing: 6px;
  text-shadow: 
    0 0 40px rgba(29, 185, 84, 0.8),
    0 0 80px rgba(29, 185, 84, 0.5),
    0 0 120px rgba(0, 0, 0, 0.9);
  animation: pulse-glow 3s infinite ease-in-out;
}

.intro-tagline {
  font-size: 20px;
  color: #fff;
  letter-spacing: 3px;
  text-transform: uppercase;
  opacity: 0.9;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
  animation: fade-in 2s ease-out 0.5s both;
}

@keyframes ken-burns {
  0% { 
    transform: scale(1);
    filter: brightness(0.7);
  }
  100% { 
    transform: scale(1.2) translate(2%, 2%);
    filter: brightness(1);
  }
}

@keyframes pulse-glow {
  0%, 100% { 
    opacity: 0.8; 
    transform: scale(1);
    text-shadow: 
      0 0 30px rgba(29, 185, 84, 0.6),
      0 0 60px rgba(29, 185, 84, 0.4);
  }
  50% { 
    opacity: 1; 
    transform: scale(1.05);
    text-shadow: 
      0 0 60px rgba(29, 185, 84, 1),
      0 0 120px rgba(29, 185, 84, 0.6),
      0 0 180px rgba(29, 185, 84, 0.3);
  }
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

@keyframes fade-in {
  0% { opacity: 0; }
  100% { opacity: 0.9; }
}
</style>
