<template>
  <div class="container py-4">
    <!-- 로딩 -->
    <div v-if="store.isLoading" class="text-center py-5">
      <div class="spinner-border text-success" role="status" />
    </div>

    <!-- 에러 -->
    <div v-else-if="store.error" class="alert alert-danger">
      {{ store.error }}
    </div>

    <template v-else-if="store.product">
      <!-- 헤더 -->
      <div class="d-flex justify-content-between align-items-start mb-4">
        <div>
          <span class="badge bg-secondary mb-2">{{ store.product.kor_co_nm }}</span>
          <h3 class="fw-bold mb-0">{{ store.product.fin_prdt_nm }}</h3>
        </div>

        <!-- 찜하기 버튼 -->
        <button
          class="btn btn-outline-danger d-flex align-items-center gap-1"
          @click="onLike"
        >
          <i :class="store.product.liked ? 'bi bi-heart-fill' : 'bi bi-heart'" />
          <span>{{ store.product.like_count }}</span>
        </button>
      </div>

      <!-- 기본 정보 -->
      <div class="card mb-4 shadow-sm">
        <div class="card-header fw-bold bg-white">기본 정보</div>
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="text-muted small">상품유형</label>
              <p class="mb-0 fw-bold">{{ store.product.product_type === 'D' ? '정기예금' : '정기적금' }}</p>
            </div>
            <div class="col-md-6">
              <label class="text-muted small">가입방법</label>
              <p class="mb-0">{{ store.product.join_way || '-' }}</p>
            </div>
            <div class="col-md-6">
              <label class="text-muted small">가입대상</label>
              <p class="mb-0">{{ store.product.join_member || '-' }}</p>
            </div>
            <div class="col-md-6">
              <label class="text-muted small">가입제한</label>
              <p class="mb-0">{{ joinDenyLabel }}</p>
            </div>
            <div v-if="store.product.max_limit" class="col-md-6">
              <label class="text-muted small">최고한도</label>
              <p class="mb-0">{{ store.product.max_limit.toLocaleString() }}원</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 금리 옵션 테이블 -->
      <div class="card mb-4 shadow-sm">
        <div class="card-header fw-bold bg-white">금리 옵션</div>
        <div class="card-body p-0">
          <table class="table table-hover mb-0">
            <thead class="table-light">
              <tr>
                <th>저축기간</th>
                <th>금리유형</th>
                <th v-if="store.product.product_type === 'S'">적립유형</th>
                <th class="text-center">기본금리</th>
                <th class="text-center text-success">최고금리</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="opt in sortedOptions" :key="opt.id">
                <td>{{ opt.save_trm }}개월</td>
                <td>{{ opt.intr_rate_type_nm || opt.intr_rate_type }}</td>
                <td v-if="store.product.product_type === 'S'">{{ opt.rsrv_type_nm || '-' }}</td>
                <td class="text-center">{{ opt.intr_rate != null ? opt.intr_rate + '%' : '-' }}</td>
                <td class="text-center fw-bold text-success">{{ opt.intr_rate2 != null ? opt.intr_rate2 + '%' : '-' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 우대조건 -->
      <div v-if="store.product.spcl_cnd" class="card mb-4 shadow-sm">
        <div class="card-header fw-bold bg-white">우대조건</div>
        <div class="card-body">
          <p class="mb-0" style="white-space: pre-line;">{{ store.product.spcl_cnd }}</p>
        </div>
      </div>

      <!-- 기타 유의사항 -->
      <div v-if="store.product.etc_note" class="card mb-4 shadow-sm">
        <div class="card-header fw-bold bg-white">기타 유의사항</div>
        <div class="card-body">
          <p class="mb-0" style="white-space: pre-line;">{{ store.product.etc_note }}</p>
        </div>
      </div>

      <!-- 뒤로가기 -->
      <button class="btn btn-outline-secondary" @click="router.back()">
        <i class="bi bi-arrow-left me-1" />목록으로
      </button>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/product'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const store = useProductStore()
const authStore = useAuthStore()

onMounted(() => {
  store.fetchProductDetail(route.params.id)
})

// 저축기간 오름차순 정렬
const sortedOptions = computed(() => {
  if (!store.product?.options) return []
  return [...store.product.options].sort((a, b) => a.save_trm - b.save_trm)
})

// 가입제한 코드 → 한글
const joinDenyLabel = computed(() => {
  const map = { '1': '제한없음', '2': '서민전용', '3': '일부제한' }
  return map[store.product?.join_deny] || '-'
})

async function onLike() {
  if (!authStore.isLoggedIn) {
    router.push({ name: 'login' })
    return
  }
  await store.likeProduct(route.params.id)
}
</script>
