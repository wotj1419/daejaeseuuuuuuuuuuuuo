import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
    const token = ref(localStorage.getItem('token'))
    const user = ref(null)

    const isAuthenticated = computed(() => !!token.value)

    // API Base URL
    const API_URL = `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'}/api/v1/accounts`

    async function signup(username, password, email) {
        // dj-rest-auth registration
        await axios.post(`${API_URL}/registration/`, {
            username,
            password1: password,
            password2: password, // 간소화를 위해 같게 전달
            email
        })
        // 회원가입 후 자동 로그인 처리 or 로그인 유도
    }

    async function login(username, password) {
        const res = await axios.post(`${API_URL}/login/`, {
            username,
            password
        })
        const newToken = res.data.key
        token.value = newToken
        localStorage.setItem('token', newToken)

        // 유저 정보 가져오기 (선택)
        // await fetchUser()
    }

    function logout() {
        // 서버에 로그아웃 요청을 보낼 수도 있음 (토큰 무효화)
        try {
            axios.post(`${API_URL}/logout/`, {}, {
                headers: { Authorization: `Token ${token.value}` }
            })
        } catch (e) { console.error(e) }

        token.value = null
        user.value = null
        localStorage.removeItem('token')
    }

    return { token, user, isAuthenticated, signup, login, logout }
})
