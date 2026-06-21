import axios from 'axios'

// 모든 API 요청에 공통으로 사용할 axios 인스턴스
const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// 요청 인터셉터: 토큰이 있으면 모든 요청 헤더에 자동으로 붙여줌
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default apiClient
