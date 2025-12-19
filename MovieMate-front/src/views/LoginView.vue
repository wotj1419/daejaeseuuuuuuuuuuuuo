<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')

const handleLogin = async () => {
  error.value = ''
  
  if (!username.value || !password.value) {
    error.value = '사용자명과 비밀번호를 입력해주세요.'
    return
  }

  const result = await authStore.login(username.value, password.value)
  
  if (result.success) {
    router.push('/')
  } else {
    error.value = result.message
  }
}
</script>

<template>
  <div class="login-container">
    <div class="login-box">
      <h1>로그인</h1>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">사용자명</label>
          <input
            id="username"
            v-model="username"
            type="text"
            placeholder="사용자명을 입력하세요"
            required
            autocomplete="username"
          />
        </div>

        <div class="form-group">
          <label for="password">비밀번호</label>
          <input
            id="password"
            v-model="password"
            type="password"
            placeholder="비밀번호를 입력하세요"
            required
            autocomplete="current-password"
          />
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <button type="submit" :disabled="authStore.loading" class="submit-button">
          {{ authStore.loading ? '로그인 중...' : '로그인' }}
        </button>
      </form>

      <div class="signup-link">
        <p>계정이 없으신가요? <RouterLink to="/register">회원가입</RouterLink></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 28px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: 600;
  color: #555;
  font-size: 14px;
}

input {
  padding: 12px 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  font-size: 16px;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #4CAF50;
}

.error-message {
  padding: 12px;
  background-color: #ffebee;
  color: #c62828;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
}

.submit-button {
  padding: 14px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.3s;
}

.submit-button:hover:not(:disabled) {
  background-color: #45a049;
}

.submit-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.signup-link {
  margin-top: 20px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.signup-link a {
  color: #4CAF50;
  text-decoration: none;
  font-weight: 600;
}

.signup-link a:hover {
  text-decoration: underline;
}
</style>

