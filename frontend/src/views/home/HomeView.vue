<template>
  <div class="home-wrapper">

    <!-- 히어로 -->
    <section class="hero-section">
      <div class="hero">
        <div class="hero-left">
          <div class="hero-tag">
            <i class="bi bi-bar-chart-fill me-1"></i>
            금융의 처음부터 끝까지
          </div>
          <h1 class="hero-title">
            모든 금융 신호가<br><em>당신에게</em>
          </h1>
          <p class="hero-desc">
            환율, 금리, 상품, 은행까지.<br>
            필요한 모든 신호를 한 곳에서 받으세요.
          </p>
          <div class="hero-btns">
            <RouterLink to="/signup" class="btn-primary">시작하기</RouterLink>
            <RouterLink to="/currency" class="btn-secondary">더 알아보기</RouterLink>
          </div>
          <div class="hero-stats">
            <div class="stat">
              <div class="stat-val">300+</div>
              <div class="stat-label">예적금 상품</div>
            </div>
            <div class="stat">
              <div class="stat-val">실시간</div>
              <div class="stat-label">인기차트 제공</div>
            </div>
            <div class="stat">
              <div class="stat-val">맞춤</div>
              <div class="stat-label">개인화 추천</div>
            </div>
          </div>
        </div>

        <div class="hero-right">
          <div class="float-card main-card">
            <div v-if="rateLoading" class="loading-text">불러오는 중...</div>
            <template v-else>
              <p class="fc-label">{{ mainRates[0]?.cur_unit }} · {{ mainRates[0]?.cur_nm }} · 오늘 기준</p>
              <p class="fc-val">{{ Number(mainRates[0]?.deal_bas_r).toLocaleString() }} ₩</p>
              <p class="fc-chg" :class="(mainRates[0]?.change || 0) > 0 ? 'up' : 'dn'">
                {{ (mainRates[0]?.change || 0) > 0 ? '▲' : '▼' }} 전일 대비 {{ Math.abs(mainRates[0]?.change || 0).toFixed(2) }}
              </p>
              <div class="mini-chart">
                <div v-for="(h, i) in chartBars" :key="i" class="bar" :class="{ hi: i === chartBars.length - 1 }" :style="{ height: h + '%' }"></div>
              </div>
            </template>
          </div>

          <div class="float-card badge-card">
            <div class="bc-icon"><i class="bi bi-star"></i></div>
            <div class="bc-title">{{ depositProducts[0].name }}</div>
            <div class="bc-sub">{{ depositProducts[0].rate }}% · {{ depositProducts[0].badge }}</div>
          </div>

          <div class="float-card mini-rates">
            <template v-if="!rateLoading">
              <div v-for="item in mainRates.slice(1)" :key="item.cur_unit" class="mr-item">
                <p class="mr-label">{{ item.cur_unit }}</p>
                <p class="mr-val">{{ Number(item.deal_bas_r).toLocaleString() }} ₩</p>
                <p class="mr-chg" :class="(item.change || 0) > 0 ? 'up' : 'dn'">
                  {{ (item.change || 0) > 0 ? '▲' : '▼' }} {{ (item.change || 0) > 0 ? '+' : '' }}{{ (item.change || 0).toFixed(2) }}
                </p>
              </div>
            </template>
          </div>
        </div>
      </div>
    </section>

    <!-- 서비스 소개 -->
    <section class="features-section">
      <div class="inner">
        <div class="feat-head">
          <div class="feat-eyebrow">Our Services</div>
          <h2 class="feat-title">필요한 모든 금융 정보를 한 곳에서</h2>
        </div>
        <div class="feat-grid">
          <div class="feat-card">
            <div class="feat-icon"><i class="bi bi-currency-exchange"></i></div>
            <p class="feat-name">실시간 환율</p>
            <p class="feat-desc">27개국 환율을 실시간으로 확인하고 차트로 추이 분석</p>
            <RouterLink to="/currency" class="feat-link">자세히 보기 →</RouterLink>
          </div>
          <div class="feat-card">
            <div class="feat-icon"><i class="bi bi-map"></i></div>
            <p class="feat-name">주변 은행 찾기</p>
            <p class="feat-desc">지도에서 내 주변 은행을 검색하고 즐겨찾기 관리</p>
            <RouterLink to="/map" class="feat-link">자세히 보기 →</RouterLink>
          </div>
          <div class="feat-card">
            <div class="feat-icon"><i class="bi bi-star"></i></div>
            <p class="feat-name">금융 상품 추천</p>
            <p class="feat-desc">나에게 맞는 예·적금 상품을 비교하고 추천받기</p>
            <RouterLink to="/products" class="feat-link">자세히 보기 →</RouterLink>
          </div>
          <div class="feat-card">
            <div class="feat-icon"><i class="bi bi-play-circle"></i></div>
            <p class="feat-name">금융 영상</p>
            <p class="feat-desc">금융 전문가 유튜브 콘텐츠로 더 깊은 인사이트</p>
            <RouterLink to="/video" class="feat-link">자세히 보기 →</RouterLink>
          </div>
        </div>
      </div>
    </section>

    <!-- 3칸 -->
    <section class="three-section">
      <div class="inner">
        <div class="three-grid">
          <!-- 환율 -->
          <div class="info-col">
            <div class="col-head">
              <p class="col-title">오늘의 주요 환율</p>
              <RouterLink to="/currency" class="col-more">더보기 →</RouterLink>
            </div>
            <div class="carousel-wrap">
              <div v-if="rateLoading" class="loading-text">불러오는 중...</div>
              <transition v-else name="fade" mode="out-in">
                <div :key="rateIdx" class="info-card" @click="$router.push('/currency')">
                  <div class="rank" :class="rateIdx === 0 ? 'gold' : 'green'">{{ rateIdx + 1 }}</div>
                  <div class="cinfo">
                    <p class="csub">{{ mainRates[rateIdx]?.cur_nm }}</p>
                    <p class="cmain">{{ Number(mainRates[rateIdx]?.deal_bas_r).toLocaleString() }} ₩</p>
                    <p class="cdetail" :class="(mainRates[rateIdx]?.change || 0) < 0 ? 'dn' : ''">
                      {{ (mainRates[rateIdx]?.change || 0) > 0 ? '▲' : '▼' }}
                      전일 대비 {{ Math.abs(mainRates[rateIdx]?.change || 0).toFixed(2) }}
                    </p>
                  </div>
                  <span class="badge">{{ mainRates[rateIdx]?.cur_unit }}</span>
                </div>
              </transition>
              <div class="carousel-dots">
                <span v-for="(_, i) in mainRates.slice(0, 3)" :key="i" :class="['dot', { active: rateIdx === i }]" @click="rateIdx = i"></span>
              </div>
            </div>
          </div>

          <!-- 인기 예금 -->
          <div class="info-col">
            <div class="col-head">
              <p class="col-title">인기 예금 상품</p>
              <RouterLink to="/products" class="col-more">더보기 →</RouterLink>
            </div>
            <div class="carousel-wrap">
              <transition name="fade" mode="out-in">
                <div :key="depositIdx" class="info-card">
                  <div class="rank" :class="depositIdx === 0 ? 'gold' : 'green'">{{ depositIdx + 1 }}</div>
                  <div class="cinfo">
                    <p class="csub">{{ depositProducts[depositIdx].bank }}</p>
                    <p class="cmain">{{ depositProducts[depositIdx].name }}</p>
                    <p class="cdetail">{{ depositProducts[depositIdx].rate }}% · {{ depositProducts[depositIdx].period }}</p>
                  </div>
                  <span class="badge">{{ depositProducts[depositIdx].badge }}</span>
                </div>
              </transition>
              <div class="carousel-dots">
                <span v-for="(_, i) in depositProducts" :key="i" :class="['dot', { active: depositIdx === i }]" @click="depositIdx = i"></span>
              </div>
            </div>
          </div>

          <!-- 인기 적금 -->
          <div class="info-col">
            <div class="col-head">
              <p class="col-title">인기 적금 상품</p>
              <RouterLink to="/products" class="col-more">더보기 →</RouterLink>
            </div>
            <div class="carousel-wrap">
              <transition name="fade" mode="out-in">
                <div :key="savingIdx" class="info-card">
                  <div class="rank" :class="savingIdx === 0 ? 'gold' : 'green'">{{ savingIdx + 1 }}</div>
                  <div class="cinfo">
                    <p class="csub">{{ savingProducts[savingIdx].bank }}</p>
                    <p class="cmain">{{ savingProducts[savingIdx].name }}</p>
                    <p class="cdetail">{{ savingProducts[savingIdx].rate }}% · {{ savingProducts[savingIdx].period }}</p>
                  </div>
                  <span class="badge">{{ savingProducts[savingIdx].badge }}</span>
                </div>
              </transition>
              <div class="carousel-dots">
                <span v-for="(_, i) in savingProducts" :key="i" :class="['dot', { active: savingIdx === i }]" @click="savingIdx = i"></span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="cta-section">
      <div class="inner">
        <div class="cta">
          <div>
            <p class="cta-title">지금 바로 시작하세요</p>
            <p class="cta-desc">회원가입 후 나만의 금융 정보를 한눈에 관리하세요</p>
          </div>
          <RouterLink to="/signup" class="cta-btn">무료로 시작하기</RouterLink>
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
const HOME_CURRENCIES = ['USD', 'JPY', 'EUR', 'CNY', 'GBP']
const chartBars = [55, 68, 48, 72, 60, 82, 65, 88, 100]

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
    const order = ['USD', 'JPY', 'EUR', 'CNY', 'GBP']
    const filtered = res.data.filter(item => HOME_CURRENCIES.includes(item.cur_unit))
    mainRates.value = order
      .map(code => filtered.find(item => item.cur_unit === code))
      .filter(Boolean)
      .slice(0, 5)  // USD 1개 + 나머지 4개

    rateTimer = setInterval(() => {
      rateIdx.value = (rateIdx.value + 1) % 3
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
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 56px);
  background: #fff;
}

.inner {
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
  padding: 0 30px;
}

.hero-section {
  background: #fff;
  border-bottom: 0.5px solid #eee;
  position: relative;
  overflow: hidden;
}
.hero-section::before {
  content: '';
  position: absolute;
  top: -100px; right: -100px;
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(160,186,163,0.15) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}
.hero-section::after {
  content: '';
  position: absolute;
  bottom: -75px; left: 30%;
  width: 375px; height: 375px;
  background: radial-gradient(circle, rgba(242,193,93,0.1) 0%, transparent 70%);
  border-radius: 50%;
  pointer-events: none;
}

.hero {
  max-width: 1120px;
  margin: 0 auto;
  width: 100%;
  padding: 65px 30px 55px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 50px;
  align-items: center;
  position: relative;
  z-index: 1;
}
.hero-left { position: relative; z-index: 1; }
.hero-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #F5F1E8;
  border-radius: 20px;
  padding: 6px 15px;
  font-size: 13px;
  color: #6A7F5A;
  font-weight: 600;
  margin-bottom: 24px;
}
.hero-title {
  font-size: 40px;
  font-weight: 800;
  color: #1a1a1a;
  line-height: 1.25;
  margin-bottom: 20px;
  letter-spacing: -0.5px;
}
.hero-title em { color: #6A7F5A; font-style: normal; }
.hero-desc {
  font-size: 15px;
  color: #666;
  line-height: 1.8;
  margin-bottom: 34px;
}
.hero-btns { display: flex; gap: 14px; margin-bottom: 44px; }
.btn-primary {
  padding: 12px 26px;
  border-radius: 8px;
  background: #6A7F5A;
  color: #fff;
  border: none;
  font-size: 14px;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
}
.btn-secondary {
  padding: 12px 26px;
  border-radius: 8px;
  background: #fff;
  color: #3B2F26;
  border: 1.5px solid #e0ddd5;
  font-size: 14px;
  text-decoration: none;
  font-weight: 600;
}
.hero-stats { display: flex; gap: 34px; }
.stat-val { font-size: 22px; font-weight: 800; color: #1a1a1a; }
.stat-label { font-size: 12px; color: #999; margin-top: 2px; }

.hero-right {
  position: relative;
  z-index: 1;
  height: 340px;
}
.float-card {
  position: absolute;
  background: #fff;
  border-radius: 16px;
  border: 0.5px solid #e8e8e8;
  padding: 16px 18px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.07);
}
.main-card {
  top: 0; left: 0; right: 0;
  padding: 20px 22px;
}
.fc-label { font-size: 12px; color: #999; margin-bottom: 5px; }
.fc-val { font-size: 24px; font-weight: 800; color: #1a1a1a; margin-bottom: 3px; }
.fc-chg { font-size: 13px; margin-bottom: 14px; }
.fc-chg.up { color: #4a8a4e; }
.fc-chg.dn { color: #a05050; }
.mini-chart { height: 48px; display: flex; align-items: flex-end; gap: 4px; }
.bar { background: #C5D9C7; border-radius: 2px; flex: 1; }
.bar.hi { background: #6A7F5A; }

.badge-card {
  top: 158px; right: 0;
  width: 170px;
}
.bc-icon {
  width: 32px; height: 32px;
  border-radius: 8px;
  background: #F5F1E8;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 8px;
}
.bc-icon i { color: #6A7F5A; font-size: 16px; }
.bc-title { font-size: 13px; font-weight: 700; color: #1a1a1a; margin-bottom: 3px; }
.bc-sub { font-size: 12px; color: #999; }

/* mini-rates: 2x2 그리드로 4개 표시 */
.mini-rates {
  bottom: 0; left: 0;
  width: 260px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.mr-label { font-size: 12px; color: #999; }
.mr-val { font-size: 14px; font-weight: 700; color: #1a1a1a; }
.mr-chg { font-size: 12px; }
.mr-chg.up { color: #4a8a4e; }
.mr-chg.dn { color: #a05050; }
.loading-text { font-size: 14px; color: #aaa; padding: 20px 0; }

.features-section {
  padding: 44px 0;
  background: #f9f8f5;
  border-top: 0.5px solid #eee;
  border-bottom: 0.5px solid #eee;
}
.feat-head { margin-bottom: 28px; }
.feat-eyebrow {
  font-size: 13px;
  color: #6A7F5A;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 10px;
}
.feat-title { font-size: 22px; font-weight: 800; color: #1a1a1a; letter-spacing: -0.3px; }
.feat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
.feat-card {
  background: #fff;
  padding: 22px;
  border-radius: 14px;
  border: 0.5px solid #eee;
  transition: border-color 0.15s, box-shadow 0.15s;
}
.feat-card:hover {
  border-color: #A0BAA3;
  box-shadow: 0 4px 16px rgba(0,0,0,0.05);
}
.feat-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  background: #F5F1E8;
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 12px;
}
.feat-icon i { color: #6A7F5A; font-size: 20px; }
.feat-name { font-size: 15px; font-weight: 700; color: #1a1a1a; margin-bottom: 6px; }
.feat-desc { font-size: 13px; color: #888; line-height: 1.6; }
.feat-link { font-size: 13px; color: #6A7F5A; font-weight: 600; margin-top: 12px; display: block; text-decoration: none; }

.three-section {
  padding: 40px 0;
  background: #fff;
}
.three-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 24px;
}
.info-col { display: flex; flex-direction: column; gap: 12px; }
.col-head { display: flex; align-items: center; justify-content: space-between; }
.col-title { font-size: 15px; font-weight: 700; color: #1a1a1a; }
.col-more { font-size: 13px; color: #6A7F5A; font-weight: 600; text-decoration: none; }
.carousel-wrap { display: flex; flex-direction: column; gap: 12px; }
.info-card {
  background: #f9f8f5;
  border-radius: 14px;
  border: 0.5px solid #eee;
  padding: 16px 18px;
  display: flex;
  align-items: center;
  gap: 12px;
  height: 90px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.15s;
}
.info-card:hover {
  background: #fff;
  border-color: #6A7F5A;
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.rank { font-size: 17px; font-weight: 800; min-width: 18px; flex-shrink: 0; }
.rank.gold { color: #F2C15D; }
.rank.green { color: #6A7F5A; }
.cinfo { flex: 1; overflow: hidden; }
.csub { font-size: 12px; color: #999; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cmain { font-size: 15px; font-weight: 700; color: #1a1a1a; margin-bottom: 3px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.cdetail { font-size: 12px; color: #6A7F5A; }
.cdetail.dn { color: #a05050; }
.badge {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 20px;
  background: #EAF0EB;
  color: #6A7F5A;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
}
.carousel-dots { display: flex; justify-content: center; gap: 5px; }
.dot { width: 5px; height: 5px; border-radius: 50%; background: #ddd; cursor: pointer; transition: all 0.2s; }
.dot.active { background: #6A7F5A; width: 14px; border-radius: 3px; }

.cta-section { padding: 0 0 44px; background: #fff; }
.cta {
  background: linear-gradient(135deg, #6A7F5A 0%, #86A78A 100%);
  border-radius: 18px;
  padding: 34px 44px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.cta-title { font-size: 22px; font-weight: 800; color: #fff; margin-bottom: 5px; letter-spacing: -0.3px; }
.cta-desc { font-size: 14px; color: rgba(255,255,255,0.75); }
.cta-btn {
  padding: 13px 30px;
  border-radius: 10px;
  background: #fff;
  color: #6A7F5A;
  border: none;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  text-decoration: none;
  white-space: nowrap;
}

.fade-enter-active, .fade-leave-active { transition: opacity 0.4s ease, transform 0.4s ease; }
.fade-enter-from { opacity: 0; transform: translateY(8px); }
.fade-leave-to { opacity: 0; transform: translateY(-8px); }
</style>