<template>
  <div class="chart-card">
    <!-- 통화 미선택 시 -->
    <div v-if="!selectedCode" class="empty-state">
      <i class="bi bi-bar-chart-line me-2"></i>통화를 선택하면 차트가 표시됩니다
    </div>

    <!-- 통화 선택 후 -->
    <div v-else class="chart-inner">
      <p class="card-label mb-3">
        <i class="bi bi-graph-up me-1"></i>환율 추이
      </p>

      <!-- 빠른 필터 버튼 -->
      <div class="filter-row mb-3">
        <button
          v-for="f in filters"
          :key="f.days"
          :class="['filter-btn', { active: selectedDays === f.days && !isCustomMode }]"
          @click="changeFilter(f.days)"
        >
          {{ f.label }}
        </button>
      </div>

      <LoadingSpinner v-if="loading" />
      <!-- 날짜 직접 설정 (항상 표시) -->
      <div class="custom-date-row mb-3">
        <div class="date-input-wrap">
          <label>시작일</label>
          <VueDatePicker
            v-model="customStart"
            :enable-time-picker="false"
            :max-date="customEnd || today"
            locale="ko"
            format="yyyy-MM-dd"
            placeholder="시작일 선택"
            auto-apply
            :clearable="false"
            class="custom-dp"
          />
        </div>
        <span class="date-separator">~</span>
        <div class="date-input-wrap">
          <label>종료일</label>
          <VueDatePicker
            v-model="customEnd"
            :enable-time-picker="false"
            :min-date="customStart"
            :max-date="today"
            locale="ko"
            format="yyyy-MM-dd"
            placeholder="종료일 선택"
            auto-apply
            :clearable="false"
            class="custom-dp"
          />
        </div>
        <button class="date-search-btn" @click="loadCustomChart" :disabled="!customStart || !customEnd">
          <i class="bi bi-search me-1"></i>조회
        </button>
      </div>

      <div v-if="loading" class="chart-loading">
        <div class="spinner-border spinner-border-sm text-secondary me-2"></div>
        신호를 찾는 중...
      </div>

      <div v-if="error" class="alert-error mb-2">
        <i class="bi bi-exclamation-circle me-1"></i>{{ error }}
      </div>

      <div v-if="!loading && !error" class="canvas-wrap">
        <canvas ref="chartCanvas"></canvas>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue'
import {
  Chart, LineElement, PointElement, LinearScale,
  CategoryScale, LineController, Tooltip, Legend, Filler, Title
} from 'chart.js'
import { fetchChartData } from '@/api/currency'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
// 수정
import VueDatePicker from '@vuepic/vue-datepicker'
import '@vuepic/vue-datepicker/dist/main.css'

Chart.register(LineElement, PointElement, LinearScale, CategoryScale, LineController, Tooltip, Legend, Filler, Title)

const props = defineProps({
  selectedCode: { type: String, default: '' }
})

const chartCanvas = ref(null)
const loading = ref(false)
const error = ref('')
const selectedDays = ref(null)
const isCustomMode = ref(false)
const customStart = ref(null)
const customEnd = ref(null)
let chartInstance = null

const today = computed(() => new Date())

const filters = [
  { label: '7일', days: 7 },
  { label: '15일', days: 15 },
  { label: '1달', days: 30 },
  { label: '2달', days: 60 },
  { label: '3달', days: 90 },
]

const renderChart = (labels, data) => {
  if (!chartCanvas.value) return
  if (chartInstance) chartInstance.destroy()

  const ctx = chartCanvas.value.getContext('2d')
  const gradient = ctx.createLinearGradient(0, 0, 0, chartCanvas.value.clientHeight || 400)
  gradient.addColorStop(0, 'rgba(134, 167, 138, 0.45)')
  gradient.addColorStop(0.6, 'rgba(134, 167, 138, 0.08)')
  gradient.addColorStop(1, 'rgba(134, 167, 138, 0.0)')

  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: `${props.selectedCode} → KRW`,
        data,
        borderColor: '#6a9e6e',
        backgroundColor: gradient,
        fill: true,
        tension: 0.35,
        pointRadius: 0,
        pointHoverRadius: 6,
        pointHoverBackgroundColor: '#6a9e6e',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2.5,
        borderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: 'rgba(26, 42, 28, 0.95)',
          titleColor: '#a0c8a4',
          titleFont: { size: 12, weight: '600' },
          bodyColor: '#ffffff',
          bodyFont: { size: 14, weight: '700' },
          padding: { x: 16, y: 12 },
          cornerRadius: 10,
          displayColors: false,
          callbacks: {
            title: (items) => items[0].label,
            label: (ctx) => `${ctx.parsed.y.toLocaleString()} ₩`
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '날짜',
            color: '#b0af9f',
            font: { size: 11, weight: '500' },
            padding: { top: 8 },
          },
          ticks: {
            maxTicksLimit: 7,
            color: '#b0af9f',
            font: { size: 11 },
            maxRotation: 0,
          },
          grid: { display: false },
          border: { display: false }
        },
        y: {
          position: 'right',
          title: {
            display: true,
            text: '환율 (KRW)',
            color: '#b0af9f',
            font: { size: 11, weight: '500' },
            padding: { bottom: 8 },
          },
          ticks: {
            color: '#b0af9f',
            font: { size: 11 },
            callback: (val) => val.toLocaleString(),
            maxTicksLimit: 6,
          },
          grid: {
            color: 'rgba(0,0,0,0.04)',
            drawTicks: false,
          },
          border: { display: false, dash: [4, 4] }
        }
      }
    }
  })
}

const loadChart = async (code, days) => {
  if (!code || !days) return
  isCustomMode.value = false
  loading.value = true
  error.value = ''
  try {
    const res = await fetchChartData(code, days)
    const chartData = res.data.chart_data
    const labels = chartData.map(d => d.date)
    const data = chartData.map(d => d.rate)
    loading.value = false
    await nextTick()
    renderChart(labels, data)
  } catch (e) {
    error.value = '차트 데이터를 불러올 수 없습니다.'
    loading.value = false
  }
}

const loadCustomChart = async () => {
  if (!customStart.value || !customEnd.value || !props.selectedCode) return

  const start = new Date(customStart.value)
  const end = new Date(customEnd.value)
  const days = Math.ceil((end - start) / (1000 * 60 * 60 * 24)) + 1

  if (days <= 0) {
    error.value = '종료일이 시작일보다 빠릅니다.'
    return
  }

  isCustomMode.value = true
  selectedDays.value = null
  loading.value = true
  error.value = ''
  try {
    const res = await fetchChartData(props.selectedCode, days)
    const chartData = res.data.chart_data
    const labels = chartData.map(d => d.date)
    const data = chartData.map(d => d.rate)
    loading.value = false
    await nextTick()
    renderChart(labels, data)
  } catch (e) {
    error.value = '차트 데이터를 불러올 수 없습니다.'
    loading.value = false
  }
}

const changeFilter = (days) => {
  isCustomMode.value = false
  selectedDays.value = days
  
  // 날짜 피커 자동 업데이트
  const end = new Date()
  const start = new Date()
  start.setDate(start.getDate() - days)
  customEnd.value = end
  customStart.value = start

  loadChart(props.selectedCode, days)
}

watch(() => props.selectedCode, (code) => {
  if (code) {
    isCustomMode.value = false
    selectedDays.value = 30
    // 날짜 피커 기본값: 1달 전 ~ 오늘
    const end = new Date()
    const start = new Date()
    start.setMonth(start.getMonth() - 1)
    customEnd.value = end
    customStart.value = start
    loadChart(code, 30)
  } else {
    selectedDays.value = null
    customStart.value = null
    customEnd.value = null
  }
})
</script>

<style scoped>
.chart-card {
  background: #fff;
  border-radius: 14px;
  border: 0.5px solid #c8c7b8;
  padding: 1.75rem 2rem;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}
.chart-inner { display: flex; flex-direction: column; }
.card-label {
  font-size: 15px;
  color: #3a3a2e;
  letter-spacing: 0.01em;
  font-weight: 700;
}
.empty-state {
  color: #aaa;
  font-size: 15px;
  text-align: center;
  padding: 4rem 0;
}
.filter-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.filter-btn {
  padding: 7px 18px;
  border-radius: 20px;
  border: 1.5px solid #A0BAA3;
  background: #fff;
  color: #86A78A;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.15s;
}
.filter-btn.active { background: #86A78A; color: #fff; border-color: #86A78A; }
.filter-btn:hover:not(.active) { background: #f3f5f0; }

/* 날짜 설정 영역 */
.custom-date-row {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  flex-wrap: wrap;
  background: #f9f8f5;
  border-radius: 12px;
  padding: 14px 16px;
  border: 0.5px solid #e8e7de;
}
.date-input-wrap {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 140px;
}
.date-input-wrap label {
  font-size: 11px;
  color: #a0a090;
  font-weight: 600;
}
.date-separator {
  color: #A0BAA3;
  font-weight: 500;
  padding-bottom: 8px;
}
.date-search-btn {
  padding: 9px 18px;
  border-radius: 8px;
  border: none;
  background: #6a9e6e;
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
  white-space: nowrap;
  height: 38px;
}
.date-search-btn:hover:not(:disabled) { background: #5a8a5e; }
.date-search-btn:disabled { background: #c8d9c9; cursor: not-allowed; }

/* VueDatePicker 커스텀 */
.custom-dp {
  --dp-font-family: -apple-system, sans-serif;
  --dp-border-radius: 8px;
  --dp-input-padding: 8px 12px;
  --dp-font-size: 13px;
  --dp-input-border-color: #A0BAA3;
  --dp-input-focus-border-color: #6a9e6e;
  --dp-primary-color: #6a9e6e;
  --dp-primary-text-color: #fff;
  --dp-secondary-color: #f3f5f0;
  --dp-hover-color: #eaf2ea;
  --dp-hover-text-color: #2d2d25;
  --dp-highlight-color: rgba(106, 158, 110, 0.1);
  --dp-border-color: #A0BAA3;
  --dp-menu-border-color: #e8e7de;
  --dp-icon-color: #86A78A;
  --dp-danger-color: #c0756a;
  --dp-disabled-color: #f0efea;
  --dp-scroll-bar-color: #c8d9c9;
  --dp-background-color: #fff;
  --dp-text-color: #2d2d25;
  --dp-header-color: #f9f8f5;
}

.chart-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: #888876;
  font-size: 14px;
}
.alert-error {
  background: #fdecea;
  color: #a05050;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  font-size: 14px;
}
.canvas-wrap { width: 100%; }
canvas { width: 100% !important; }
</style>