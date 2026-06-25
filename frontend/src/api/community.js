import apiClient from '@/api/axios'

// 게시글 목록 조회 (category 파라미터로 필터링 가능)
export const getPosts = (category = '') =>
  apiClient.get('/community/posts/', { params: category ? { category } : {} })

// 키워드로 게시글 검색 — 상품 상세에서 관련 글 찾을 때 사용
// search: 제목/본문 포함 키워드, limit: 최대 결과 수
export const searchPosts = (search, limit = 5) =>
  apiClient.get('/community/posts/', { params: { search, category: 'DEPOSIT', limit } })

// 게시글 상세 조회
export const getPost = (postId) => apiClient.get(`/community/posts/${postId}/`)

// 게시글 작성 - 이미지 포함 시 FormData로 전송, Content-Type은 브라우저가 자동 설정
export const createPost = (formData) =>
  apiClient.post('/community/posts/', formData, {
    headers: { 'Content-Type': undefined },
  })

// 게시글 수정 - 동일하게 FormData 사용
export const updatePost = (postId, formData) =>
  apiClient.put(`/community/posts/${postId}/`, formData, {
    headers: { 'Content-Type': undefined },
  })

// 게시글 삭제
export const deletePost = (postId) => apiClient.delete(`/community/posts/${postId}/`)

// 좋아요 토글
export const togglePostLike = (postId) => apiClient.post(`/community/posts/${postId}/like/`)

// 댓글 작성
export const createComment = (postId, data) => apiClient.post(`/community/posts/${postId}/comments/`, data)

// 댓글 삭제
export const deleteComment = (commentId) => apiClient.delete(`/community/comments/${commentId}/`)
