<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const formData = ref({
  username: '',
  email: '',
  password: '',
  password2: '',
  first_name: '',
  last_name: '',
})

const error = ref('')
const errors = ref({})

const handleRegister = async () => {
  error.value = ''
  errors.value = {}

  // 기본 유효성 검사
  if (!formData.value.username || !formData.value.email || !formData.value.password) {
    error.value = '필수 항목을 모두 입력해주세요.'
    return
  }

  if (formData.value.password !== formData.value.password2) {
    errors.value.password2 = '비밀번호가 일치하지 않습니다.'
    return
  }

  if (formData.value.password.length < 8) {
    errors.value.password = '비밀번호는 최소 8자 이상이어야 합니다.'
    return
  }

  const result = await authStore.register(formData.value)

  if (result.success) {
    router.push('/')
  } else {
    error.value = result.message
    // 백엔드에서 반환한 필드별 에러 처리
    if (result.errors) {
      errors.value = result.errors
    }
  }
}
</script>

<template>
  <div class="register-container">
    <div class="register-box">
      <h1>회원가입</h1>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">사용자명 *</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            placeholder="사용자명을 입력하세요"
            required
            autocomplete="username"
          />
          <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
        </div>

        <div class="form-group">
          <label for="email">이메일 *</label>
          <input
            id="email"
            v-model="formData.email"
            type="email"
            placeholder="이메일을 입력하세요"
            required
            autocomplete="email"
          />
          <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label for="first_name">이름</label>
            <input
              id="first_name"
              v-model="formData.first_name"
              type="text"
              placeholder="이름"
              autocomplete="given-name"
            />
          </div>

          <div class="form-group">
            <label for="last_name">성</label>
            <input
              id="last_name"
              v-model="formData.last_name"
              type="text"
              placeholder="성"
              autocomplete="family-name"
            />
          </div>
        </div>

        <div class="form-group">
          <label for="password">비밀번호 *</label>
          <input
            id="password"
            v-model="formData.password"
            type="password"
            placeholder="비밀번호 (최소 8자)"
            required
            autocomplete="new-password"
          />
          <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
        </div>

        <div class="form-group">
          <label for="password2">비밀번호 확인 *</label>
          <input
            id="password2"
            v-model="formData.password2"
            type="password"
            placeholder="비밀번호를 다시 입력하세요"
            required
            autocomplete="new-password"
          />
          <span v-if="errors.password2" class="field-error">{{ errors.password2 }}</span>
        </div>

        <div v-if="error" class="error-message">{{ error }}</div>

        <button type="submit" :disabled="authStore.loading" class="submit-button">
          {{ authStore.loading ? '가입 중...' : '회원가입' }}
        </button>
      </form>

      <div class="login-link">
        <p>이미 계정이 있으신가요? <RouterLink to="/login">로그인</RouterLink></p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 80vh;
  padding: 20px;
}

.register-box {
  width: 100%;
  max-width: 500px;
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

.register-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
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

.field-error {
  color: #c62828;
  font-size: 12px;
  margin-top: -4px;
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

.login-link {
  margin-top: 20px;
  text-align: center;
  color: #666;
  font-size: 14px;
}

.login-link a {
  color: #4CAF50;
  text-decoration: none;
  font-weight: 600;
}

.login-link a:hover {
  text-decoration: underline;
}

@media (max-width: 600px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

