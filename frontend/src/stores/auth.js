import { defineStore } from 'pinia'
import { signup as signupApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // 회원가입 요청, 실패 시 에러를 그대로 throw해서 컴포넌트에서 처리
  async function signup(formData) {
    await signupApi(formData)
  }

  return { signup }
})
