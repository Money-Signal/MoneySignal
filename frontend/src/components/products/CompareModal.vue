<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-box">

      <!-- 헤더 -->
      <div class="modal-head">
        <h5 class="modal-title">
          <i class="bi bi-bar-chart-line me-2" />상품 비교
        </h5>
        <button class="btn-close-modal" @click="$emit('close')">
          <i class="bi bi-x-lg" />
        </button>
      </div>

      <!-- 로딩 -->
      <div v-if="isLoading" class="text-center py-5">
        <div class="spinner-border" style="color:#86A78A" role="status" />
        <p class="mt-3 text-muted small">상품 정보를 불러오는 중...</p>
      </div>

      <!-- 비교 콘텐츠 -->
      <div v-else class="modal-content-scroll">

        <!-- 기본 정보 테이블 -->
        <div class="section-title">기본 정보</div>
        <div class="table-wrap">
          <table class="compare-table">
            <thead>
              <tr>
                <th class="row-label"></th>
                <th v-for="p in details" :key="p.id" class="product-col">
                  <RouterLink
                    :to="{ name: 'productDetail', params: { id: p.id } }"
                    class="product-link"
                    @click="$emit('close')"
                  >
                    <span class="th-bank">{{ p.kor_co_nm }}</span>
                    <span class="th-name">{{ p.fin_prdt_nm }}</span>
                  </RouterLink>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="row-label">상품유형</td>
                <td v-for="p in details" :key="p.id">
                  <span :class="['type-badge', p.product_type === 'D' ? 'type-d' : 'type-s']">
                    {{ p.product_type === 'D' ? '정기예금' : '정기적금' }}
                  </span>
                </td>
              </tr>
              <tr>
                <td class="row-label">최고금리</td>
                <td v-for="p in details" :key="p.id" class="highlight-cell">
                  {{ getMaxRate2(p) != null ? getMaxRate2(p) + '%' : '-' }}
                </td>
              </tr>
              <tr>
                <td class="row-label">기본금리</td>
                <td v-for="p in details" :key="p.id">
                  {{ getMaxRate(p) != null ? getMaxRate(p) + '%' : '-' }}
                </td>
              </tr>
              <tr>
                <td class="row-label">금리유형</td>
                <td v-for="p in details" :key="p.id">
                  <div class="d-flex flex-wrap gap-1">
                    <span
                      v-for="type in getRateTypes(p)"
                      :key="type.code"
                      :class="['rate-type-chip', type.code === 'M' ? 'compound' : '']"
                    >{{ type.name }}</span>
                  </div>
                </td>
              </tr>
              <tr>
                <td class="row-label">가입방법</td>
                <td v-for="p in details" :key="p.id">{{ p.join_way || '-' }}</td>
              </tr>
              <tr>
                <td class="row-label">가입대상</td>
                <td v-for="p in details" :key="p.id">{{ p.join_member || '-' }}</td>
              </tr>
              <tr>
                <td class="row-label">최고한도</td>
                <td v-for="p in details" :key="p.id">
                  {{ p.max_limit ? p.max_limit.toLocaleString() + '원' : '제한없음' }}
                </td>
              </tr>
              <tr>
                <td class="row-label">가입제한</td>
                <td v-for="p in details" :key="p.id">
                  <span v-if="p.join_deny !== '1'" :class="['deny-badge', joinDenyClass(p.join_deny)]">
                    {{ joinDenyLabel(p.join_deny) }}
                  </span>
                  <span v-else>{{ joinDenyLabel(p.join_deny) }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 기간별 금리 차트 (Mixed: 바=기본금리, 라인=최고금리) -->
        <div class="section-title mt-3">기간별 금리 비교</div>
        <div class="chart-meta">
          <div class="chart-products">
            <span v-for="(p, i) in details" :key="p.id" class="product-chip" :style="{ background: hexToRgba(COLORS[i], 0.15), color: COLORS[i] }">
              {{ p.kor_co_nm }}
            </span>
          </div>
          <div class="chart-hint">
            <span class="hint-item"><span class="hint-bar-icon" />막대 = 기본금리</span>
            <span class="hint-item"><span class="hint-line-icon" />라인 = 최고금리</span>
          </div>
        </div>
        <div class="chart-wrap">
          <canvas ref="chartRef" />
        </div>

        <!-- 기간별 금리 상세 -->
        <div class="section-title mt-3">기간별 금리 상세</div>
        <div class="table-wrap">
          <table class="compare-table">
            <thead>
              <tr>
                <th class="row-label">기간</th>
                <th v-for="p in details" :key="p.id" class="product-col">{{ p.kor_co_nm }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="term in allTerms" :key="term">
                <td class="row-label">{{ term }}개월</td>
                <td v-for="p in details" :key="p.id">
                  <template v-if="getTermRate(p, term) != null || getTermRate2(p, term) != null">
                    <div class="term-rate-base">기본 {{ getTermRate(p, term) ?? '-' }}%</div>
                    <div class="term-rate-max">최고 {{ getTermRate2(p, term) ?? '-' }}%</div>
                  </template>
                  <span v-else class="text-muted">-</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 우대조건 -->
        <div class="section-title mt-3">우대조건</div>
        <div class="spcl-list">
          <div v-for="(p, i) in details" :key="p.id" class="spcl-item">
            <div class="spcl-header">
              <span class="spcl-dot" :style="{ background: COLORS[i] }" />
              <span class="spcl-bank-name">{{ p.kor_co_nm }}</span>
              <span class="spcl-prod-name">{{ p.fin_prdt_nm }}</span>
            </div>
            <p v-if="p.spcl_cnd" class="spcl-text">{{ p.spcl_cnd }}</p>
            <p v-else class="spcl-empty">우대조건 정보 없음</p>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { RouterLink } from 'vue-router'
import {
  Chart,
  BarElement, BarController,
  LineElement, LineController, PointElement,
  LinearScale, CategoryScale, Tooltip, Legend, Filler,
} from 'chart.js'
import { getProductDetail } from '@/api/product'
import { useProductStore } from '@/stores/product'

Chart.register(BarElement, BarController, LineElement, LineController, PointElement, LinearScale, CategoryScale, Tooltip, Legend, Filler)

defineEmits(['close'])

const store = useProductStore()
const details = ref([])
const isLoading = ref(true)
const chartRef = ref(null)
let chartInstance = null

const COLORS = ['#86A78A', '#c0756a', '#7a9bc4']

onMounted(async () => {
  const ids = store.compareList.map(p => p.id)
  const results = await Promise.all(ids.map(id => getProductDetail(id).then(r => r.data)))
  details.value = results
  isLoading.value = false
  await nextTick()
  buildChart()
})

onUnmounted(() => {
  if (chartInstance) chartInstance.destroy()
})

const allTerms = computed(() => {
  const set = new Set(details.value.flatMap(p => p.options.map(o => o.save_trm)))
  return [...set].sort((a, b) => a - b)
})

function getMaxRate2(p) {
  const rates = p.options.map(o => o.intr_rate2).filter(r => r != null)
  return rates.length ? Math.max(...rates) : null
}

function getMaxRate(p) {
  const rates = p.options.map(o => o.intr_rate).filter(r => r != null)
  return rates.length ? Math.max(...rates) : null
}

function getTermRate(p, term) {
  const opts = p.options.filter(o => o.save_trm === term)
  const rates = opts.map(o => o.intr_rate).filter(r => r != null)
  return rates.length ? Math.max(...rates) : null
}

function getTermRate2(p, term) {
  const opts = p.options.filter(o => o.save_trm === term)
  const rates = opts.map(o => o.intr_rate2).filter(r => r != null)
  return rates.length ? Math.max(...rates) : null
}

function getRateTypes(p) {
  const seen = new Set()
  return p.options
    .filter(o => { if (seen.has(o.intr_rate_type)) return false; seen.add(o.intr_rate_type); return true })
    .map(o => ({ code: o.intr_rate_type, name: o.intr_rate_type_nm || o.intr_rate_type }))
}

function joinDenyLabel(v) {
  return { '1': '제한없음', '2': '서민전용', '3': '일부제한' }[v] || '-'
}

function joinDenyClass(v) {
  return { '2': 'deny-warn', '3': 'deny-danger' }[v] || ''
}

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${alpha})`
}

function buildChart() {
  if (!chartRef.value || !details.value.length || !allTerms.value.length) return
  if (chartInstance) chartInstance.destroy()

  const labels = allTerms.value.map(t => t + '개월')
  const datasets = []

  details.value.forEach((p, i) => {
    const color = COLORS[i % COLORS.length]
    // 바: 기본금리
    datasets.push({
      type: 'bar',
      label: `${p.kor_co_nm} 기본`,
      data: allTerms.value.map(term => getTermRate(p, term) ?? null),
      backgroundColor: hexToRgba(color, 0.45),
      borderColor: hexToRgba(color, 0.7),
      borderWidth: 1,
      borderRadius: 4,
      maxBarThickness: 40,
      skipNull: true,
    })
    // 라인: 최고금리
    datasets.push({
      type: 'line',
      label: `${p.kor_co_nm} 최고`,
      data: allTerms.value.map(term => getTermRate2(p, term) ?? null),
      borderColor: color,
      backgroundColor: hexToRgba(color, 0.08),
      borderWidth: 2.5,
      pointBackgroundColor: color,
      pointRadius: 5,
      pointHoverRadius: 7,
      tension: 0.3,
      fill: false,
      spanGaps: false,
    })
  })

  chartInstance = new Chart(chartRef.value, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 3,
      categoryPercentage: 0.6,
      barPercentage: 0.8,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y ?? '-'}%`,
          },
        },
      },
      scales: {
        x: { grid: { display: false }, ticks: { font: { size: 12 } } },
        y: {
          grid: { color: '#f0efe8' },
          ticks: { callback: v => v + '%', font: { size: 11 } },
          suggestedMin: 0,
        },
      },
    },
  })
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-box {
  background: #fff;
  border-radius: 18px;
  width: 100%;
  max-width: 860px;
  max-height: 88vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  overflow: hidden;
}

.modal-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 20px 12px;
  border-bottom: 1.5px solid #EBEADD;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1rem;
  font-weight: 700;
  color: #2d2d25;
  margin: 0;
}
.modal-title i { color: #86A78A; }

.btn-close-modal {
  background: none;
  border: none;
  font-size: 1rem;
  color: #a0a090;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  transition: color 0.15s;
}
.btn-close-modal:hover { color: #2d2d25; }

.modal-content-scroll {
  overflow-y: auto;
  padding: 14px 20px 20px;
  flex: 1;
}

.section-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #6b6b5e;
  margin-bottom: 8px;
  padding-bottom: 6px;
  border-bottom: 1.5px solid #EBEADD;
}

/* 테이블 */
.table-wrap { overflow-x: auto; }

.compare-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.87rem;
}

.compare-table th,
.compare-table td {
  padding: 7px 12px;
  border-bottom: 1px solid #f2f1e8;
  vertical-align: middle;
  text-align: left;
}

.compare-table thead tr { border-bottom: 2px solid #EBEADD; }

.row-label {
  font-size: 0.78rem;
  font-weight: 600;
  color: #a0a090;
  white-space: nowrap;
  width: 90px;
  background: #fafaf5;
}

.product-col { min-width: 180px; }

.product-link {
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-decoration: none;
}
.product-link:hover .th-name { color: #86A78A; }

.th-bank { font-size: 0.72rem; color: #a0a090; }
.th-name {
  font-size: 0.85rem;
  font-weight: 700;
  color: #2d2d25;
  transition: color 0.15s;
}

.highlight-cell {
  font-size: 1rem;
  font-weight: 700;
  color: #4a7a51;
}

/* 배지 */
.type-badge {
  font-size: 0.75rem;
  padding: 3px 10px;
  border-radius: 20px;
  font-weight: 500;
}
.type-d { background: #dde8de; color: #4a7a51; }
.type-s { background: #e8e4d4; color: #7a6e3a; }

.deny-badge {
  font-size: 0.75rem;
  padding: 3px 9px;
  border-radius: 20px;
  font-weight: 500;
}
.deny-warn   { background: #f5eccb; color: #8a6d1a; }
.deny-danger { background: #f5ddd9; color: #8a3a30; }

.rate-type-chip {
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 20px;
  background: #f0efea;
  color: #6b6b5e;
}
.rate-type-chip.compound {
  background: #dde8de;
  color: #4a7a51;
}

/* 차트 */
.chart-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.chart-products {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.product-chip {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
}

.chart-hint {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
  color: #a0a090;
}

.hint-item {
  display: flex;
  align-items: center;
  gap: 5px;
}

.hint-bar-icon {
  display: inline-block;
  width: 14px;
  height: 10px;
  background: #c0bfb0;
  border-radius: 2px;
}

.hint-line-icon {
  display: inline-block;
  width: 14px;
  height: 2px;
  background: #c0bfb0;
  position: relative;
}
.hint-line-icon::after {
  content: '';
  position: absolute;
  width: 5px;
  height: 5px;
  background: #c0bfb0;
  border-radius: 50%;
  top: -1.5px;
  left: 50%;
  transform: translateX(-50%);
}

.chart-wrap {
  background: #fafaf5;
  border-radius: 12px;
  padding: 10px 12px;
}

/* 기간별 금리 상세 */
.term-rate-base {
  font-size: 0.78rem;
  color: #a0a090;
}

.term-rate-max {
  font-size: 0.82rem;
  font-weight: 600;
  color: #4a7a51;
}

.spcl-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.spcl-item {
  padding: 10px 12px;
  background: #fafaf5;
  border-radius: 10px;
}

.spcl-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.spcl-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.spcl-bank-name {
  font-size: 0.75rem;
  color: #a0a090;
}

.spcl-prod-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: #2d2d25;
}

.spcl-text {
  font-size: 0.8rem;
  color: #5a5a4a;
  line-height: 1.8;
  white-space: pre-line;
  margin: 0;
  padding-left: 16px;
}

.spcl-empty {
  font-size: 0.8rem;
  color: #c0bfb0;
  margin: 0;
  padding-left: 16px;
}
</style>
