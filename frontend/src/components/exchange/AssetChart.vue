<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import Chart from 'chart.js/auto'

const props = defineProps({
  chartData: {
    type: Object,
    required: true,
    default: () => ({ asset_type: 'gold', labels: [], prices: [] })
  }
})

const chartCanvas = ref(null)
let chartInstance = null

// 자산 타입에 따른 다이내믹 컬러 추출 함수
const getAssetColors = (type) => {
  if (type === 'gold') {
    return {
      borderColor: '#D4AF37',       // 고급스러운 골드
      backgroundColor: 'rgba(212, 175, 55, 0.08)',
      pointHoverBackgroundColor: '#D4AF37'
    }
  } else {
    return {
      borderColor: '#8A9A86',       // 세련된 실버/플래티넘 톤 (MoneySignal 무드 조화)
      backgroundColor: 'rgba(138, 154, 134, 0.08)',
      pointHoverBackgroundColor: '#8A9A86'
    }
  }
}

const renderChart = async () => {
  await nextTick()

  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }

  if (!chartCanvas.value || !props.chartData.labels || props.chartData.labels.length === 0) {
    return
  }

  const colors = getAssetColors(props.chartData.asset_type)

  chartInstance = new Chart(chartCanvas.value, {
    type: 'line',
    data: {
      labels: props.chartData.labels,
      datasets: [
        {
          label: props.chartData.asset_type === 'gold' ? '금 가격 (USD)' : '은 가격 (USD)',
          data: props.chartData.prices,
          borderColor: colors.borderColor,
          backgroundColor: colors.backgroundColor,
          borderWidth: 2.5,
          pointRadius: 0,
          pointHoverRadius: 5,
          pointHoverBackgroundColor: colors.pointHoverBackgroundColor,
          fill: true,
          tension: 0.1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { maxTicksLimit: 12, color: '#556256' }
        },
        y: {
          beginAtZero: false,
          grid: { color: '#EBEADD' },
          ticks: { color: '#556256' }
        }
      }
    }
  })
}

watch(
  () => props.chartData,
  () => { renderChart() },
  { deep: true }
)

onMounted(() => { renderChart() })
onBeforeUnmount(() => {
  if (chartInstance) chartInstance.destroy()
})
</script>

<style scoped>
.chart-container {
  position: relative;
  width: 100%;
  height: 400px;
}
canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}
</style>