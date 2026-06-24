<template>
  <div class="chart-card">
    <!-- 통화 미선택 시: 흰 카드 안에 안내문 -->
    <div v-if="!selectedCode" class="empty-state">
      <i class="bi bi-bar-chart-line me-2"></i>통화를 선택하면 차트가 표시됩니다
    </div>

    <!-- 통화 선택 후 -->
    <div v-else>
      <p class="card-label mb-3">
        <i class="bi bi-graph-up me-1"></i>환율 추이
      </p>

      <div class="filter-row mb-3">
        <button
          v-for="f in filters"
          :key="f.days"
          :class="['filter-btn', { active: selectedDays === f.days }]"
          @click="changeFilter(f.days)"
        >
          {{ f.label }}
        </button>
      </div>

      <div v-if="loading" class="chart-loading">
        <div class="spinner-border spinner-border-sm text-secondary me-2"></div>
        불러오는 중...
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
import { ref, watch, nextTick } from 'vue'
import {
  Chart, LineElement, PointElement, LinearScale,
  CategoryScale, LineController, Tooltip, Legend, Filler, Title
} from 'chart.js'
import { fetchChartData } from '@/api/currency'

Chart.register(LineElement, PointElement, LinearScale, CategoryScale, LineController, Tooltip, Legend, Filler, Title)

const props = defineProps({
  selectedCode: { type: String, default: '' }
})

const chartCanvas = ref(null)
const loading = ref(false)
const error = ref('')
const selectedDays = ref(null)  // ← 기본값 null (아무것도 선택 안 된 상태)
let chartInstance = null

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
  loading.value = true
  error.value = ''
  try {
    const res = await fetchChartData(code, days)
    const chartData = res.data.chart_data
    const labels = chartData.map(d => d.date)
    const data = chartData.map(d => d.rate)

    loading.value = false  // ← canvas가 DOM에 나타나도록 먼저 false로
    await nextTick()       // ← DOM 업데이트 기다리기
    renderChart(labels, data)
  } catch (e) {
    error.value = '차트 데이터를 불러올 수 없습니다.'
    loading.value = false  // ← 에러 시에도 false로
  }
}

const changeFilter = (days) => {
  selectedDays.value = days
  loadChart(props.selectedCode, days)
}

// 통화 선택 시 필터도 1달로 자동 선택 후 차트 로드
watch(() => props.selectedCode, (code) => {
  if (code) {
    selectedDays.value = 30  // ← 통화 선택하면 1달 기본 선택
    loadChart(code, 30)
  } else {
    selectedDays.value = null  // ← 통화 해제 시 필터도 초기화
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
.filter-wrap {
  display: flex;
  gap: 8px;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
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
.filter-btn.active {
  background: #86A78A;
  color: #fff;
  border-color: #86A78A;
}
.filter-btn:hover:not(.active) {
  background: #f3f5f0;
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
.canvas-wrap {
  width: 100%;
}
canvas {
  width: 100% !important;
}
</style>