<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const store = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
    loading.value = true
    error.value = ''
    try {
        await store.login(username.value, password.value)
        router.push({ name: 'home' })
    } catch (e) {
        console.error(e)
        // dj-rest-auth 에러 처리 (invalid credentials)
        if (e.response?.data?.non_field_errors) {
            error.value = '아이디 또는 비밀번호가 일치하지 않습니다.'
        } else {
            error.value = '로그인 실패. 다시 시도해주세요.'
        }
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="auth-container">
        <div class="auth-card">
            <div class="auth-header">
                <h1 class="auth-title">로그인</h1>
                <p class="auth-subtitle">MovieMate에 오신 것을 환영합니다</p>
            </div>
            
            <form @submit.prevent="submit" class="auth-form">
                <div class="input-group">
                    <label class="input-label">아이디</label>
                    <div class="input-wrapper">
                        <span class="input-icon">👤</span>
                        <input 
                            v-model="username" 
                            required 
                            class="input-field"
                            placeholder="아이디를 입력하세요"
                        />
                    </div>
                </div>

                <div class="input-group">
                    <label class="input-label">비밀번호</label>
                    <div class="input-wrapper">
                        <span class="input-icon">🔒</span>
                        <input 
                            type="password" 
                            v-model="password" 
                            required 
                            class="input-field"
                            placeholder="비밀번호를 입력하세요"
                        />
                    </div>
                </div>

                <button :disabled="loading" class="submit-btn">
                    <span v-if="!loading">로그인</span>
                    <span v-else class="loading-spinner"></span>
                    <span v-if="loading">로그인 중...</span>
                </button>
                
                <div v-if="error" class="error-message">
                    <span class="error-icon">⚠️</span>
                    {{ error }}
                </div>

                <div class="auth-footer">
                    <p class="footer-text">
                        계정이 없으신가요? 
                        <RouterLink to="/signup" class="footer-link">회원가입</RouterLink>
                    </p>
                </div>
            </form>
        </div>
    </div>
</template>

<style scoped>
.auth-container {
    min-height: calc(100vh - 70px);
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    background: linear-gradient(135deg, #1a0a1a 0%, #0a0a0a 100%);
}

.auth-card {
    width: 100%;
    max-width: 480px;
    background: rgba(20, 20, 20, 0.8);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 48px 40px;
    box-shadow: 0 8px 32px rgba(29, 185, 84, 0.2);
    border: 1px solid rgba(29, 185, 84, 0.1);
}

.auth-header {
    text-align: center;
    margin-bottom: 40px;
}

.auth-title {
    font-size: 36px;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 12px;
    background: linear-gradient(135deg, #1DB954 0%, #169B43 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.auth-subtitle {
    font-size: 16px;
    color: #888;
}

.auth-form {
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.input-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
}

.input-label {
    font-size: 14px;
    font-weight: 600;
    color: #1DB954;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.input-wrapper {
    position: relative;
    display: flex;
    align-items: center;
}

.input-icon {
    position: absolute;
    left: 16px;
    font-size: 20px;
    pointer-events: none;
    z-index: 1;
}

.input-field {
    width: 100%;
    padding: 16px 16px 16px 50px;
    background: rgba(255, 255, 255, 0.05);
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    font-size: 16px;
    color: #ffffff;
    transition: all 0.3s ease;
}

.input-field::placeholder {
    color: rgba(255, 255, 255, 0.3);
}

.input-field:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.08);
    border-color: #1DB954;
    box-shadow: 0 0 20px rgba(29, 185, 84, 0.3);
}

.submit-btn {
    padding: 18px;
    background: linear-gradient(135deg, #1DB954 0%, #169B43 100%);
    color: #000000;
    border: none;
    border-radius: 12px;
    font-size: 18px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.3s ease;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-top: 8px;
    box-shadow: 0 4px 20px rgba(29, 185, 84, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
}

.submit-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 6px 25px rgba(29, 185, 84, 0.6);
}

.submit-btn:active:not(:disabled) {
    transform: translateY(0);
}

.submit-btn:disabled {
    background: #555;
    cursor: not-allowed;
    box-shadow: none;
}

.loading-spinner {
    width: 18px;
    height: 18px;
    border: 3px solid rgba(0, 0, 0, 0.1);
    border-top: 3px solid #000;
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.error-message {
    background: rgba(255, 68, 68, 0.1);
    border: 1px solid rgba(255, 68, 68, 0.3);
    border-radius: 12px;
    padding: 14px 16px;
    color: #FF4444;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.error-icon {
    font-size: 18px;
}

.auth-footer {
    margin-top: 8px;
    text-align: center;
}

.footer-text {
    color: #888;
    font-size: 14px;
}

.footer-link {
    color: #1DB954;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
}

.footer-link:hover {
    color: #169B43;
    text-shadow: 0 0 10px rgba(29, 185, 84, 0.5);
}

/* Responsive */
@media (max-width: 576px) {
    .auth-card {
        padding: 32px 24px;
    }
    
    .auth-title {
        font-size: 28px;
    }
}
</style>

