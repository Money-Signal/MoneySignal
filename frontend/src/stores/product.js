import { ref } from 'vue'
import { defineStore } from 'pinia'
import { getProducts, getProductDetail, toggleLike, getLikedProducts, getRecommendations } from '@/api/product'

export const useProductStore = defineStore('product', () => {
  const products = ref([])       // 상품 목록
  const product = ref(null)      // 상품 상세
  const likedProducts = ref([])  // 찜한 상품 목록
  const recommendations = ref([])        // 추천 상품 목록
  const recommendationType = ref(null)   // 'personalized' | 'popular'
  const compareList = ref([])            // 비교할 상품 목록 (최대 3개)
  const isLoading = ref(false)
  const isRecommendLoading = ref(false)
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

      // 추천 섹션 상태 반영
      const recommended = recommendations.value.find((p) => p.id === productId)
      if (recommended) recommended.liked = liked

      return liked
    } catch (e) {
      error.value = '찜하기 처리 중 오류가 발생했습니다.'
    }
  }

  // 맞춤 추천 상품 조회
  // recommendationType이 이미 세팅돼 있으면 세션 내 캐시 사용 (재호출 스킵)
  async function fetchRecommendations({ force = false } = {}) {
    if (!force && recommendationType.value !== null) return
    isRecommendLoading.value = true
    try {
      const res = await getRecommendations()
      recommendations.value = res.data.results
      recommendationType.value = res.data.type
    } catch {
      recommendations.value = []
    } finally {
      isRecommendLoading.value = false
    }
  }

  // 프로필 수정 후 추천 결과 초기화 (다음 조회 시 재검색)
  function clearRecommendations() {
    recommendations.value = []
    recommendationType.value = null
  }

  // 비교 목록 추가 (최대 3개, 중복 제외)
  function addToCompare(product) {
    if (compareList.value.length >= 3) return false
    if (compareList.value.find(p => p.id === product.id)) return false
    compareList.value.push(product)
    return true
  }

  // 비교 목록에서 제거
  function removeFromCompare(productId) {
    compareList.value = compareList.value.filter(p => p.id !== productId)
  }

  // 비교 목록 전체 초기화
  function clearCompare() {
    compareList.value = []
  }

  // 비교 목록에 있는지 여부
  function isInCompare(productId) {
    return compareList.value.some(p => p.id === productId)
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
    products, product, likedProducts, recommendations, recommendationType,
    compareList,
    isLoading, isRecommendLoading, error,
    fetchProducts, fetchProductDetail, likeProduct, fetchLikedProducts,
    fetchRecommendations, clearRecommendations,
    addToCompare, removeFromCompare, clearCompare, isInCompare,
  }
})
