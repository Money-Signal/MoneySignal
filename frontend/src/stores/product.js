import { ref } from 'vue'
import { defineStore } from 'pinia'
import { getProducts, getProductDetail, toggleLike, getLikedProducts } from '@/api/product'

export const useProductStore = defineStore('product', () => {
  const products = ref([])       // 상품 목록
  const product = ref(null)      // 상품 상세
  const likedProducts = ref([])  // 찜한 상품 목록
  const isLoading = ref(false)
  const error = ref(null)

  // 상품 목록 조회
  async function fetchProducts(params = {}) {
    isLoading.value = true
    error.value = null
    try {
      const res = await getProducts(params)
      products.value = res.data
    } catch (e) {
      error.value = '상품 목록을 불러오는 데 실패했습니다.'
    } finally {
      isLoading.value = false
    }
  }

  // 상품 상세 조회
  async function fetchProductDetail(productId) {
    isLoading.value = true
    error.value = null
    try {
      const res = await getProductDetail(productId)
      product.value = res.data
    } catch (e) {
      error.value = '상품 정보를 불러오는 데 실패했습니다.'
    } finally {
      isLoading.value = false
    }
  }

  // 찜하기 토글 (목록/상세 모두 즉시 반영)
  async function likeProduct(productId) {
    try {
      const res = await toggleLike(productId)
      const liked = res.data.liked

      // 상세 페이지 상태 반영
      if (product.value?.id === productId) {
        product.value.liked = liked
        product.value.like_count += liked ? 1 : -1
      }

      // 목록 페이지 상태 반영
      const target = products.value.find((p) => p.id === productId)
      if (target) target.liked = liked

      return liked
    } catch (e) {
      error.value = '찜하기 처리 중 오류가 발생했습니다.'
    }
  }

  // 찜한 상품 목록 조회
  async function fetchLikedProducts() {
    isLoading.value = true
    error.value = null
    try {
      const res = await getLikedProducts()
      likedProducts.value = res.data
    } catch (e) {
      error.value = '찜한 상품 목록을 불러오는 데 실패했습니다.'
    } finally {
      isLoading.value = false
    }
  }

  return {
    products, product, likedProducts, isLoading, error,
    fetchProducts, fetchProductDetail, likeProduct, fetchLikedProducts,
  }
})
