<template>
  <div class="container py-4">
    <h2 class="fw-bold mb-4">금융상품 비교</h2>

    <!-- 추천 섹션 -->
    <div class="recommend-section mb-4">
      <div class="d-flex align-items-center mb-2 gap-2">
        <h5 class="fw-bold mb-0">
          맞춤 추천
        </h5>
        <span v-if="store.recommendationType === 'personalized'" class="badge-personalized">AI 추천</span>
      </div>


      <!-- 추천 로딩 -->
      <div v-if="store.isRecommendLoading" class="text-center py-3">
        <div class="spinner-border spinner-border-sm text-success" role="status" />
      </div>

      <!-- 비로그인 → 로그인 유도 -->
      <div v-else-if="store.recommendationType === 'not_logged_in'" class="recommend-nudge">
        <i class="bi bi-lightbulb-fill"></i>
        로그인하면 AI 맞춤 추천을 받을 수 있어요!
        <RouterLink to="/login" class="nudge-link">로그인하기 →</RouterLink>
      </div>

      <!-- 로그인 O + 금융정보 없음 → 프로필 입력 유도 -->
      <div v-else-if="store.recommendationType === 'no_profile'" class="recommend-nudge">
        <i class="bi bi-lightbulb-fill"></i>
        금융정보를 입력하면 AI 맞춤 추천을 받을 수 있어요!
        <RouterLink to="/mypage" class="nudge-link">마이페이지에서 설정하기 →</RouterLink>
      </div>

      <!-- 추천 카드 가로 스크롤 -->
      <div v-else-if="store.recommendations.length" class="recommend-scroll">
        <div
          v-for="product in store.recommendations"
          :key="product.id"
          class="recommend-card"
          @click="goDetail(product.id)"
        >
          <div class="d-flex justify-content-between align-items-start mb-2">
            <span class="badge bg-secondary small">{{ product.kor_co_nm }}</span>
            <button
              class="btn btn-sm p-0 border-0 like-btn"
              :class="product.liked ? 'text-danger' : 'text-muted'"
              @click.stop="onLike(product.id)"
            >
              <i :class="product.liked ? 'bi bi-heart-fill' : 'bi bi-heart'" />
            </button>
          </div>
          <p class="fw-semibold small mb-1 product-name">{{ product.fin_prdt_nm }}</p>
          <p class="text-muted" style="font-size:0.75rem">{{ product.join_member || '-' }}</p>
          <div class="text-end mt-auto">
            <span class="text-success fw-bold">
              {{ product.max_intr_rate2 != null ? product.max_intr_rate2 + '%' : '-' }}
            </span>
            <span class="text-muted" style="font-size:0.75rem"> 최고금리</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 예금/적금 탭 -->
    <ul class="nav nav-tabs mb-3">
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'D' }"
          @click="changeTab('D')"
        >
          정기예금
        </button>
      </li>
      <li class="nav-item">
        <button
          class="nav-link"
          :class="{ active: activeTab === 'S' }"
          @click="changeTab('S')"
        >
          정기적금
        </button>
      </li>
    </ul>

    <!-- 은행명 검색 필터 -->
    <div class="mb-4">
      <input
        v-model="bankFilter"
        type="text"
        class="form-control w-auto"
        placeholder="은행명으로 검색"
        @input="onBankFilter"
      />
    </div>

    <!-- 로딩 -->
    <div v-if="store.isLoading" class="text-center py-5">
      <div class="spinner-border text-success" role="status" />
    </div>

    <!-- 에러 -->
    <div v-else-if="store.error" class="alert alert-danger">
      {{ store.error }}
    </div>

    <!-- 상품 목록 -->
    <div v-else>
      <div v-if="store.products.length === 0" class="text-center text-muted py-5">
        조건에 맞는 상품이 없습니다.
      </div>

      <div class="row g-3">
        <div
          v-for="product in store.products"
          :key="product.id"
          class="col-md-6 col-lg-4"
        >
          <div
            class="card h-100 shadow-sm product-card"
            @click="goDetail(product.id)"
          >
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <span class="badge bg-secondary">{{ product.kor_co_nm }}</span>
                <!-- 찜하기 버튼 -->
                <button
                  class="btn btn-sm p-0 border-0 like-btn"
                  :class="product.liked ? 'text-danger' : 'text-muted'"
                  @click.stop="onLike(product.id)"
                >
                  <i :class="product.liked ? 'bi bi-heart-fill' : 'bi bi-heart'" style="font-size: 1.2rem;" />
                </button>
              </div>

              <h6 class="card-title fw-bold">{{ product.fin_prdt_nm }}</h6>

              <p class="card-text text-muted small mb-1">가입방법: {{ product.join_way || '-' }}</p>
              <p class="card-text text-muted small mb-2">가입대상: {{ product.join_member || '-' }}</p>

              <div class="text-end">
                <span class="text-success fw-bold fs-5">
                  {{ product.max_intr_rate2 != null ? product.max_intr_rate2 + '%' : '-' }}
                </span>
                <span class="text-muted small ms-1">최고금리</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useProductStore } from '@/stores/product'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const store = useProductStore()
const authStore = useAuthStore()

const activeTab = ref('D')   // 기본: 정기예금
const bankFilter = ref('')
let filterTimer = null

onMounted(() => {
  store.fetchProducts({ type: activeTab.value })
  store.fetchRecommendations()
})

function changeTab(type) {
  activeTab.value = type
  bankFilter.value = ''
  store.fetchProducts({ type })
}

// 은행 필터 300ms 디바운스
function onBankFilter() {
  clearTimeout(filterTimer)
  filterTimer = setTimeout(() => {
    store.fetchProducts({ type: activeTab.value, bank: bankFilter.value })
  }, 300)
}

function goDetail(id) {
  router.push({ name: 'productDetail', params: { id } })
}

async function onLike(productId) {
  if (!authStore.isLoggedIn) {
    router.push({ name: 'login' })
    return
  }
  await store.likeProduct(productId)
}
</script>

<style scoped>
/* 추천 섹션 */
.recommend-section {
  background: linear-gradient(135deg, #f5faf5 0%, #edf4ee 100%);
  border-radius: 14px;
  padding: 1.25rem 1.25rem 1rem;
  border: 1px solid #d8ead9;
}

.badge-personalized {
  font-size: 0.7rem;
  font-weight: 700;
  color: white;
  background: #86A78A;
  padding: 0.2rem 0.55rem;
  border-radius: 20px;
}

/* 금융정보 미입력 유도 */
.recommend-nudge {
  font-size: 0.83rem;
  color: #6a8f6e;
  background: white;
  border-radius: 8px;
  padding: 0.6rem 1rem;
  border: 1px dashed #a8cca9;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}
.nudge-link {
  color: #86A78A;
  font-weight: 600;
  text-decoration: none;
}
.nudge-link:hover { text-decoration: underline; }

/* 가로 스크롤 컨테이너 */
.recommend-scroll {
  display: flex;
  gap: 0.75rem;
  overflow-x: auto;
  padding-bottom: 0.5rem;
  scrollbar-width: thin;
  scrollbar-color: #c8dfc9 transparent;
}
.recommend-scroll::-webkit-scrollbar {
  height: 4px;
}
.recommend-scroll::-webkit-scrollbar-track {
  background: transparent;
}
.recommend-scroll::-webkit-scrollbar-thumb {
  background: #c8dfc9;
  border-radius: 2px;
}

/* 추천 카드 */
.recommend-card {
  flex: 0 0 200px;
  background: white;
  border-radius: 10px;
  padding: 0.85rem;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: transform 0.15s, box-shadow 0.15s;
  border: 1px solid #e8f0e8;
}
.recommend-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0,0,0,0.1);
}

.product-name {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

/* 상품 목록 */
.product-card {
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.15s;
}
.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1) !important;
}
.like-btn:focus {
  box-shadow: none;
}
.nav-link.active {
  color: #86A78A;
  border-bottom-color: #86A78A;
}
</style>
