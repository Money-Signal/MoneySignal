<template>
  <div class="currency-rate">
    <div class="rate-card mb-3">
      <p class="card-label">통화 선택</p>

      <div class="custom-select-wrapper" ref="dropdownRef">
        <div
          class="custom-select-box"
          :class="{ open: isOpen }"
          @click="isOpen = !isOpen"
        >
          <span :class="{ 'is-placeholder': !selectedCode }">
            {{ selectedLabel }}
          </span>
          <svg class="arrow-icon" :class="{ rotated: isOpen }" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
        <ul v-if="isOpen" class="custom-options">
          <li class="is-placeholder" @click="selectOption('')">통화를 선택하세요</li>
          <li
            v-for="item in rates"
            :key="item.cur_unit"
            :class="{ selected: selectedCode === item.cur_unit }"
            @click="selectOption(item.cur_unit)"
          >
            {{ item.cur_unit }} - {{ item.cur_nm }}
          </li>
        </ul>
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

    <!-- 환율 계산기 -->
    <div v-if="selectedRate" class="calc-card mb-3">
      <p class="card-label">환율 계산기</p>
      <div class="calc-row">
        <div class="calc-input-wrap">
          <input
            v-model.number="calcAmount"
            type="number"
            class="calc-input"
            placeholder="금액 입력"
            min="0"
          />
          <span class="calc-unit">{{ isKrwToForeign ? 'KRW' : selectedRate.cur_unit }}</span>
        </div>

        <button class="swap-btn" @click="isKrwToForeign = !isKrwToForeign">
          <i class="bi bi-arrow-left-right"></i>
        </button>

        <div class="calc-result-wrap">
          <span class="calc-result">{{ calcResult }}</span>
          <span class="calc-unit">{{ isKrwToForeign ? selectedRate.cur_unit : 'KRW' }}</span>
        </div>
      </div>
      <p class="calc-desc">
        1 {{ selectedRate.cur_unit }} = {{ Number(selectedRate.deal_bas_r).toLocaleString() }} KRW 기준
      </p>
    </div>

    <div v-if="error" class="alert-error">
      <i class="bi bi-exclamation-circle me-2"></i>{{ error }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue'
import { fetchLatestRates, fetchChartData } from '@/api/currency'

const props = defineProps({
  selectedCode: { type: String, default: '' }
})

const emit = defineEmits(['update:selectedCode'])

const rates = ref([])
const error = ref('')
const isOpen = ref(false)
const dropdownRef = ref(null)
const change = ref(0)
const monthHigh = ref(0)
const monthLow = ref(0)
const calcAmount = ref(null)
const isKrwToForeign = ref(true)

const selectedLabel = computed(() => {
  if (!props.selectedCode) return '통화를 선택하세요'
  const found = rates.value.find(item => item.cur_unit === props.selectedCode)
  return found ? `${found.cur_unit} - ${found.cur_nm}` : '통화를 선택하세요'
})

const selectedRate = computed(() => {
  if (!props.selectedCode) return null
  return rates.value.find(item => item.cur_unit === props.selectedCode) || null
})

const calcResult = computed(() => {
  if (!calcAmount.value || !selectedRate.value) return '-'
  const rate = Number(selectedRate.value.deal_bas_r)
  if (!rate) return '-'
  if (isKrwToForeign.value) {
    return (calcAmount.value / rate).toFixed(4)
  } else {
    return (calcAmount.value * rate).toLocaleString()
  }
})

const selectOption = (code) => {
  emit('update:selectedCode', code)
  isOpen.value = false
  calcAmount.value = null
  isKrwToForeign.value = true
}

const handleClickOutside = (e) => {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

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
  document.addEventListener('click', handleClickOutside)
  try {
    const res = await fetchLatestRates()
    rates.value = res.data.filter(item => item.deal_bas_r && item.deal_bas_r !== '-')
  } catch (e) {
    error.value = '환율 데이터를 불러올 수 없습니다.'
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.currency-rate {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.page-title {
  font-size: 26px;
  font-weight: 600;
  color: #3a3a2e;
}
.page-sub {
  font-size: 15px;
  color: #6b6b5a;
  margin-top: 4px;
}
.rate-card {
  background: #fff;
  border-radius: 14px;
  border: 0.5px solid #c8c7b8;
  padding: 1.75rem 2rem;
}
.calc-card {
  background: #fff;
  border-radius: 14px;
  border: 0.5px solid #c8c7b8;
  padding: 1.75rem 2rem;
}
.card-label {
  font-size: 15px;
  color: #3a3a2e;
  margin-bottom: 0.75rem;
  letter-spacing: 0.01em;
  font-weight: 700;
}
.custom-select-wrapper {
  position: relative;
}
.custom-select-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  font-size: 15px;
  border: 1.5px solid #A0BAA3;
  border-radius: 8px;
  background-color: #ffffff;
  cursor: pointer;
  user-select: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.custom-select-box.open {
  border-color: #86A78A;
  box-shadow: 0 0 0 2px rgba(134, 167, 138, 0.2);
}
.custom-select-box span {
  color: #333;
  font-size: 15px;
}
.custom-select-box span.is-placeholder {
  color: #aaa;
}
.arrow-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  transition: transform 0.2s;
  color: #86A78A;
}
.arrow-icon.rotated {
  transform: rotate(180deg);
}
.custom-options {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1.5px solid #A0BAA3;
  border-radius: 8px;
  max-height: 220px;
  overflow-y: auto;
  list-style: none;
  margin: 0;
  padding: 4px 0;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.custom-options li {
  padding: 10px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.15s;
  color: #333;
}
.custom-options li.is-placeholder {
  color: #aaa;
}
.custom-options li:hover {
  background-color: #f0f4f0;
}
.custom-options li.selected {
  color: #606c38;
  font-weight: 600;
  background-color: #edf2ed;
}
.custom-options::-webkit-scrollbar {
  width: 4px;
}
.custom-options::-webkit-scrollbar-thumb {
  background: #c4c3b7;
  border-radius: 4px;
}
.rate-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #f3f5f0;
  border-radius: 12px;
  padding: 1.25rem 1.5rem;
  gap: 12px;
}
.rate-main {
  font-size: 24px;
  font-weight: 600;
  color: #2e4a31;
}
.rate-arrow {
  margin: 0 10px;
  color: #A0BAA3;
}
.rate-value {
  color: #86A78A;
}
.rate-sub {
  font-size: 13px;
  color: #7a9a7d;
  margin-top: 6px;
}
.rate-badge {
  background: #A0BAA3;
  color: #fff;
  font-size: 14px;
  padding: 6px 16px;
  border-radius: 20px;
  white-space: nowrap;
}
.stat-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}
.stat-card {
  background: #f3f5f0;
  border-radius: 12px;
  padding: 1rem 1.25rem;
}
.stat-label {
  font-size: 13px;
  color: #888876;
  margin-bottom: 6px;
}
.stat-val {
  font-size: 20px;
  font-weight: 600;
  color: #2e4a31;
}
.stat-val.up { color: #4a8a4e; }
.stat-val.down { color: #a05050; }
.calc-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.calc-input-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  border: 1.5px solid #A0BAA3;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}
.calc-input {
  flex: 1;
  border: none;
  outline: none;
  padding: 12px 14px;
  font-size: 16px;
  color: #333;
  background: transparent;
  width: 100%;
}
.calc-input::-webkit-inner-spin-button,
.calc-input::-webkit-outer-spin-button {
  appearance: none;
}
.calc-unit {
  padding: 12px 12px;
  font-size: 14px;
  color: #86A78A;
  font-weight: 600;
  background: #f3f5f0;
  white-space: nowrap;
}
.swap-btn {
  background: #86A78A;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #fff;
  font-size: 16px;
  flex-shrink: 0;
  transition: background 0.15s;
}
.swap-btn:hover {
  background: #6f9473;
}
.calc-result-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  border: 1.5px solid #c8c7b8;
  border-radius: 8px;
  overflow: hidden;
  background: #f7f7f0;
}
.calc-result {
  flex: 1;
  padding: 12px 14px;
  font-size: 16px;
  font-weight: 500;
  color: #2e4a31;
}
.calc-desc {
  font-size: 13px;
  color: #aaa;
  margin-top: 10px;
  text-align: right;
}
.alert-error {
  background: #fdecea;
  color: #a05050;
  border-radius: 10px;
  padding: 0.75rem 1rem;
  font-size: 14px;
}
</style>