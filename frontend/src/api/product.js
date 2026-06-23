import apiClient from '@/api/axios'

// 상품 목록 조회 (type: 'D'=예금 | 'S'=적금, bank: 은행명)
export const getProducts = (params = {}) => apiClient.get('/products/', { params })

// 상품 상세 조회
export const getProductDetail = (productId) => apiClient.get(`/products/${productId}/`)

// 찜하기 토글
export const toggleLike = (productId) => apiClient.post(`/products/${productId}/like/`)

// 찜한 상품 목록 조회
export const getLikedProducts = () => apiClient.get('/products/liked/')
