import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:8000/api',
  headers: { 'Content-Type': 'application/json' },
})

// 요청 인터셉터: access token을 모든 요청 헤더에 자동으로 붙여줌
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 응답 인터셉터: 401 에러(토큰 만료) 감지 → refresh token으로 자동 갱신 후 원래 요청 재시도
apiClient.interceptors.response.use(
  (response) => response,  // 정상 응답은 그대로 통과

  async (error) => {
    const originalRequest = error.config

    // 401이고 아직 재시도 안 한 요청인 경우에만 갱신 시도
    // _retry 플래그로 무한 루프 방지 (refresh 요청 자체가 401 나는 경우)
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const refreshToken = localStorage.getItem('refresh_token')

      if (!refreshToken) {
        // refresh token도 없으면 로그인 페이지로
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(error)
      }

      try {
        const { data } = await axios.post('http://127.0.0.1:8000/api/accounts/token/refresh/', {
          refresh: refreshToken,
        })

        // 새 access token 저장
        localStorage.setItem('access_token', data.access)
        originalRequest.headers.Authorization = `Bearer ${data.access}`

        // 실패했던 원래 요청 재시도
        return apiClient(originalRequest)

      } catch (refreshError) {
        // refresh token도 만료된 경우 → 완전히 로그아웃
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user')
        window.location.href = '/login'
        return Promise.reject(refreshError)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
