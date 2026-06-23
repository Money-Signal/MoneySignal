<template>
  <div class="currency-rate">
    <div class="page-header mb-4">
      <h2 class="page-title">
        <i class="bi bi-currency-exchange me-2"></i>환율 조회
      </h2>
      <p class="page-sub">실시간 환율 및 과거 추이를 확인하세요</p>
    </div>

    <div class="rate-card mb-3">
      <p class="card-label">통화 선택</p>
      <div class="select-wrap">
        <select :value="selectedCode" @change="$emit('update:selectedCode', $event.target.value)" class="currency-select">
          <option value="">통화를 선택하세요</option>
          <option v-for="item in rates" :key="item.cur_unit" :value="item.cur_unit">
            {{ item.cur_unit }} - {{ item.cur_nm }}
          </option>
        </select>
        <i class="bi bi-chevron-down select-icon"></i>
      </div>

      <div v-if="selectedRate" class="rate-display mt-3">
        <div class="rate-info">
          <p class="rate-main">
            1 {{ selectedRate.cur_unit }}
            <span class="rate-arrow">→</span>
            <span class="rate-value">{{ Number(selectedRate.deal_bas_r).toLocaleString() }} KRW</span>
          </p>
          <p class="rate-sub">
            <i class="bi bi-clock me-1"></i>최근 영업일 기준 · 매매기준율
          </p>
        </div>
        <span class="rate-badge">{{ selectedRate.cur_nm }}</span>
      </div>

      <div v-if="selectedRate" class="stat-row mt-3">
        <div class="stat-card">
          <p class="stat-label"><i class="bi bi-arrow-left-right me-1"></i>전일 대비</p>
          <p class="stat-val" :class="change > 0 ? 'up' : change < 0 ? 'down' : ''">
            {{ change > 0 ? '+' : '' }}{{ change.toFixed(2) }}
          </p>
        </div>
        <div class="stat-card">
          <p class="stat-label"><i class="bi bi-arrow-up me-1"></i>1달 최고</p>
          <p class="stat-val">{{ monthHigh.toLocaleString() }}</p>
        </div>
        <div class="stat-card">
          <p class="stat-label"><i class="bi bi-arrow-down me-1"></i>1달 최저</p>
          <p class="stat-val">{{ monthLow.toLocaleString() }}</p>
        </div>
      </div>
    </div>

    <div v-if="error" class="alert-error">
      <i class="bi bi-exclamation-circle me-2"></i>{{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { fetchLatestRates, fetchChartData } from '@/api/currency'

const props = defineProps({
  selectedCode: { type: String, default: '' }
})

defineEmits(['update:selectedCode'])

const rates = ref([])
const error = ref('')
const change = ref(0)
const monthHigh = ref(0)
const monthLow = ref(0)

const selectedRate = computed(() => {
  if (!props.selectedCode) return null
  return rates.value.find(item => item.cur_unit === props.selectedCode) || null
})

const loadStats = async (code) => {
  if (!code) return
  try {
    const res = await fetchChartData(code, 30)
    const data = res.data.chart_data
    if (!data || data.length < 2) return
    const rateList = data.map(d => d.rate)
    monthHigh.value = Math.max(...rateList)
    monthLow.value = Math.min(...rateList)
    change.value = rateList[rateList.length - 1] - rateList[rateList.length - 2]
  } catch (e) {
    console.error('통계 데이터 로드 실패:', e)
  }
}

watch(() => props.selectedCode, (code) => {
  if (code) loadStats(code)
})

onMounted(async () => {
  try {
    const res = await fetchLatestRates()
    rates.value = res.data.filter(item => item.deal_bas_r && item.deal_bas_r !== '-')
  } catch (e) {
    error.value = '환율 데이터를 불러올 수 없습니다.'
  }
})
</script>

<style scoped>
.page-title {
  font-size: 22px;
  font-weight: 500;
  color: #3a3a2e;
}
.page-sub {
  font-size: 14px;
  color: #6b6b5a;
  margin-top: 4px;
}
.rate-card {
  background: #fff;
  border-radius: 14px;
  border: 0.5px solid #c8c7b8;
  padding: 1.25rem 1.5rem;
}
.card-label {
  font-size: 12px;
  color: #888876;
  margin-bottom: 0.5rem;
  letter-spacing: 0.04em;
}
.select-wrap {
  position: relative;
}
.currency-select {
  width: 100%;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1.5px solid #A0BAA3;
  background: #f7f7f0;
  font-size: 15px;
  color: #3a3a2e;
  appearance: none;
  cursor: pointer;
  outline: none;
}
.select-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #86A78A;
  pointer-events: none;
}
.rate-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f3f5f0;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  gap: 12px;
}
.rate-main {
  font-size: 18px;
  font-weight: 500;
  color: #2e4a31;
}
.rate-arrow {
  margin: 0 8px;
  color: #A0BAA3;
}
.rate-value {
  color: #86A78A;
}
.rate-sub {
  font-size: 12px;
  color: #7a9a7d;
  margin-top: 4px;
}
.rate-badge {
  background: #A0BAA3;
  color: #fff;
  font-size: 12px;
  padding: 4px 12px;
  border-radius: 20px;
  white-space: nowrap;
}
.stat-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}
.stat-card {
  background: #f3f5f0;
  border-radius: 10px;
  padding: 0.75rem 1rem;
}
.stat-label {
  font-size: 11px;
  color: #888876;
  margin-bottom: 4px;
}
.stat-val {
  font-size: 16px;
  font-weight: 500;
  color: #2e4a31;
}
.stat-val.up { color: #4a8a4e; }
.stat-val.down { color: #a05050; }
.alert-error {
  background: #fdecea;
  color: #a05050;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  font-size: 14px;
}
</style>