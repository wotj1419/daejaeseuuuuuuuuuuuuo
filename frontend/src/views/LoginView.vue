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
    <div class="auth-page">
        <h1>로그인</h1>
        <form @submit.prevent="submit" class="auth-form">
            <div class="field">
                <label>아이디</label>
                <input v-model="username" required />
            </div>

            <div class="field">
                <label>비밀번호</label>
                <input type="password" v-model="password" required />
            </div>

            <button :disabled="loading" class="btn">
                {{ loading ? '로그인 중...' : '로그인' }}
            </button> 
            
            <p v-if="error" class="error">{{ error }}</p>
        </form>
    </div>
</template>

<style scoped>
.auth-page {
    max-width: 400px;
    margin: 40px auto;
    padding: 20px;
}
.auth-form {
    display: flex;
    flex-direction: column;
    gap: 16px;
    margin-top: 20px;
}
.field {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.field input {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 6px;
}
.btn {
    padding: 12px;
    background: #000;
    color: #fff;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 16px;
    margin-top: 10px;
}
.btn:disabled {
    background: #ccc;
}
.error {
    color: red;
    font-size: 14px;
}
</style>
