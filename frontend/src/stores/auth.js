import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, signup as signupApi, getProfile as getProfileApi, updateProfile as updateProfileApi, deleteAccount as deleteAccountApi } from '@/api/auth'
import { useProductStore } from '@/stores/product'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))

  const isLoggedIn = computed(() => !!accessToken.value)

  async function signup(formData) {
    try {
      await signupApi(formData)
      console.log('회원가입 API 성공')
      await login({
        email: formData.email,
        password: formData.password,
      })
      console.log('자동 로그인 성공')
    } catch (e) {
      console.error('signup 에러:', e)
      throw e
    }
  }

  async function login(credentials) {
    const { data } = await loginApi(credentials)

    accessToken.value = data.access
    user.value = data.user
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    localStorage.setItem('user', JSON.stringify(data.user))

    useProductStore().clearRecommendations()
  }

  async function logout() {
    try {
      await logoutApi()
    } finally {
      accessToken.value = null
      user.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user')

      useProductStore().clearRecommendations()
    }
  }

  function loginWithKakao(access, refresh) {
    accessToken.value = access
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  async function fetchProfile() {
    const { data } = await getProfileApi()
    user.value = data
    localStorage.setItem('user', JSON.stringify(data))
  }

  async function updateProfile(formData) {
    const { data } = await updateProfileApi(formData)
    user.value = data
    localStorage.setItem('user', JSON.stringify(data))
  }

  async function deleteAccount() {
    await deleteAccountApi()
    accessToken.value = null
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }

  return { accessToken, user, isLoggedIn, signup, login, logout, loginWithKakao, fetchProfile, updateProfile, deleteAccount }
})