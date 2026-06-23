<template>
  <div class="container py-4">
    <h2 class="fw-bold mb-4">금융상품 비교</h2>

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
import { useRouter } from 'vue-router'
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
