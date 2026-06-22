<template>
  <div class="setup-wrapper">
    <div class="setup-container">

      <div class="text-center mb-4">
        <h1 class="brand-title">MoneySignal</h1>
        <p class="text-muted small">나만의 금융 상품 추천 서비스</p>
      </div>

      <div class="setup-card">
        <h4 class="fw-bold mb-1">프로필 설정</h4>
        <p class="text-muted small mb-4">맞춤 추천을 위해 정보를 입력해주세요. 나중에 마이페이지에서 수정 가능해요.</p>

        <form @submit.prevent="handleSubmit">

          <!-- 닉네임 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">닉네임 <span class="text-danger">*</span></label>
            <input
              v-model="form.nickname"
              type="text"
              class="form-control custom-input"
              :class="{ 'is-invalid': errors.nickname }"
              placeholder="사용할 닉네임을 입력해주세요"
            />
            <div class="invalid-feedback">{{ errors.nickname }}</div>
          </div>

          <!-- 연령대 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">연령대</label>
            <div class="d-flex flex-wrap gap-2">
              <label v-for="opt in ageOptions" :key="opt" class="chip-option" :class="{ active: form.age_group === opt }">
                <input type="radio" class="d-none" :value="opt" v-model="form.age_group" />
                {{ opt }}
              </label>
            </div>
          </div>

          <!-- 월 저축 가능 금액 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">월 저축 가능 금액</label>
            <div class="d-flex flex-wrap gap-2">
              <label v-for="opt in savingOptions" :key="opt.label" class="chip-option" :class="{ active: form.monthly_saving === opt.value }">
                <input type="radio" class="d-none" :value="opt.value" v-model="form.monthly_saving" />
                {{ opt.label }}
              </label>
            </div>
          </div>

          <!-- 선호 상품 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">관심 상품</label>
            <div class="d-flex gap-2">
              <label v-for="opt in productTypeOptions" :key="opt.value" class="invest-option flex-fill text-center" :class="{ active: form.preferred_product_type === opt.value }">
                <input type="radio" class="d-none" :value="opt.value" v-model="form.preferred_product_type" />
                <div class="invest-label py-2 px-1">
                  <span class="d-block fs-4">{{ opt.emoji }}</span>
                  <span class="small fw-semibold">{{ opt.label }}</span>
                  <span class="d-block text-muted" style="font-size:0.7rem">{{ opt.desc }}</span>
                </div>
              </label>
            </div>
          </div>

          <!-- 투자 성향 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">투자 성향</label>
            <div class="d-flex gap-2">
              <label v-for="opt in investmentOptions" :key="opt.value" class="invest-option flex-fill text-center" :class="{ active: form.investment_type === opt.value }">
                <input type="radio" class="d-none" :value="opt.value" v-model="form.investment_type" />
                <div class="invest-label py-2 px-1">
                  <span class="d-block fs-4">{{ opt.emoji }}</span>
                  <span class="small fw-semibold">{{ opt.label }}</span>
                  <span class="d-block text-muted" style="font-size:0.7rem">{{ opt.desc }}</span>
                </div>
              </label>
            </div>
          </div>

          <!-- 금융 목표 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">금융 목표</label>
            <input v-model="form.financial_goal" type="text" class="form-control custom-input" placeholder="예) 내 집 마련, 노후 준비, 여행 자금" />
          </div>

          <!-- 목표 금액 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">목표 금액</label>
            <div class="input-group">
              <input v-model="targetAmountInput" type="text" inputmode="numeric" class="form-control custom-input" placeholder="예) 5,000" @input="onTargetAmountInput" />
              <span class="input-group-text unit-text">만원</span>
            </div>
          </div>

          <!-- 투자 기간 슬라이더 -->
          <div class="mb-4">
            <label class="form-label fw-semibold d-flex justify-content-between">
              투자 기간
              <span class="period-badge">{{ form.investment_period ? `${form.investment_period}개월` : '선택 안 함' }}</span>
            </label>
            <input type="range" class="period-slider w-100" min="1" max="36" step="1"
              v-model.number="form.investment_period"
              :style="{ '--val': form.investment_period ?? 1 }"
            />
            <div class="d-flex justify-content-between mt-1">
              <span class="slider-tick">1개월</span>
              <span class="slider-tick">18개월</span>
              <span class="slider-tick">36개월</span>
            </div>
          </div>

          <div v-if="serverError" class="alert alert-danger py-2 small">{{ serverError }}</div>

          <button type="submit" class="btn btn-primary-custom w-100 py-2 mb-2" :disabled="isLoading">
            {{ isLoading ? '저장 중...' : '시작하기' }}
          </button>
          <button type="button" class="btn btn-skip w-100 py-2" @click="skip">
            건너뛰기
          </button>

        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLoading = ref(false)
const serverError = ref('')
const targetAmountInput = ref('')
const errors = ref({ nickname: '' })

const form = ref({
  nickname:               '',
  age_group:              '',
  monthly_saving:         null,
  investment_type:        '',
  preferred_product_type: '',
  financial_goal:         '',
  target_amount:          null,
  investment_period:      null,
})

const ageOptions = ['10대', '20대', '30대', '40대', '50대 이상']

const savingOptions = [
  { label: '10만원 미만',  value: 5   },
  { label: '10~30만원',   value: 20  },
  { label: '30~50만원',   value: 40  },
  { label: '50~100만원',  value: 75  },
  { label: '100~200만원', value: 150 },
  { label: '200만원 이상', value: 200 },
]

const productTypeOptions = [
  { value: 'DEPOSIT', label: '예금',    emoji: '🏦', desc: '목돈 한 번에 납입' },
  { value: 'SAVING',  label: '적금',    emoji: '🪙', desc: '매달 꾸준히 납입' },
  { value: 'BOTH',    label: '상관없음', emoji: '✨', desc: '둘 다 추천받기'   },
]

const investmentOptions = [
  { value: 'CONSERVATIVE', label: '안정형', emoji: '🛡️', desc: '원금 보호 우선' },
  { value: 'MODERATE',     label: '중립형', emoji: '⚖️', desc: '균형 추구'     },
  { value: 'AGGRESSIVE',   label: '공격형', emoji: '🚀', desc: '수익 극대화'   },
]

function onTargetAmountInput(e) {
  const raw = e.target.value.replace(/[^0-9]/g, '')
  form.value.target_amount = raw ? Number(raw) : null
  targetAmountInput.value = raw ? Number(raw).toLocaleString() : ''
}

async function handleSubmit() {
  errors.value.nickname = ''
  if (!form.value.nickname.trim()) {
    errors.value.nickname = '닉네임을 입력해주세요.'
    return
  }

  isLoading.value = true
  serverError.value = ''
  try {
    const formData = new FormData()
    Object.entries(form.value).forEach(([key, value]) => {
      if (value !== '' && value !== null) formData.append(key, value)
    })
    await authStore.updateProfile(formData)
    router.push('/')
  } catch (err) {
    const data = err.response?.data
    if (data?.nickname) errors.value.nickname = data.nickname[0]
    else serverError.value = '저장에 실패했습니다. 다시 시도해주세요.'
  } finally {
    isLoading.value = false
  }
}

// 건너뛰기 — 닉네임만 필수로 저장
async function skip() {
  if (!form.value.nickname.trim()) {
    errors.value.nickname = '닉네임은 필수입니다.'
    return
  }
  isLoading.value = true
  try {
    const formData = new FormData()
    formData.append('nickname', form.value.nickname)
    await authStore.updateProfile(formData)
    router.push('/')
  } catch {
    serverError.value = '저장에 실패했습니다.'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.setup-wrapper {
  min-height: 100vh;
  background-color: #EBEADD;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
}

.setup-container {
  width: 100%;
  max-width: 520px;
}

.brand-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #86A78A;
  letter-spacing: -0.5px;
}

.setup-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  padding: 2rem;
}

.custom-input {
  border: 1.5px solid #ddd;
  border-radius: 8px;
  padding: 0.6rem 0.9rem;
  transition: border-color 0.2s;
}
.custom-input:focus {
  border-color: #A0BAA3;
  box-shadow: 0 0 0 3px rgba(160, 186, 163, 0.2);
}

.chip-option {
  cursor: pointer;
  border: 1.5px solid #ddd;
  border-radius: 20px;
  padding: 0.35rem 0.9rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: #555;
  transition: all 0.2s;
  user-select: none;
}
.chip-option:hover { border-color: #A0BAA3; color: #86A78A; }
.chip-option.active { border-color: #86A78A; background-color: #86A78A; color: white; }

.invest-option {
  cursor: pointer;
  border: 1.5px solid #ddd;
  border-radius: 10px;
  transition: all 0.2s;
}
.invest-option:hover { border-color: #A0BAA3; background-color: #f5faf5; }
.invest-option.active { border-color: #86A78A; background-color: #eaf2ea; }
.invest-label { pointer-events: none; }

.unit-text {
  background-color: #f5f5f0;
  border-color: #ddd;
  color: #888;
  font-size: 0.85rem;
}

.period-badge {
  font-size: 0.85rem;
  font-weight: 700;
  color: #86A78A;
}

.period-slider {
  -webkit-appearance: none;
  appearance: none;
  height: 6px;
  border-radius: 3px;
  background: linear-gradient(
    to right,
    #86A78A 0%,
    #86A78A calc((var(--val, 1) - 1) / 35 * 100%),
    #ddd calc((var(--val, 1) - 1) / 35 * 100%),
    #ddd 100%
  );
  outline: none;
  cursor: pointer;
}
.period-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #86A78A;
  border: 3px solid white;
  box-shadow: 0 1px 6px rgba(0,0,0,0.2);
  cursor: pointer;
  transition: transform 0.1s;
}
.period-slider::-webkit-slider-thumb:hover { transform: scale(1.15); }
.period-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #86A78A;
  border: 3px solid white;
}

.slider-tick {
  font-size: 0.72rem;
  color: #aaa;
}

.btn-primary-custom {
  background-color: #86A78A;
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  transition: background-color 0.2s;
}
.btn-primary-custom:hover:not(:disabled) { background-color: #749478; color: white; }
.btn-primary-custom:disabled { background-color: #A0BAA3; color: white; }

.btn-skip {
  background-color: transparent;
  border: 1.5px solid #A0BAA3;
  border-radius: 8px;
  color: #86A78A;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-skip:hover { background-color: #f0f5f0; }
</style>
