<template>
  <div class="home-wrapper">
    <section class="hero">
      <div class="hero-left">
        <div class="hero-tag">
          <i class="bi bi-bar-chart-fill me-1"></i>
          금융의 처음부터 끝까지, 언제나 당신 곁에
        </div>
        <h1 class="hero-title">
          모든 순간의 금융을<br><em>연결하다</em>
        </h1>
        <p class="hero-desc">
          개인 금융 정보 기반 상품 비교와 추천부터,<br>
          환율 정보 · 금/은 차트, 주변 은행 검색까지.<br>
          필요한 모든 금융 정보를 한 곳에서.
        </p>
        <div class="hero-btns">
          <RouterLink to="/signup" class="btn-primary">시작하기</RouterLink>
          <RouterLink to="/currency" class="btn-secondary">더 알아보기</RouterLink>
        </div>
      </div>
      <div class="hero-right">
        <img src="@/assets/banner.png" alt="MoneySignal 배너" class="hero-banner" />
      </div>
    </section>

    <section class="three-section">
      <!-- 환율 -->
      <div class="info-col">
        <div class="section-header">
          <p class="section-title">오늘의 주요 환율</p>
          <RouterLink to="/currency" class="section-more">더보기 →</RouterLink>
        </div>
        <div class="carousel-wrap">
          <div v-if="rateLoading" class="loading-text">불러오는 중...</div>
          <transition v-else name="fade" mode="out-in">
            <div :key="rateIdx" class="info-card" @click="$router.push('/currency')">
              <div class="product-rank" :class="{ top: rateIdx > 0 }">{{ rateIdx + 1 }}</div>
              <div class="product-info">
                <p class="product-bank">{{ mainRates[rateIdx]?.cur_nm }}</p>
                <p class="product-name">{{ Number(mainRates[rateIdx]?.deal_bas_r).toLocaleString() }} ₩</p>
                <div class="product-rate-row">
                  <span
                    v-if="mainRates[rateIdx]?.change !== null && mainRates[rateIdx]?.change !== undefined"
                    class="rc-change"
                    :class="mainRates[rateIdx]?.change > 0 ? 'up' : mainRates[rateIdx]?.change < 0 ? 'down' : 'flat'"
                  >
                    {{ mainRates[rateIdx]?.change > 0 ? '▲' : mainRates[rateIdx]?.change < 0 ? '▼' : '－' }}
                    전일 대비 {{ Math.abs(mainRates[rateIdx]?.change).toFixed(2) }}
                  </span>
                </div>
              </div>
              <span class="product-badge">{{ mainRates[rateIdx]?.cur_unit }}</span>
            </div>
          </transition>
          <div class="carousel-dots">
            <span
              v-for="(_, i) in mainRates"
              :key="i"
              :class="['dot', { active: rateIdx === i }]"
              @click="rateIdx = i"
            ></span>
          </div>
        </div>
      </div>

      <!-- 인기 예금 -->
      <div class="info-col">
        <div class="section-header">
          <p class="section-title">인기 예금 상품</p>
          <RouterLink to="/products" class="section-more">더보기 →</RouterLink>
        </div>
        <div class="carousel-wrap">
          <transition name="fade" mode="out-in">
            <div :key="depositIdx" class="info-card">
              <div class="product-rank" :class="{ top: depositIdx > 0 }">{{ depositIdx + 1 }}</div>
              <div class="product-info">
                <p class="product-bank">{{ depositProducts[depositIdx].bank }}</p>
                <p class="product-name">{{ depositProducts[depositIdx].name }}</p>
                <div class="product-rate-row">
                  <span class="product-rate">{{ depositProducts[depositIdx].rate }}%</span>
                  <span class="product-period">{{ depositProducts[depositIdx].period }}</span>
                </div>
              </div>
              <span class="product-badge">{{ depositProducts[depositIdx].badge }}</span>
            </div>
          </transition>
          <div class="carousel-dots">
            <span
              v-for="(_, i) in depositProducts"
              :key="i"
              :class="['dot', { active: depositIdx === i }]"
              @click="depositIdx = i"
            ></span>
          </div>
        </div>
      </div>

      <!-- 인기 적금 -->
      <div class="info-col">
        <div class="section-header">
          <p class="section-title">인기 적금 상품</p>
          <RouterLink to="/products" class="section-more">더보기 →</RouterLink>
        </div>
        <div class="carousel-wrap">
          <transition name="fade" mode="out-in">
            <div :key="savingIdx" class="info-card">
              <div class="product-rank" :class="{ top: savingIdx > 0 }">{{ savingIdx + 1 }}</div>
              <div class="product-info">
                <p class="product-bank">{{ savingProducts[savingIdx].bank }}</p>
                <p class="product-name">{{ savingProducts[savingIdx].name }}</p>
                <div class="product-rate-row">
                  <span class="product-rate">{{ savingProducts[savingIdx].rate }}%</span>
                  <span class="product-period">{{ savingProducts[savingIdx].period }}</span>
                </div>
              </div>
              <span class="product-badge">{{ savingProducts[savingIdx].badge }}</span>
            </div>
          </transition>
          <div class="carousel-dots">
            <span
              v-for="(_, i) in savingProducts"
              :key="i"
              :class="['dot', { active: savingIdx === i }]"
              @click="savingIdx = i"
            ></span>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { fetchLatestRates } from '@/api/currency'

const rateLoading = ref(true)
const mainRates = ref([])
const HOME_CURRENCIES = ['USD', 'EUR', 'JPY', 'CNY', 'CNH']

const rateIdx = ref(0)
const depositIdx = ref(0)
const savingIdx = ref(0)
let rateTimer = null
let depositTimer = null
let savingTimer = null

const depositProducts = [
  { bank: 'KB국민은행', name: 'KB Star 정기예금', rate: '3.85', period: '12개월 기준', badge: '최고금리' },
  { bank: '신한은행', name: '쏠편한 정기예금', rate: '3.75', period: '12개월 기준', badge: '인기' },
  { bank: '하나은행', name: '하나의 정기예금', rate: '3.70', period: '12개월 기준', badge: '온라인' },
]

const savingProducts = [
  { bank: '우리은행', name: '우리 SUPER 주거래 적금', rate: '4.20', period: '12개월 기준', badge: '최고금리' },
  { bank: '카카오뱅크', name: '카카오뱅크 자유적금', rate: '4.00', period: '12개월 기준', badge: '인기' },
  { bank: '토스뱅크', name: '키워봐요 적금', rate: '3.90', period: '12개월 기준', badge: '온라인' },
]

onMounted(async () => {
  try {
    const res = await fetchLatestRates()
    const filtered = res.data.filter(item => HOME_CURRENCIES.includes(item.cur_unit))
    const order = ['USD', 'JPY', 'EUR', 'CNY', 'CNH']
    mainRates.value = order
      .map(code => filtered.find(item => item.cur_unit === code))
      .filter(Boolean)
      .slice(0, 3)

    rateTimer = setInterval(() => {
      rateIdx.value = (rateIdx.value + 1) % mainRates.value.length
    }, 3000)
  } catch (e) {
    console.error('환율 로드 실패:', e)
  } finally {
    rateLoading.value = false
  }

  depositTimer = setInterval(() => {
    depositIdx.value = (depositIdx.value + 1) % depositProducts.length
  }, 3000)
  savingTimer = setInterval(() => {
    savingIdx.value = (savingIdx.value + 1) % savingProducts.length
  }, 3000)
})

onBeforeUnmount(() => {
  clearInterval(rateTimer)
  clearInterval(depositTimer)
  clearInterval(savingTimer)
})
</script>

<style scoped>
.home-wrapper {
  padding: 40px 48px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  min-height: calc(100vh - 56px);
}

.hero {
  display: grid;
  grid-template-columns: 2fr 3fr;
  gap: 48px;
  align-items: center;
  min-height: 55vh;
}
.hero-left {
  display: flex;
  flex-direction: column;
  justify-content: center;
  margin: auto;
  max-width: 380px;
}
.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #fff;
  border: 1px solid #ddd9cc;
  border-radius: 20px;
  padding: 5px 12px;
  font-size: 12px;
  color: #6A7F5A;
  margin-bottom: 18px;
  width: fit-content;
}
.hero-title {
  font-size: 42px;
  font-weight: 700;
  color: #3B2F26;
  line-height: 1.35;
  margin-bottom: 14px;
}
.hero-title em { color: #6A7F5A; font-style: normal; }
.hero-desc {
  font-size: 16px;
  color: #7a7060;
  line-height: 1.9;
  margin-bottom: 26px;
}
.hero-btns { display: flex; gap: 10px; }
.btn-primary {
  padding: 10px 24px;
  border-radius: 8px;
  background: #6A7F5A;
  color: #fff;
  border: none;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
}
.btn-secondary {
  padding: 10px 24px;
  border-radius: 8px;
  background: transparent;
  color: #6A7F5A;
  border: 1.5px solid #6A7F5A;
  font-size: 14px;
  text-decoration: none;
}
.hero-right {
  display: flex;
  justify-content: center;
  align-items: center;
}
.hero-banner {
  width: 100%;
  height: auto;
  border-radius: 16px;
  object-fit: contain;
  border: none;
}

/* 3칸 섹션 */
.three-section {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 20px;
}
.info-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.section-title {
  font-size: 15px;
  font-weight: 600;
  color: #3B2F26;
}
.section-more {
  font-size: 12px;
  color: #6A7F5A;
  text-decoration: none;
}
.loading-text {
  font-size: 13px;
  color: #aaa;
  padding: 20px 0;
}
.carousel-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 공통 카드 */
.info-card {
  background: #fff;
  border-radius: 10px;
  border: 0.5px solid #ddd9cc;
  padding: 14px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  height: 90px;
  cursor: pointer;
  transition: border-color 0.15s;
  overflow: hidden;
}
.info-card:hover { border-color: #6A7F5A; }

/* 공통 상품/환율 카드 내부 */
.product-rank {
  font-size: 16px;
  font-weight: 700;
  color: #F2C15D;
  min-width: 20px;
  flex-shrink: 0;
}
.product-rank.top { color: #6A7F5A; }
.product-info {
  flex: 1;
  overflow: hidden;
}
.product-bank {
  font-size: 11px;
  color: #888;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.product-name {
  font-size: 13px;
  font-weight: 600;
  color: #3B2F26;
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.product-rate-row {
  display: flex;
  align-items: center;
  gap: 6px;
}
.product-rate {
  font-size: 15px;
  font-weight: 700;
  color: #6A7F5A;
}
.product-period {
  font-size: 11px;
  color: #aaa;
}
.product-badge {
  font-size: 10px;
  padding: 3px 8px;
  border-radius: 20px;
  background: #F5F1E8;
  color: #6A7F5A;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

/* 환율 전일 대비 */
.rc-change {
  font-size: 11px;
  font-weight: 500;
}
.rc-change.up { color: #4a8a4e; }
.rc-change.down { color: #a05050; }
.rc-change.flat { color: #aaa; }

/* 도트 */
.carousel-dots {
  display: flex;
  justify-content: center;
  gap: 6px;
  padding: 4px 0;
}
.dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #ddd9cc;
  cursor: pointer;
  transition: all 0.2s;
}
.dot.active {
  background: #6A7F5A;
  width: 18px;
  border-radius: 3px;
}

/* 트랜지션 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>