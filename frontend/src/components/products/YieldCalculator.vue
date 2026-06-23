<template>
  <div class="calc-card">
    <div class="calc-header">
      <i class="bi bi-calculator" />수익 계산기
    </div>
    <div class="calc-body">

      <!-- 입력 영역 -->
      <div class="d-flex flex-column gap-3 mb-4">

        <!-- 저축기간 -->
        <div>
          <label class="calc-label">저축기간</label>
          <div class="term-grid">
            <button
              v-for="term in availableTerms"
              :key="term"
              :class="['term-btn', selectedTerm === term ? 'active' : '']"
              @click="selectedTerm = term"
            >
              {{ term }}개월
            </button>
          </div>
        </div>

        <!-- 적립유형 (적금만) -->
        <div v-if="product.product_type === 'S' && availableRsrvTypes.length > 1">
          <label class="calc-label">적립유형</label>
          <div class="term-grid">
            <button
              v-for="rt in availableRsrvTypes"
              :key="rt.code"
              :class="['term-btn', selectedRsrvType === rt.code ? 'active' : '']"
              @click="selectedRsrvType = rt.code"
            >
              {{ rt.name }}
            </button>
          </div>
        </div>

        <!-- 금액 입력 -->
        <div>
          <label class="calc-label">
            {{ product.product_type === 'D' ? '원금' : '월 납입액' }}
          </label>
          <div class="input-group">
            <input
              v-model.number="amount"
              type="number"
              class="form-control calc-input"
              :placeholder="product.product_type === 'D' ? '예: 10,000,000' : '예: 100,000'"
              min="1"
            />
            <span class="input-group-text bg-white">원</span>
          </div>
        </div>
      </div>

      <!-- 결과 영역 -->
      <template v-if="amount > 0 && results.length > 0">
        <div v-for="result in results" :key="result.label">

          <p v-if="results.length > 1" class="text-muted small fw-semibold mb-2">
            {{ result.label }} 기준
          </p>

          <!-- 기본금리 / 최고금리 비교 -->
          <div class="result-grid mb-3">
            <div class="result-col base">
              <div class="result-col-title">기본금리 {{ result.intr_rate }}%</div>
              <div class="result-row">
                <span class="result-row-label">세전 이자</span>
                <span>{{ formatWon(result.base.beforeTax) }}</span>
              </div>
              <div class="result-row text-danger">
                <span class="result-row-label">세금</span>
                <span>-{{ formatWon(result.base.tax) }}</span>
              </div>
              <div class="result-row">
                <span class="result-row-label">세후 이자</span>
                <span class="fw-semibold">{{ formatWon(result.base.afterTax) }}</span>
              </div>
              <hr class="my-2" />
              <div class="result-total">
                <span class="result-row-label">만기수령액</span>
                <span class="total-value">{{ formatWon(result.base.total) }}</span>
              </div>
            </div>

            <div class="result-col best">
              <div class="result-col-title text-success">최고금리 {{ result.intr_rate2 }}%</div>
              <div class="result-row">
                <span class="result-row-label">세전 이자</span>
                <span>{{ formatWon(result.max.beforeTax) }}</span>
              </div>
              <div class="result-row text-danger">
                <span class="result-row-label">세금</span>
                <span>-{{ formatWon(result.max.tax) }}</span>
              </div>
              <div class="result-row">
                <span class="result-row-label">세후 이자</span>
                <span class="fw-semibold text-success">{{ formatWon(result.max.afterTax) }}</span>
              </div>
              <hr class="my-2" />
              <div class="result-total">
                <span class="result-row-label">만기수령액</span>
                <span class="total-value text-success">{{ formatWon(result.max.total) }}</span>
              </div>
            </div>
          </div>

        </div>

        <!-- 주의사항 -->
        <ul class="notice-list">
          <li>일반과세(이자소득세 15.4%) 기준</li>
          <li v-if="hasCompound">복리는 월복리 기준 (실제와 다를 수 있음)</li>
          <li v-if="product.product_type === 'S'">월초 납입 기준 단리 계산</li>
          <li v-if="isFreeRsrv">자유적립은 월평균 납입액 기준 근사값</li>
          <li>실제 수령액은 상품 조건에 따라 다를 수 있음</li>
        </ul>
      </template>

      <!-- 금액 미입력 안내 -->
      <div v-else class="empty-state">
        <i class="bi bi-calculator" />
        <p>금액을 입력하면<br />예상 수익이 계산됩니다</p>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  product: {
    type: Object,
    required: true,
  },
})

const amount = ref(null)
const selectedTerm = ref(null)
const selectedRsrvType = ref(null)

// 사용 가능한 기간 목록 (중복 제거, 오름차순)
const availableTerms = computed(() => {
  if (!props.product?.options) return []
  const terms = [...new Set(props.product.options.map(o => o.save_trm))]
  return terms.sort((a, b) => a - b)
})

// 선택된 기간에서 가능한 적립유형 목록 (적금만)
const availableRsrvTypes = computed(() => {
  if (props.product?.product_type !== 'S' || !selectedTerm.value) return []
  const seen = new Set()
  return props.product.options
    .filter(o => o.save_trm === selectedTerm.value)
    .filter(o => {
      if (seen.has(o.rsrv_type)) return false
      seen.add(o.rsrv_type)
      return true
    })
    .map(o => ({ code: o.rsrv_type, name: o.rsrv_type_nm || o.rsrv_type }))
})

// 기간 목록이 바뀌면 첫 번째 기간으로 초기화
watch(availableTerms, (terms) => {
  if (terms.length > 0) selectedTerm.value = terms[0]
}, { immediate: true })

// 기간 또는 적립유형 목록이 바뀌면 첫 번째 값으로 초기화
watch([selectedTerm, availableRsrvTypes], ([, rsrvTypes]) => {
  if (rsrvTypes.length > 0) selectedRsrvType.value = rsrvTypes[0].code
})

// 선택 조건에 맞는 옵션들
const matchingOptions = computed(() => {
  if (!props.product?.options || !selectedTerm.value) return []
  const byTerm = props.product.options.filter(o => o.save_trm === selectedTerm.value)
  if (props.product.product_type === 'S') {
    return byTerm.filter(o => o.rsrv_type === selectedRsrvType.value)
  }
  // 예금은 단리/복리 옵션 모두 표시
  return byTerm
})

// 이자 계산
function calcInterest(rate, term, isCompound) {
  if (!amount.value || !rate) return 0
  const r = Number(rate)
  if (props.product.product_type === 'D') {
    if (isCompound) {
      // 예금 복리 (월복리)
      return amount.value * (Math.pow(1 + r / 100 / 12, term) - 1)
    }
    // 예금 단리
    return amount.value * (r / 100) * (term / 12)
  }
  // 적금 단리 (월초 납입 기준)
  return amount.value * (r / 100 / 12) * (term * (term + 1) / 2)
}

function buildResult(interest) {
  const tax = interest * 0.154
  const afterTax = interest - tax
  // 예금: 원금 + 세후이자 / 적금: 총납입액 + 세후이자
  const principal =
    props.product.product_type === 'D'
      ? amount.value
      : amount.value * selectedTerm.value
  return {
    beforeTax: Math.round(interest),
    tax: Math.round(tax),
    afterTax: Math.round(afterTax),
    total: Math.round(principal + afterTax),
  }
}

const results = computed(() => {
  if (!amount.value || matchingOptions.value.length === 0) return []
  return matchingOptions.value.map(opt => {
    const isCompound = opt.intr_rate_type === 'M'
    return {
      label: opt.intr_rate_type_nm || (isCompound ? '복리' : '단리'),
      intr_rate: opt.intr_rate,
      intr_rate2: opt.intr_rate2,
      base: buildResult(calcInterest(opt.intr_rate, opt.save_trm, isCompound)),
      max: buildResult(calcInterest(opt.intr_rate2, opt.save_trm, isCompound)),
    }
  })
})

const hasCompound = computed(() => matchingOptions.value.some(o => o.intr_rate_type === 'M'))
const isFreeRsrv = computed(() => selectedRsrvType.value === 'F')

function formatWon(value) {
  return value.toLocaleString('ko-KR') + '원'
}
</script>

<style scoped>
/* ── 카드 ── */
.calc-card {
  background: #fff;
  border-radius: 14px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  overflow: hidden;
}
.calc-header {
  font-size: 0.9rem;
  font-weight: 700;
  color: #3d3d30;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 18px 24px 14px;
  border-bottom: 1.5px solid #EBEADD;
}
.calc-header i { color: #86A78A; font-size: 1rem; }
.calc-body { padding: 20px 24px 24px; }

/* ── 라벨 ── */
.calc-label {
  display: block;
  font-size: 0.75rem;
  color: #a0a090;
  margin-bottom: 8px;
  font-weight: 500;
}

/* ── 기간/유형 토글 버튼 ── */
.term-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.term-btn {
  padding: 5px 14px;
  font-size: 0.83rem;
  border: 1.5px solid #d4d3c4;
  border-radius: 20px;
  background: white;
  color: #8a8a7a;
  cursor: pointer;
  transition: all 0.15s;
}
.term-btn:hover {
  border-color: #A0BAA3;
  color: #5a8a5e;
}
.term-btn.active {
  border-color: #86A78A;
  background: #86A78A;
  color: white;
}

/* ── 금액 입력 ── */
.calc-input {
  border-right: none;
  border-color: #d4d3c4;
  font-size: 0.9rem;
}
.calc-input:focus {
  border-color: #A0BAA3;
  box-shadow: 0 0 0 0.2rem rgba(160, 186, 163, 0.2);
}
.calc-input:focus + .input-group-text {
  border-color: #A0BAA3;
}
.input-group-text {
  border-color: #d4d3c4;
  background: #fafaf5;
  color: #8a8a7a;
  font-size: 0.88rem;
}

/* ── 결과 2열 ── */
.result-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.result-col {
  border-radius: 10px;
  padding: 14px;
  font-size: 0.82rem;
}
.result-col.base {
  background: #f5f5ee;
}
.result-col.best {
  background: #eef4ef;
  border: 1.5px solid #c4d9c6;
}
.result-col-title {
  font-size: 0.77rem;
  font-weight: 700;
  margin-bottom: 10px;
  color: #5a5a4a;
}
.result-col.best .result-col-title { color: #4a7a51; }

.result-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}
.result-row-label { color: #a0a090; }
.result-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 2px;
}
.total-value {
  font-weight: 700;
  font-size: 0.9rem;
  color: #2d2d25;
}
.result-col.best .total-value { color: #4a7a51; }

/* ── 주의사항 ── */
.notice-list {
  margin: 4px 0 0;
  padding-left: 1rem;
  font-size: 0.73rem;
  color: #c0bfb0;
  line-height: 1.9;
}

/* ── 빈 상태 ── */
.empty-state {
  text-align: center;
  padding: 32px 0;
  color: #d4d3c4;
}
.empty-state i {
  font-size: 2.2rem;
  display: block;
  margin-bottom: 10px;
}
.empty-state p {
  font-size: 0.85rem;
  margin: 0;
  line-height: 1.7;
  color: #b8b7a8;
}
</style>
