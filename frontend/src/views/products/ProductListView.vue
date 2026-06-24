<template>
  <div class="page-outer">
    <div class="page-container">

      <PageHeader title="금융상품 비교" description="예금·적금 상품을 한눈에 비교하고 나에게 맞는 상품을 찾아보세요." class="mb-4" />

      <!-- 추천 섹션 -->
      <div class="recommend-section mb-4">
        <div class="d-flex align-items-center gap-2 mb-3">
          <h6 class="fw-bold mb-0 rec-title">맞춤 추천</h6>
          <span v-if="store.recommendationType === 'personalized'" class="ai-badge">
            <i class="bi bi-stars me-1" />AI 추천
          </span>
        </div>

        <!-- 추천 로딩 -->
        <div v-if="store.isRecommendLoading" class="text-center py-3">
          <div class="spinner-border spinner-border-sm" style="color:#86A78A" role="status" />
        </div>

        <!-- 비로그인 유도 -->
        <div v-else-if="store.recommendationType === 'not_logged_in'" class="nudge-box">
          <i class="bi bi-lightbulb-fill nudge-icon" />
          <span>로그인하면 AI 맞춤 추천을 받을 수 있어요!</span>
          <RouterLink to="/login" class="nudge-link">로그인하기 →</RouterLink>
        </div>

        <!-- 금융정보 미입력 유도 -->
        <div v-else-if="store.recommendationType === 'no_profile'" class="nudge-box">
          <i class="bi bi-lightbulb-fill nudge-icon" />
          <span>금융정보를 입력하면 AI 맞춤 추천을 받을 수 있어요!</span>
          <RouterLink to="/mypage" class="nudge-link">마이페이지에서 설정하기 →</RouterLink>
        </div>

        <!-- 추천 카드 가로 스크롤 -->
        <div v-else-if="store.recommendations.length" class="recommend-scroll">
          <div
            v-for="product in store.recommendations"
            :key="product.id"
            class="rec-card"
            @click="goDetail(product.id)"
          >
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span class="bank-chip">{{ product.kor_co_nm }}</span>
              <button
                :class="['heart-btn', product.liked ? 'liked' : '']"
                @click.stop="onLike(product.id)"
              >
                <i :class="product.liked ? 'bi bi-heart-fill' : 'bi bi-heart'" />
              </button>
            </div>
            <p class="rec-name">{{ product.fin_prdt_nm }}</p>
            <p class="rec-member">{{ product.join_member || '-' }}</p>
            <div class="rec-rate mt-auto">
              <span class="rate-value">{{ product.max_intr_rate2 != null ? product.max_intr_rate2 + '%' : '-' }}</span>
              <span class="rate-label">최고금리</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 툴바 -->
      <div class="toolbar mb-3">
        <div class="tab-group">
          <button :class="['tab-btn', activeTab === 'D' ? 'active' : '']" @click="changeTab('D')">
            정기예금
          </button>
          <button :class="['tab-btn', activeTab === 'S' ? 'active' : '']" @click="changeTab('S')">
            정기적금
          </button>
        </div>

        <div class="toolbar-right">
          <div class="search-wrap">
            <i class="bi bi-search search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              class="search-input"
              placeholder="은행명 또는 상품명"
            />
          </div>

          <div class="sort-wrap">
            <DropdownSelect v-model="sortBy" :options="sortOptions" />
          </div>
        </div>
      </div>

      <!-- 로딩 -->
      <div v-if="store.isLoading" class="text-center py-5">
        <div class="spinner-border" style="color:#86A78A" role="status" />
      </div>

      <!-- 에러 -->
      <div v-else-if="store.error" class="alert alert-danger">
        {{ store.error }}
      </div>

      <!-- 빈 결과 -->
      <div v-else-if="filteredSortedProducts.length === 0" class="empty-state">
        <i class="bi bi-inbox" />
        <p v-if="store.products.length === 0">조건에 맞는 상품이 없습니다.</p>
        <p v-else>검색 조건에 맞는 상품이 없어요.</p>
      </div>

      <!-- 상품 목록: 현재 페이지에 해당하는 상품만 렌더링 -->
      <div v-else class="row g-3">
        <div
          v-for="product in pagedProducts"
          :key="product.id"
          class="col-md-6 col-lg-4"
        >
          <div :class="['product-card', store.isInCompare(product.id) ? 'comparing' : '']" @click="goDetail(product.id)">

            <div class="d-flex justify-content-between align-items-start mb-2">
              <span class="bank-chip">{{ product.kor_co_nm }}</span>
              <button
                :class="['heart-btn', product.liked ? 'liked' : '']"
                @click.stop="onLike(product.id)"
              >
                <i :class="product.liked ? 'bi bi-heart-fill' : 'bi bi-heart'" />
              </button>
            </div>

            <p class="product-name">{{ product.fin_prdt_nm }}</p>

            <div class="product-meta">
              <span>{{ product.join_way || '-' }}</span>
              <span class="meta-dot">·</span>
              <span>{{ product.join_member || '-' }}</span>
            </div>

            <div class="product-rate">
              <span class="rate-value">{{ product.max_intr_rate2 != null ? product.max_intr_rate2 + '%' : '-' }}</span>
              <span class="rate-label">최고금리</span>
            </div>

            <button
              :class="['compare-btn', store.isInCompare(product.id) ? 'active' : '']"
              :disabled="!store.isInCompare(product.id) && store.compareList.length >= 3"
              @click.stop="onCompareToggle(product)"
            >
              <i :class="store.isInCompare(product.id) ? 'bi bi-check2' : 'bi bi-plus'" />
              {{ store.isInCompare(product.id) ? '비교 중' : '비교 추가' }}
            </button>

          </div>
        </div>
      </div>

      <!-- 페이지네이션 -->
      <div v-if="totalPages > 1" class="pagination-wrap">
        <!-- 이전 버튼 -->
        <button class="page-btn" :disabled="currentPage === 1" @click="goPage(currentPage - 1)">
          <i class="bi bi-chevron-left" />
        </button>

        <!-- 페이지 번호 버튼들 -->
        <button
          v-for="p in pageNumbers"
          :key="p"
          :class="['page-btn', { active: p === currentPage, ellipsis: p === '...' }]"
          :disabled="p === '...'"
          @click="p !== '...' && goPage(p)"
        >
          {{ p }}
        </button>

        <!-- 다음 버튼 -->
        <button class="page-btn" :disabled="currentPage === totalPages" @click="goPage(currentPage + 1)">
          <i class="bi bi-chevron-right" />
        </button>
      </div>

    </div>
  </div>

  <CompareBar @open="showCompareModal = true" />
  <CompareModal v-if="showCompareModal" @close="showCompareModal = false" />
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, RouterLink } from 'vue-router'
import { useProductStore } from '@/stores/product'
import { useAuthStore } from '@/stores/auth'
import CompareBar from '@/components/products/CompareBar.vue'
import CompareModal from '@/components/products/CompareModal.vue'
import DropdownSelect from '@/components/common/DropdownSelect.vue'
import PageHeader from '@/components/common/PageHeader.vue'

const router = useRouter()
const store = useProductStore()
const authStore = useAuthStore()

const activeTab = ref('D')
const searchQuery = ref('')
const sortBy = ref('popular')
const sortOptions = [
  { value: 'popular',        label: '인기순' },
  { value: 'rate_desc',      label: '최고금리 높은순' },
  { value: 'base_rate_desc', label: '기본금리 높은순' },
]
const showCompareModal = ref(false)

onMounted(() => {
  store.fetchProducts({ type: activeTab.value })
  store.fetchRecommendations()
})

function changeTab(type) {
  activeTab.value = type
  searchQuery.value = ''
  currentPage.value = 1 // 탭 전환 시 1페이지로 리셋
  store.fetchProducts({ type })
}

// ── 필터·정렬 ─────────────────────────────────────────────
// 검색어·정렬 기준을 클라이언트에서 처리. store.products는 전체 목록을 보유.
const filteredSortedProducts = computed(() => {
  let list = [...store.products]

  // 은행명 또는 상품명으로 부분 일치 검색
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.trim().toLowerCase()
    list = list.filter(p =>
      p.kor_co_nm.toLowerCase().includes(q) || p.fin_prdt_nm.toLowerCase().includes(q)
    )
  }

  // 선택된 정렬 기준 적용 (기본값 'popular'은 서버에서 이미 like_cnt 내림차순 반환)
  if (sortBy.value === 'rate_desc')
    list.sort((a, b) => (b.max_intr_rate2 ?? -Infinity) - (a.max_intr_rate2 ?? -Infinity))
  else if (sortBy.value === 'base_rate_desc')
    list.sort((a, b) => (b.max_intr_rate ?? -Infinity) - (a.max_intr_rate ?? -Infinity))

  return list
})

// ── 페이지네이션 ──────────────────────────────────────────
const PAGE_SIZE = 12 // 한 페이지에 보여줄 상품 수
const currentPage = ref(1)

// 전체 페이지 수
const totalPages = computed(() =>
  Math.ceil(filteredSortedProducts.value.length / PAGE_SIZE)
)

// 현재 페이지에 해당하는 상품 슬라이스
const pagedProducts = computed(() => {
  const start = (currentPage.value - 1) * PAGE_SIZE
  return filteredSortedProducts.value.slice(start, start + PAGE_SIZE)
})

// 검색어·정렬이 바뀌면 1페이지로 리셋
watch([searchQuery, sortBy], () => { currentPage.value = 1 })

// 페이지 이동 + 목록 상단으로 스크롤
function goPage(page) {
  currentPage.value = page
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 표시할 페이지 번호 목록 (최대 7개, 중간 생략 시 '...' 삽입)
// 예: 1 2 3 ... 8 9 10  /  1 ... 4 5 6 ... 10
const pageNumbers = computed(() => {
  const total = totalPages.value
  const cur = currentPage.value
  if (total <= 7) {
    // 페이지가 7개 이하면 전부 표시
    return Array.from({ length: total }, (_, i) => i + 1)
  }
  const pages = []
  if (cur <= 4) {
    // 앞쪽에 있을 때: 1 2 3 4 5 ... last
    pages.push(1, 2, 3, 4, 5, '...', total)
  } else if (cur >= total - 3) {
    // 뒤쪽에 있을 때: 1 ... last-4 last-3 last-2 last-1 last
    pages.push(1, '...', total - 4, total - 3, total - 2, total - 1, total)
  } else {
    // 중간에 있을 때: 1 ... cur-1 cur cur+1 ... last
    pages.push(1, '...', cur - 1, cur, cur + 1, '...', total)
  }
  return pages
})

// ── 라우팅·인터랙션 ───────────────────────────────────────
function goDetail(id) {
  router.push({ name: 'productDetail', params: { id } })
}

async function onLike(productId) {
  // 비로그인 시 로그인 페이지로 이동
  if (!authStore.isLoggedIn) {
    router.push({ name: 'login' })
    return
  }
  await store.likeProduct(productId)
}

function onCompareToggle(product) {
  if (store.isInCompare(product.id)) {
    store.removeFromCompare(product.id)
  } else {
    store.addToCompare(product)
  }
}
</script>

<style scoped>

/* ── 타이틀 ── */
.page-title h2 {
  font-size: 1.6rem;
  font-weight: 700;
  color: #2d2d25;
  margin-bottom: 4px;
}
.page-title p {
  font-size: 0.88rem;
  color: #a0a090;
  margin: 0;
}

/* ── 추천 섹션 ── */
.recommend-section {
  background: #fff;
  border-radius: 16px;
  padding: 20px 22px 18px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.rec-title { color: #2d2d25; font-size: 0.95rem; }
.ai-badge {
  font-size: 0.7rem;
  font-weight: 700;
  color: #fff;
  background: #86A78A;
  padding: 3px 10px;
  border-radius: 20px;
}

/* 유도 박스 */
.nudge-box {
  font-size: 0.83rem;
  color: #6b8a6e;
  background: #f5f8f5;
  border-radius: 10px;
  padding: 10px 16px;
  border: 1.5px dashed #A0BAA3;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.nudge-icon { color: #A0BAA3; }
.nudge-link {
  color: #86A78A;
  font-weight: 600;
  text-decoration: none;
}
.nudge-link:hover { text-decoration: underline; }

/* 추천 가로 스크롤 */
.recommend-scroll {
  display: flex;
  justify-content: center;
  gap: 12px;
  overflow-x: auto;
  padding: 4px 2px 8px;
  scrollbar-width: thin;
  scrollbar-color: #c8d9c9 transparent;
}
.recommend-scroll::-webkit-scrollbar { height: 4px; }
.recommend-scroll::-webkit-scrollbar-thumb {
  background: #c8d9c9;
  border-radius: 2px;
}

/* 추천 카드 */
.rec-card {
  flex: 0 0 210px;
  background: #fafaf6;
  border: 1.5px solid #e4e3d4;
  border-radius: 12px;
  padding: 14px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}
.rec-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(134,167,138,0.15);
  border-color: #A0BAA3;
}
.rec-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: #2d2d25;
  margin: 6px 0 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}
.rec-member {
  font-size: 0.75rem;
  color: #a0a090;
  margin: 0;
}
.rec-rate {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-top: 10px;
}

/* ── 정렬 드롭다운 ── */
.sort-wrap :deep(.ds-trigger) {
  padding: 8px 10px;
  font-size: 0.88rem;
  border-radius: 10px;
  border-color: #d4d3c4;
  white-space: nowrap;
  width: auto;
}
.sort-wrap :deep(.ds-panel) {
  min-width: max-content;
  right: auto;
  white-space: nowrap;
}

/* ── 툴바 ── */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* 탭 */
.tab-group {
  display: flex;
  background: #fff;
  border-radius: 10px;
  padding: 4px;
  box-shadow: 0 1px 6px rgba(0,0,0,0.06);
}
.tab-btn {
  padding: 7px 22px;
  font-size: 0.88rem;
  font-weight: 500;
  border: none;
  border-radius: 8px;
  background: none;
  color: #a0a090;
  cursor: pointer;
  transition: all 0.15s;
}
.tab-btn.active {
  background: #86A78A;
  color: #fff;
  font-weight: 600;
}

/* 검색 */
.search-wrap {
  position: relative;
}
.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #b0b0a0;
  font-size: 0.85rem;
  pointer-events: none;
}
.search-input {
  padding: 8px 14px 8px 34px;
  font-size: 0.88rem;
  border: 1.5px solid #d4d3c4;
  border-radius: 10px;
  background: #fff;
  color: #2d2d25;
  outline: none;
  width: 280px;
  transition: border-color 0.15s;
}
.search-input:focus {
  border-color: #A0BAA3;
}
.search-input::placeholder { color: #c0bfb0; }

/* ── 공통 요소 ── */
.bank-chip {
  font-size: 0.75rem;
  padding: 3px 10px;
  border-radius: 20px;
  background: #ebebeb;
  color: #4a4a4a;
  border: none;
}

.heart-btn {
  background: none;
  border: none;
  padding: 2px 4px;
  font-size: 1rem;
  color: #c8c7b8;
  cursor: pointer;
  line-height: 1;
  transition: color 0.15s;
}
.heart-btn:hover { color: #c0756a; }
.heart-btn.liked { color: #c0756a; }

.rate-value {
  font-size: 1.15rem;
  font-weight: 700;
  color: #5a8a5e;
}
.rate-label {
  font-size: 0.75rem;
  color: #a0a090;
}

/* ── 상품 카드 ── */
.product-card {
  background: #fff;
  border-radius: 14px;
  padding: 18px 20px 32px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1.5px solid transparent;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}
.product-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 20px rgba(134,167,138,0.15);
  border-color: #A0BAA3;
}
.product-card.comparing {
  border-color: #86A78A;
  box-shadow: 0 4px 16px rgba(134,167,138,0.2);
}

.product-name {
  font-size: 0.92rem;
  font-weight: 600;
  color: #2d2d25;
  margin: 8px 0 6px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.45;
}

.product-meta {
  font-size: 0.78rem;
  color: #a0a090;
  display: flex;
  align-items: center;
  gap: 5px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.meta-dot { color: #d4d3c4; }

.product-rate {
  display: flex;
  align-items: baseline;
  gap: 5px;
  justify-content: flex-end;
  margin-top: auto;
}

/* ── 비교 버튼 ── */
.compare-btn {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 6px 0;
  font-size: 0.8rem;
  font-weight: 500;
  border: none;
  border-top: 1.5px solid #e4e3d4;
  border-radius: 0;
  background: rgba(255, 255, 255, 0.96);
  color: #8a8a7a;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  transform: translateY(100%);
  transition: transform 0.2s ease, background 0.15s, color 0.15s;
}
.product-card:hover .compare-btn {
  transform: translateY(0);
}
.compare-btn.active {
  transform: translateY(0);
  background: #eef4ef;
  border-top-color: #A0BAA3;
  color: #4a7a51;
  font-weight: 600;
}
.compare-btn:disabled {
  color: #c8c7b8;
  cursor: not-allowed;
  background: #f7f7f2;
}

/* ── 페이지네이션 ── */
.pagination-wrap {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 6px;
  margin-top: 36px;
}
.page-btn {
  min-width: 36px;
  height: 36px;
  padding: 0 10px;
  border-radius: 8px;
  border: 1.5px solid #e4e3d4;
  background: #fff;
  color: #5a5a4a;
  font-size: 0.88rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.page-btn:hover:not(:disabled):not(.active):not(.ellipsis) {
  border-color: #A0BAA3;
  color: #4a7a51;
}
.page-btn.active {
  background: #86A78A;
  border-color: #86A78A;
  color: #fff;
  font-weight: 700;
  cursor: default;
}
.page-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.page-btn.ellipsis {
  border-color: transparent;
  background: none;
  cursor: default;
  color: #b0b0a0;
}

/* 비교바 있을 때 하단 여백 */
.page-outer {
  padding-bottom: 80px;
}

/* ── 빈 상태 ── */
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #c8c7b8;
}
.empty-state i {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 12px;
}
.empty-state p {
  font-size: 0.9rem;
  margin: 0;
}
</style>
