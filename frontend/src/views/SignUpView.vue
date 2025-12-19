<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const store = useAuthStore()
const router = useRouter()

const form = ref({
    username: '',
    email: '',
    password: ''
})

const loading = ref(false)
const error = ref('')

async function submit() {
    loading.value = true
    error.value = ''
    try {
        await store.signup(form.value.username, form.value.password, form.value.email)
        alert('회원가입이 완료되었습니다! 로그인 해주세요.')
        router.push({ name: 'login' })
    } catch (e) {
        console.error(e)
        // dj-rest-auth 에러 응답 처리 (예: username exists)
        if (e.response?.data) {
            error.value = JSON.stringify(e.response.data)
        } else {
            error.value = '회원가입 실패'
        }
    } finally {
        loading.value = false
    }
}
</script>

<template>
    <div class="auth-page">
        <h1>회원가입</h1>
        <form @submit.prevent="submit" class="auth-form">
            <div class="field">
                <label>아이디</label>
                <input v-model="form.username" required />
            </div>
            
            <div class="field">
                <label>이메일</label>
                <input type="email" v-model="form.email" required />
            </div>

            <div class="field">
                <label>비밀번호</label>
                <input type="password" v-model="form.password" required />
            </div>

            <button :disabled="loading" class="btn">
                {{ loading ? '가입 중...' : '가입하기' }}
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
