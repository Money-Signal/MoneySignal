import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, signup as signupApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // localStorage에서 초기값 복원 (새로고침 해도 로그인 유지)
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!accessToken.value)

  async function signup(formData) {
    await signupApi(formData)
  }

  async function login(credentials) {
    const { data } = await loginApi(credentials)

    // 토큰과 유저 정보를 state와 localStorage에 저장
    accessToken.value = data.access
    user.value = data.user
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(data.user))
  }

  async function logout() {
    try {
      await logoutApi()
    } finally {
      // 서버 요청 실패해도 클라이언트 토큰은 무조건 삭제
      accessToken.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')
    }
  }

  // 카카오 로그인 콜백에서 받은 토큰을 저장 (API 호출 없이 URL 파라미터로 바로 처리)
  function loginWithKakao(access, refresh) {
    accessToken.value = access
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  return { accessToken, user, isLoggedIn, signup, login, logout, loginWithKakao }
})
