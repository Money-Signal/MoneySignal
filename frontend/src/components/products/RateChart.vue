<template>
  <div class="chart-wrap">
    <canvas ref="chartRef" />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import {
  Chart, BarElement, BarController,
  LinearScale, CategoryScale, Tooltip, Legend,
} from 'chart.js'

Chart.register(BarElement, BarController, LinearScale, CategoryScale, Tooltip, Legend)

const props = defineProps({
  product: { type: Object, required: true },
})

const chartRef = ref(null)
let chartInstance = null

function getTermData() {
  const options = props.product?.options || []
  const termMap = {}
  for (const opt of options) {
    const t = opt.save_trm
    if (!termMap[t]) termMap[t] = { base: [], max: [] }
    if (opt.intr_rate != null)  termMap[t].base.push(opt.intr_rate)
    if (opt.intr_rate2 != null) termMap[t].max.push(opt.intr_rate2)
  }
  const terms = Object.keys(termMap).map(Number).sort((a, b) => a - b)
  return {
    terms,
    baseRates: terms.map(t => termMap[t].base.length ? Math.max(...termMap[t].base) : null),
    maxRates:  terms.map(t => termMap[t].max.length  ? Math.max(...termMap[t].max)  : null),
  }
}

function buildChart() {
  if (!chartRef.value) return
  if (chartInstance) chartInstance.destroy()

  const { terms, baseRates, maxRates } = getTermData()
  if (!terms.length) return

  chartInstance = new Chart(chartRef.value, {
    type: 'bar',
    data: {
      labels: terms.map(t => t + '개월'),
      datasets: [
        {
          label: '기본금리',
          data: baseRates,
          backgroundColor: 'rgba(134,167,138,0.35)',
          borderColor: 'rgba(134,167,138,0.7)',
          borderWidth: 1,
          borderRadius: 5,
          borderSkipped: false,
        },
        {
          label: '최고금리',
          data: maxRates,
          backgroundColor: 'rgba(134,167,138,0.85)',
          borderColor: '#86A78A',
          borderWidth: 1,
          borderRadius: 5,
          borderSkipped: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      aspectRatio: 3,
      categoryPercentage: 0.55,
      barPercentage: 0.8,
      plugins: {
        legend: {
          position: 'top',
          labels: {
            boxWidth: 11,
            boxHeight: 11,
            borderRadius: 3,
            useBorderRadius: true,
            padding: 14,
            font: { size: 11 },
          },
        },
        tooltip: {
          callbacks: {
            label: ctx => ` ${ctx.dataset.label}: ${ctx.parsed.y ?? '-'}%`,
          },
        },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 } },
        },
        y: {
          grid: { color: '#f0efe8' },
          ticks: { callback: v => v + '%', font: { size: 10 } },
          suggestedMin: 0,
        },
      },
    },
  })
}

onMounted(buildChart)
onUnmounted(() => { if (chartInstance) chartInstance.destroy() })
watch(() => props.product, async () => { await nextTick(); buildChart() })
</script>

<style scoped>
.chart-wrap {
  background: #fafaf5;
  border-radius: 10px;
  padding: 12px 14px;
  margin-bottom: 16px;
}
</style>
