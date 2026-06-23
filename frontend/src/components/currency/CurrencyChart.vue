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

      <canvas v-if="!loading && !error" ref="chartCanvas"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import {
  Chart, LineElement, PointElement, LinearScale,
  CategoryScale, LineController, Tooltip, Legend, Filler
} from 'chart.js'
import { fetchChartData } from '@/api/currency'

Chart.register(LineElement, PointElement, LinearScale, CategoryScale, LineController, Tooltip, Legend, Filler)

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
  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: `${props.selectedCode} → KRW`,
        data,
        borderColor: '#86A78A',
        backgroundColor: 'rgba(160, 186, 163, 0.15)',
        fill: true,
        tension: 0.4,
        pointRadius: 3,
        pointBackgroundColor: '#86A78A',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
      }]
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          display: true,
          labels: { color: '#3a3a2e', font: { size: 12 } }
        },
        tooltip: {
          mode: 'index',
          intersect: false,
          backgroundColor: '#2e4a31',
          titleColor: '#A0BAA3',
          bodyColor: '#fff',
          padding: 10,
          callbacks: {
            label: (ctx) => ` ${ctx.parsed.y.toLocaleString()} ₩`
          }
        }
      },
      scales: {
        x: {
          ticks: { maxTicksLimit: 8, color: '#888876', font: { size: 11 } },
          grid: { color: 'rgba(0,0,0,0.04)' }
        },
        y: {
          ticks: {
            color: '#888876',
            font: { size: 11 },
            callback: (val) => val.toLocaleString() + ' ₩'
          },
          grid: { color: 'rgba(0,0,0,0.04)' }
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
  padding: 1.25rem 1.5rem;
}
.card-label {
  font-size: 12px;
  color: #888876;
  letter-spacing: 0.04em;
}
.empty-state {
  color: #aaa;
  font-size: 14px;
  text-align: center;
  padding: 2rem 0;
}
.filter-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.filter-btn {
  padding: 5px 14px;
  border-radius: 20px;
  border: 1.5px solid #A0BAA3;
  background: #fff;
  color: #86A78A;
  font-size: 13px;
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
</style>