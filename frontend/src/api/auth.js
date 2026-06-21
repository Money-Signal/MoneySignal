import apiClient from './axios'

// 회원가입
export const signup = (data) => apiClient.post('/accounts/signup/', data)
