<template>
  <div class="page-wrap">
    <div class="container py-4">

      <!-- 로딩 -->
      <LoadingSpinner v-if="store.isLoading" />

      <!-- 에러 -->
      <div v-else-if="store.error" class="alert alert-danger">
        {{ store.error }}
      </div>

      <template v-else-if="store.product">

        <!-- 뒤로가기 -->
        <button class="btn-back mb-3" @click="router.back()">
          <i class="bi bi-arrow-left me-1" />목록으로
        </button>

        <!-- 헤더 -->
        <div class="hero-card mb-4">
          <div class="d-flex justify-content-between align-items-center gap-3 flex-wrap">
            <div class="hero-left">
              <div class="d-flex align-items-center gap-2 mb-2 flex-wrap">
                <span :class="['type-badge', store.product.product_type === 'D' ? 'type-deposit' : 'type-saving']">
                  {{ store.product.product_type === 'D' ? '정기예금' : '정기적금' }}
                </span>
              </div>
              <h2 class="product-title">{{ store.product.fin_prdt_nm }}</h2>
              <div class="d-flex align-items-center gap-3 flex-wrap mt-2">
                <span class="meta-text">
                  <i class="bi bi-calendar3 me-1" />{{ formatMonth(store.product.dcls_month) }} 공시
                </span>
                <span :class="['deny-badge', joinDenyBadgeClass]">
                  <i class="bi bi-shield-check me-1" />{{ joinDenyLabel }}
                </span>
              </div>
            </div>

            <!-- 오른쪽: 은행명 + 지도 버튼 + 하트 -->
            <div class="hero-right">
              <div class="bank-action-group">
                <span class="bank-name">{{ store.product.kor_co_nm }}</span>
                <button class="map-link-btn" @click="goToMap(store.product.kor_co_nm)">
                  <i class="bi bi-geo-alt-fill me-1" />지도에서 찾기
                </button>
              </div>
              <button :class="['like-btn', store.product.liked ? 'liked' : '']" @click="onLike">
                <i :class="store.product.liked ? 'bi bi-heart-fill' : 'bi bi-heart'" />
                <span>{{ store.product.like_count }}</span>
              </button>
            </div>

          </div>
        </div>

        <!-- 카드 목록 -->
        <div class="row g-4 align-items-start">

          <!-- 왼쪽: 기본 정보 + 우대조건 + 유의사항 -->
          <div class="col-lg-5 d-flex flex-column gap-4">

            <!-- 기본 정보 -->
            <div class="info-card">
              <div class="card-section-title">
                <i class="bi bi-info-circle" />기본 정보
              </div>
              <div class="d-flex flex-column gap-3 pt-1">

                <div>
                  <p class="field-label">가입방법</p>
                  <div class="d-flex flex-wrap gap-1">
                    <span v-for="way in joinWays" :key="way" class="chip">{{ way }}</span>
                  </div>
                </div>

                <div>
                  <p class="field-label">가입대상</p>
                  <p class="field-value">{{ store.product.join_member || '-' }}</p>
                </div>

                <div v-if="store.product.max_limit">
                  <p class="field-label">최고한도</p>
                  <p class="field-value accent-text">{{ store.product.max_limit.toLocaleString() }}원</p>
                </div>

                <div v-if="store.product.mtrt_int">
                  <p class="field-label">만기 후 이자율</p>
                  <p class="field-value">{{ store.product.mtrt_int }}</p>
                </div>

                <div>
                  <p class="field-label">공시기간</p>
                  <p class="field-value">
                    {{ formatDay(store.product.dcls_strt_day) }} ~
                    <span v-if="store.product.dcls_end_day" :class="isExpired ? 'text-danger' : 'end-valid'">
                      {{ formatDay(store.product.dcls_end_day) }}
                      <span class="small ms-1">{{ isExpired ? '(마감)' : '(가입 가능)' }}</span>
                    </span>
                    <span v-else class="end-valid">판매 기간 제한 없음</span>
                  </p>
                </div>

              </div>
            </div>

            <!-- 우대조건 -->
            <div v-if="store.product.spcl_cnd" class="info-card">
              <div class="card-section-title">
                <i class="bi bi-star" />우대조건
              </div>
              <p class="condition-text">{{ store.product.spcl_cnd }}</p>
            </div>

            <!-- 유의사항 -->
            <div v-if="store.product.etc_note" class="info-card">
              <div class="card-section-title">
                <i class="bi bi-exclamation-circle" />유의사항
              </div>
              <p class="condition-text">{{ store.product.etc_note }}</p>
            </div>

          </div>

          <!-- 오른쪽: 금리 옵션 -->
          <div class="col-lg-7">
            <div class="info-card">
              <div class="card-section-title">
                <i class="bi bi-graph-up-arrow" />금리 옵션
                <button class="calc-btn ms-auto" @click="showCalcModal = true">
                  <i class="bi bi-calculator me-1" />수익 계산기
                </button>
              </div>
              <RateChart :product="store.product" class="mt-3" />
              <div class="table-responsive mt-2">
                <table class="rate-table w-100">
                  <thead>
                    <tr>
                      <th>저축기간</th>
                      <th>금리유형</th>
                      <th v-if="store.product.product_type === 'S'">적립유형</th>
                      <th class="text-center">기본금리</th>
                      <th class="text-center">최고금리</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="opt in sortedOptions" :key="opt.id">
                      <td class="fw-semibold">{{ opt.save_trm }}개월</td>
                      <td>
                        <span class="tag tag-gray">{{ opt.intr_rate_type_nm || opt.intr_rate_type }}</span>
                      </td>
                      <td v-if="store.product.product_type === 'S'">
                        <span v-if="opt.rsrv_type_nm" :class="['tag', opt.rsrv_type === 'S' ? 'tag-green' : 'tag-warm']">
                          {{ opt.rsrv_type_nm }}
                        </span>
                        <span v-else class="text-muted">-</span>
                      </td>
                      <td class="text-center muted-rate">{{ opt.intr_rate != null ? opt.intr_rate + '%' : '-' }}</td>
                      <td class="text-center best-rate">{{ opt.intr_rate2 != null ? opt.intr_rate2 + '%' : '-' }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>

        </div>

        <!-- 관련 커뮤니티 글 -->
        <div class="info-card mt-4">
          <div class="card-section-title">
            <i class="bi bi-chat-square-text" />관련 커뮤니티 글
            <RouterLink
              :to="{ name: 'communityList' }"
              class="more-link ms-auto"
            >
              커뮤니티 바로가기 →
            </RouterLink>
          </div>

          <!-- 로딩 -->
          <LoadingSpinner v-if="relatedLoading" />

          <!-- 결과 없음 -->
          <div v-else-if="relatedPosts.length === 0" class="related-empty">
            <i class="bi bi-pencil-square" />
            <p>{{ store.product.kor_co_nm }} 관련 글이 아직 없어요.</p>
            <RouterLink :to="{ name: 'communityWrite' }" class="write-link">
              첫 번째 글 작성하기 →
            </RouterLink>
          </div>

          <!-- 글 목록 -->
          <ul v-else class="related-list">
            <li
              v-for="post in relatedPosts"
              :key="post.id"
              class="related-item"
              @click="router.push({ name: 'communityDetail', params: { id: post.id } })"
            >
              <div class="related-top">
                <span class="related-category">{{ post.category === 'DEPOSIT' ? '예금·적금' : post.category }}</span>
                <span class="related-date">{{ formatPostDate(post.created_at) }}</span>
              </div>
              <p class="related-title">{{ post.title }}</p>
              <p class="related-preview">{{ post.content }}</p>
              <div class="related-meta">
                <span><i class="bi bi-person me-1" />{{ post.author_nickname }}</span>
                <span><i class="bi bi-heart me-1" />{{ post.like_count }}</span>
                <span><i class="bi bi-chat me-1" />{{ post.comment_count }}</span>
              </div>
            </li>
          </ul>
        </div>

      </template>
    </div>
  </div>

  <!-- 수익 계산기 모달 -->
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="showCalcModal" class="calc-modal-overlay" @click.self="showCalcModal = false">
        <div class="calc-modal-box">
          <div class="calc-modal-head">
            <span class="calc-modal-title"><i class="bi bi-calculator me-2" />수익 계산기</span>
            <button class="btn-close-calc" @click="showCalcModal = false"><i class="bi bi-x-lg" /></button>
          </div>
          <div class="calc-modal-body">
            <YieldCalculator :product="store.product" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/product'
import { useAuthStore } from '@/stores/auth'
import { searchPosts } from '@/api/community'
import YieldCalculator from '@/components/products/YieldCalculator.vue'
import RateChart from '@/components/products/RateChart.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const route = useRoute()
const router = useRouter()
const store = useProductStore()
const authStore = useAuthStore()
const showCalcModal = ref(false)

// ── 관련 커뮤니티 글 ──────────────────────────────────────
const relatedPosts = ref([])
const relatedLoading = ref(false)

// 날짜 포맷: "2024-05-01T..." → "2024.05.01"
function formatPostDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.slice(0, 10).replace(/-/g, '.')
}

// 은행명 + 상품명 두 키워드로 각각 검색 후 중복 제거해서 최대 5개 반환
async function fetchRelatedPosts(bankName, productName) {
  relatedLoading.value = true
  try {
    // 두 검색을 병렬로 요청
    const [bankRes, productRes] = await Promise.all([
      searchPosts(bankName, 5),
      searchPosts(productName, 5),
    ])

    // id 기준으로 중복 제거 후 최대 5개만 사용
    const seen = new Set()
    const merged = []
    for (const post of [...bankRes.data, ...productRes.data]) {
      if (!seen.has(post.id)) {
        seen.add(post.id)
        merged.push(post)
      }
    }
    relatedPosts.value = merged.slice(0, 5)
  } catch (e) {
    relatedPosts.value = []
  } finally {
    relatedLoading.value = false
  }
}

onMounted(async () => {
  await store.fetchProductDetail(Number(route.params.id))
  if (store.product) {
    fetchRelatedPosts(store.product.kor_co_nm, store.product.fin_prdt_nm)
  }
})

const sortedOptions = computed(() => {
  if (!store.product?.options) return []
  return [...store.product.options].sort((a, b) => {
    if (a.save_trm !== b.save_trm) return a.save_trm - b.save_trm
    return a.rsrv_type.localeCompare(b.rsrv_type)
  })
})

const joinDenyLabel = computed(() => {
  const map = { '1': '제한없음', '2': '서민전용', '3': '일부제한' }
  return map[store.product?.join_deny] || '-'
})

const joinDenyBadgeClass = computed(() => {
  const map = { '2': 'deny-warn', '3': 'deny-danger' }
  return map[store.product?.join_deny] || 'deny-ok'
})

const joinWays = computed(() => {
  if (!store.product?.join_way) return []
  return store.product.join_way.split(',').map(s => s.trim()).filter(Boolean)
})

const isExpired = computed(() => {
  const end = store.product?.dcls_end_day
  if (!end) return false
  const today = new Date().toISOString().slice(0, 10).replace(/-/g, '')
  return end < today
})

function formatMonth(v) {
  if (!v || v.length !== 6) return v || '-'
  return `${v.slice(0, 4)}년 ${v.slice(4)}월`
}

function formatDay(v) {
  if (!v || v.length !== 8) return v || '-'
  return `${v.slice(0, 4)}.${v.slice(4, 6)}.${v.slice(6)}`
}

async function onLike() {
  if (!authStore.isLoggedIn) {
    router.push({ name: 'login' })
    return
  }
  await store.likeProduct(Number(route.params.id))
}

function goToMap(bankName) {
  router.push({ name: 'map', query: { bank: bankName } })
}
</script>

<style scoped>
/* ── 페이지 배경 ── */
.page-wrap {
  min-height: 100vh;
  background-color: #f9f8f5;
}

/* ── 히어로 오른쪽 영역 ── */
.hero-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.bank-action-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.bank-name {
  font-size: 1.15rem;
  font-weight: 700;
  color: #2d2d25;
  letter-spacing: -0.01em;
  border-bottom: 2px solid #86A78A;
  padding-bottom: 2px;
}

.map-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 14px;
  font-size: 0.78rem;
  font-weight: 600;
  border: 1.5px solid #A0BAA3;
  border-radius: 20px;
  background: #fff;
  color: #6A7F5A;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
}
.map-link-btn:hover {
  background: #f0f4f0;
  border-color: #6A7F5A;
}

/* ── 수익 계산 버튼 ── */
.calc-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 5px 14px;
  font-size: 0.8rem;
  font-weight: 600;
  border: none;
  border-radius: 20px;
  background: #86A78A;
  color: #fff;
  cursor: pointer;
  letter-spacing: 0.01em;
  box-shadow: 0 2px 6px rgba(134,167,138,0.35);
  transition: background 0.15s, box-shadow 0.15s;
  white-space: nowrap;
}
.calc-btn:hover {
  background: #6a9170;
  box-shadow: 0 3px 10px rgba(134,167,138,0.45);
}

/* ── 계산기 모달 ── */
.calc-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.calc-modal-box {
  background: #fff;
  border-radius: 18px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,0.18);
  overflow: hidden;
}
.calc-modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px 12px;
  border-bottom: 1.5px solid #EBEADD;
  flex-shrink: 0;
}
.calc-modal-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #2d2d25;
}
.calc-modal-title i { color: #86A78A; }
.btn-close-calc {
  background: none;
  border: none;
  font-size: 1rem;
  color: #a0a090;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: color 0.15s;
}
.btn-close-calc:hover { color: #2d2d25; }
.calc-modal-body {
  overflow-y: auto;
  flex: 1;
}
.calc-modal-body :deep(.calc-header) {
  display: none;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ── 뒤로가기 ── */
.btn-back {
  background: none;
  border: 1.5px solid #c8c7b6;
  border-radius: 8px;
  padding: 5px 14px;
  font-size: 0.85rem;
  color: #6b6b5e;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-back:hover {
  border-color: #86A78A;
  color: #86A78A;
}

/* ── 히어로 카드 ── */
.hero-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px 28px;
  box-shadow: 0 2px 12px rgba(134,167,138,0.10);
  border-left: 5px solid #86A78A;
}

.type-badge {
  font-size: 0.78rem;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 20px;
  letter-spacing: 0.02em;
}
.type-deposit { background: #dde8de; color: #4a7a51; }
.type-saving  { background: #e8e4d4; color: #7a6e3a; }

.product-title {
  font-size: 1.4rem;
  font-weight: 700;
  color: #2d2d25;
  margin: 0;
  line-height: 1.4;
}
.meta-text {
  font-size: 0.8rem;
  color: #a0a090;
}

.deny-badge {
  font-size: 0.75rem;
  padding: 3px 10px;
  border-radius: 20px;
  font-weight: 500;
}
.deny-ok      { background: #dde8de; color: #4a7a51; }
.deny-warn    { background: #f5eccb; color: #8a6d1a; }
.deny-danger  { background: #f5ddd9; color: #8a3a30; }

/* 찜 버튼 */
.like-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  border: 2px solid #d8d7c8;
  border-radius: 12px;
  padding: 10px 18px;
  font-size: 0.8rem;
  color: #a0a090;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  min-width: 58px;
}
.like-btn i { font-size: 1.3rem; }
.like-btn:hover  { border-color: #c0756a; color: #c0756a; }
.like-btn.liked  { border-color: #c0756a; color: #c0756a; background: #fdf3f1; }

/* ── 정보 카드 공통 ── */
.info-card {
  background: #fff;
  border-radius: 14px;
  padding: 20px 24px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.card-section-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #3d3d30;
  display: flex;
  align-items: center;
  gap: 7px;
  padding-bottom: 12px;
  border-bottom: 1.5px solid #EBEADD;
  margin-bottom: 4px;
}
.card-section-title > i { color: #86A78A; font-size: 1rem; }
.calc-btn i { color: #fff; }

/* 필드 */
.field-label {
  font-size: 0.75rem;
  color: #a0a090;
  margin-bottom: 4px;
}
.field-value {
  font-size: 0.92rem;
  color: #2d2d25;
  margin: 0;
}
.accent-text { color: #5a8a5e; font-weight: 600; }
.end-valid   { color: #5a8a5e; }

/* 칩 */
.chip {
  font-size: 0.78rem;
  padding: 3px 10px;
  border-radius: 20px;
  background: #f9f8f5;
  color: #5a5a4a;
  border: 1px solid #d4d3c4;
}

/* ── 금리 테이블 ── */
.rate-table {
  border-collapse: collapse;
  font-size: 0.88rem;
}
.rate-table th {
  font-size: 0.78rem;
  font-weight: 600;
  color: #a0a090;
  padding: 8px 12px;
  border-bottom: 1.5px solid #EBEADD;
}
.rate-table td {
  padding: 10px 12px;
  color: #2d2d25;
  border-bottom: 1px solid #f2f1e8;
  vertical-align: middle;
}
.rate-table tbody tr:last-child td { border-bottom: none; }
.rate-table tbody tr:hover td { background: #fafaf5; }

.tag {
  font-size: 0.75rem;
  padding: 2px 9px;
  border-radius: 20px;
  font-weight: 500;
}
.tag-gray  { background: #f0efea; color: #6b6b5e; }
.tag-green { background: #dde8de; color: #4a7a51; }
.tag-warm  { background: #f5eccb; color: #7a6232; }

.muted-rate { color: #b0b0a0; font-size: 0.85rem; }
.best-rate  { color: #5a8a5e; font-weight: 700; font-size: 0.95rem; }

/* ── 관련 커뮤니티 글 ── */
.more-link {
  font-size: 0.78rem;
  color: #86A78A;
  font-weight: 600;
  text-decoration: none;
}
.more-link:hover { text-decoration: underline; }

.related-empty {
  text-align: center;
  padding: 28px 0 20px;
  color: #c0bfb0;
}
.related-empty i {
  font-size: 1.8rem;
  display: block;
  margin-bottom: 8px;
}
.related-empty p { font-size: 0.88rem; margin: 0 0 10px; }
.write-link {
  font-size: 0.82rem;
  color: #86A78A;
  font-weight: 600;
  text-decoration: none;
}
.write-link:hover { text-decoration: underline; }

.related-list {
  list-style: none;
  padding: 0;
  margin: 8px 0 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.related-item {
  padding: 14px 4px;
  border-bottom: 1px solid #f2f1e8;
  cursor: pointer;
  border-radius: 8px;
  transition: background 0.12s;
}
.related-item:last-child { border-bottom: none; }
.related-item:hover { background: #fafaf5; padding-left: 8px; }

.related-top {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 5px;
}
.related-category {
  font-size: 0.72rem;
  font-weight: 600;
  color: #6A7F5A;
  background: #eaf0eb;
  padding: 2px 8px;
  border-radius: 20px;
}
.related-date {
  font-size: 0.75rem;
  color: #b0b0a0;
  margin-left: auto;
}
.related-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2d2d25;
  margin: 0 0 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.related-preview {
  font-size: 0.8rem;
  color: #8a8a7a;
  margin: 0 0 8px;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.related-meta {
  display: flex;
  gap: 14px;
  font-size: 0.75rem;
  color: #b0b0a0;
}

/* 우대조건 / 유의사항 */
.condition-text {
  font-size: 0.88rem;
  color: #5a5a4a;
  white-space: pre-line;
  line-height: 1.8;
  margin: 12px 0 0;
}
</style>