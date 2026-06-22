<template>
  <div class="signup-wrapper">
    <div class="signup-container">

      <!-- 브랜드 -->
      <div class="text-center mb-4">
        <h1 class="brand-title">MoneySignal</h1>
        <p class="text-muted small">나만의 금융 상품 추천 서비스</p>
      </div>

      <div class="signup-card">

        <!-- 단계 인디케이터 -->
        <div class="step-indicator mb-4">
          <div class="step" :class="{ active: step === 1, done: step > 1 }">
            <span class="step-num">{{ step > 1 ? '✓' : '1' }}</span>
            <span class="step-label">기본 정보</span>
          </div>
          <div class="step-line" :class="{ done: step > 1 }"></div>
          <div class="step" :class="{ active: step === 2 }">
            <span class="step-num">2</span>
            <span class="step-label">금융 정보</span>
          </div>
        </div>

        <!-- STEP 1: 기본 정보 -->
        <form v-if="step === 1" @submit.prevent="goToStep2" novalidate>

          <div class="mb-3">
            <label class="form-label fw-semibold">이메일 <span class="text-danger">*</span></label>
            <input
              v-model="form.email"
              type="email"
              class="form-control custom-input"
              :class="{ 'is-invalid': errors.email }"
              placeholder="example@email.com"
            />
            <div class="invalid-feedback">{{ errors.email }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold">비밀번호 <span class="text-danger">*</span></label>
            <input
              v-model="form.password"
              type="password"
              class="form-control custom-input"
              :class="{ 'is-invalid': errors.password }"
              placeholder="8자 이상 입력해주세요"
            />
            <div class="invalid-feedback">{{ errors.password }}</div>
          </div>

          <div class="mb-3">
            <label class="form-label fw-semibold">비밀번호 확인 <span class="text-danger">*</span></label>
            <input
              v-model="form.password_confirm"
              type="password"
              class="form-control custom-input"
              :class="{ 'is-invalid': errors.password_confirm }"
              placeholder="비밀번호를 다시 입력해주세요"
            />
            <div class="invalid-feedback">{{ errors.password_confirm }}</div>
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold">닉네임 <span class="text-danger">*</span></label>
            <input
              v-model="form.nickname"
              type="text"
              class="form-control custom-input"
              :class="{ 'is-invalid': errors.nickname }"
              placeholder="닉네임을 입력해주세요"
            />
            <div class="invalid-feedback">{{ errors.nickname }}</div>
          </div>

          <button type="submit" class="btn btn-primary-custom w-100 py-2">다음 →</button>

          <p class="text-center text-muted small mt-3 mb-0">
            이미 계정이 있으신가요?
            <RouterLink to="/login" class="link-custom">로그인</RouterLink>
          </p>
        </form>

        <!-- STEP 2: 금융 정보 (선택) -->
        <form v-else @submit.prevent="handleSignup">

          <!-- 연령대 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">연령대</label>
            <div class="d-flex flex-wrap gap-2">
              <label
                v-for="opt in ageOptions"
                :key="opt"
                class="chip-option"
                :class="{ active: form.age_group === opt }"
              >
                <input type="radio" class="d-none" :value="opt" v-model="form.age_group" />
                {{ opt }}
              </label>
            </div>
          </div>

          <!-- 월 저축 가능 금액 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">월 저축 가능 금액</label>
            <div class="d-flex flex-wrap gap-2">
              <label
                v-for="opt in savingOptions"
                :key="opt.label"
                class="chip-option"
                :class="{ active: form.monthly_saving === opt.value }"
              >
                <input type="radio" class="d-none" :value="opt.value" v-model="form.monthly_saving" />
                {{ opt.label }}
              </label>
            </div>
          </div>

          <!-- 선호 상품 유형 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">관심 상품</label>
            <div class="d-flex gap-2">
              <label
                v-for="opt in productTypeOptions"
                :key="opt.value"
                class="invest-option flex-fill text-center"
                :class="{ active: form.preferred_product_type === opt.value }"
              >
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
              <label
                v-for="opt in investmentOptions"
                :key="opt.value"
                class="invest-option flex-fill text-center"
                :class="{ active: form.investment_type === opt.value }"
              >
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
            <input
              v-model="form.financial_goal"
              type="text"
              class="form-control custom-input"
              placeholder="예) 내 집 마련, 노후 준비, 여행 자금"
            />
          </div>

          <!-- 목표 금액 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">목표 금액</label>
            <div class="input-group">
              <input
                v-model="targetAmountInput"
                type="text"
                inputmode="numeric"
                class="form-control custom-input"
                placeholder="예) 5,000"
                @input="onTargetAmountInput"
              />
              <span class="input-group-text unit-text">만원</span>
            </div>
          </div>

          <!-- 투자 기간 -->
          <div class="mb-4">
            <label class="form-label fw-semibold d-flex justify-content-between">
              투자 기간
              <span class="period-badge">
                {{ form.investment_period ? `${form.investment_period}개월` : '선택 안 함' }}
              </span>
            </label>
            <input
              type="range"
              class="period-slider w-100"
              min="1"
              max="36"
              step="1"
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
            {{ isLoading ? '처리 중...' : '가입 완료' }}
          </button>
          <button type="button" class="btn btn-skip w-100 py-2" @click="handleSignup(true)">
            건너뛰기
          </button>

          <button type="button" class="btn btn-link text-muted small mt-2 w-100" @click="step = 1">
            ← 이전으로
          </button>

        </form>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const step = ref(1)
const isLoading = ref(false)
const serverError = ref('')
const targetAmountInput = ref('')

const ageOptions = ['10대', '20대', '30대', '40대', '50대 이상']

const savingOptions = [
  { label: '10만원 미만',  value: 5 },
  { label: '10~30만원',   value: 20 },
  { label: '30~50만원',   value: 40 },
  { label: '50~100만원',  value: 75 },
  { label: '100~200만원', value: 150 },
  { label: '200만원 이상', value: 200 },
]

const productTypeOptions = [
  { value: 'DEPOSIT', label: '예금',    emoji: '🏦', desc: '목돈 한 번에 납입' },
  { value: 'SAVING',  label: '적금',    emoji: '🪙', desc: '매달 꾸준히 납입' },
  { value: 'BOTH',    label: '상관없음', emoji: '✨', desc: '둘 다 추천받기' },
]

const investmentOptions = [
  { value: 'CONSERVATIVE', label: '안정형', emoji: '🛡️', desc: '원금 보호 우선' },
  { value: 'MODERATE',     label: '중립형', emoji: '⚖️', desc: '균형 추구' },
  { value: 'AGGRESSIVE',   label: '공격형', emoji: '🚀', desc: '수익 극대화' },
]


const form = reactive({
  email: '',
  password: '',
  password_confirm: '',
  nickname: '',
  age_group: '',
  monthly_saving: null,
  investment_type: '',
  preferred_product_type: '',
  financial_goal: '',
  target_amount: null,
  investment_period: null,
})

const errors = reactive({
  email: '',
  password: '',
  password_confirm: '',
  nickname: '',
})

// 목표 금액 입력 시 숫자만 허용
function onTargetAmountInput(e) {
  const raw = e.target.value.replace(/[^0-9]/g, '')
  form.target_amount = raw ? Number(raw) : null
  targetAmountInput.value = raw ? Number(raw).toLocaleString() : ''
}

function clearStep1Errors() {
  Object.keys(errors).forEach((key) => (errors[key] = ''))
}

// 1단계 클라이언트 검증 후 2단계로 이동
function goToStep2() {
  clearStep1Errors()
  let hasError = false

  if (!form.email) {
    errors.email = '이메일을 입력해주세요.'; hasError = true
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = '올바른 이메일 형식이 아닙니다.'; hasError = true
  }

  if (!form.password) {
    errors.password = '비밀번호를 입력해주세요.'; hasError = true
  } else if (form.password.length < 8) {
    errors.password = '비밀번호는 8자 이상이어야 합니다.'; hasError = true
  }

  if (form.password !== form.password_confirm) {
    errors.password_confirm = '비밀번호가 일치하지 않습니다.'; hasError = true
  }

  if (!form.nickname) { errors.nickname = '닉네임을 입력해주세요.'; hasError = true }

  if (!hasError) step.value = 2
}

function buildPayload(skip = false) {
  const payload = {
    email: form.email,
    password: form.password,
    password_confirm: form.password_confirm,
    nickname: form.nickname,
  }
  if (!skip) {
    if (form.age_group)              payload.age_group = form.age_group
    if (form.monthly_saving)         payload.monthly_saving = form.monthly_saving
    if (form.investment_type)        payload.investment_type = form.investment_type
    if (form.preferred_product_type) payload.preferred_product_type = form.preferred_product_type
    if (form.financial_goal)         payload.financial_goal = form.financial_goal
    if (form.target_amount)          payload.target_amount = form.target_amount
    if (form.investment_period)      payload.investment_period = form.investment_period
  }
  return payload
}

async function handleSignup(skip = false) {
  serverError.value = ''
  isLoading.value = true
  try {
    await authStore.signup(buildPayload(skip === true))
    alert('회원가입이 완료되었습니다. 로그인 해주세요.')
    router.push('/login')
  } catch (err) {
    const data = err.response?.data
    if (data) {
      // 서버에서 1단계 필드 에러가 오면 1단계로 되돌아감
      if (data.email || data.password || data.password_confirm || data.nickname) {
        if (data.email)            errors.email = data.email[0]
        if (data.password)         errors.password = data.password[0]
        if (data.password_confirm) errors.password_confirm = data.password_confirm[0]
        if (data.nickname)         errors.nickname = data.nickname[0]
        step.value = 1
      }
      if (data.non_field_errors) serverError.value = data.non_field_errors[0]
    } else {
      serverError.value = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
    }
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.signup-wrapper {
  min-height: 100vh;
  background-color: #EBEADD;
  display: flex;
  align-items: center;
  justify-content: center;
}

.signup-container {
  width: 100%;
  max-width: 520px;
  padding: 2rem 1rem;
}

.brand-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #86A78A;
  letter-spacing: -0.5px;
}

.signup-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  padding: 2rem;
}

/* 단계 인디케이터 */
.step-indicator {
  display: flex;
  align-items: center;
}
.step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}
.step-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  border: 2px solid #ddd;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  color: #bbb;
  transition: all 0.3s;
}
.step.active .step-num {
  border-color: #86A78A;
  background-color: #86A78A;
  color: white;
}
.step.done .step-num {
  border-color: #86A78A;
  background-color: #86A78A;
  color: white;
}
.step-label {
  font-size: 0.72rem;
  color: #bbb;
  font-weight: 500;
  white-space: nowrap;
}
.step.active .step-label,
.step.done .step-label {
  color: #86A78A;
}
.step-line {
  flex: 1;
  height: 2px;
  background-color: #ddd;
  margin: 0 8px;
  margin-bottom: 18px;
  transition: background-color 0.3s;
}
.step-line.done {
  background-color: #86A78A;
}

/* 인풋 */
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

/* 칩 선택 버튼 */
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
.chip-option:hover {
  border-color: #A0BAA3;
  color: #86A78A;
}
.chip-option.active {
  border-color: #86A78A;
  background-color: #86A78A;
  color: white;
}

/* 투자 성향 카드 */
.invest-option {
  cursor: pointer;
  border: 1.5px solid #ddd;
  border-radius: 10px;
  transition: all 0.2s;
}
.invest-option:hover {
  border-color: #A0BAA3;
  background-color: #f5faf5;
}
.invest-option.active {
  border-color: #86A78A;
  background-color: #eaf2ea;
}
.invest-label { pointer-events: none; }

/* 단위 */
.unit-text {
  background-color: #f5f5f0;
  border-color: #ddd;
  color: #888;
  font-size: 0.85rem;
}

/* 버튼 */
.btn-primary-custom {
  background-color: #86A78A;
  border: none;
  border-radius: 8px;
  color: white;
  font-weight: 600;
  transition: background-color 0.2s;
}
.btn-primary-custom:hover:not(:disabled) {
  background-color: #749478;
  color: white;
}
.btn-primary-custom:disabled {
  background-color: #A0BAA3;
  color: white;
}

.btn-skip {
  background-color: transparent;
  border: 1.5px solid #A0BAA3;
  border-radius: 8px;
  color: #86A78A;
  font-weight: 600;
  transition: all 0.2s;
}
.btn-skip:hover {
  background-color: #f0f5f0;
}

/* 투자 기간 슬라이더 */
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
.period-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
}
.period-slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #86A78A;
  border: 3px solid white;
  box-shadow: 0 1px 6px rgba(0,0,0,0.2);
  cursor: pointer;
}

.slider-tick {
  font-size: 0.72rem;
  color: #aaa;
}

.link-custom {
  color: #86A78A;
  font-weight: 600;
  text-decoration: none;
}
.link-custom:hover {
  color: #749478;
  text-decoration: underline;
}
</style>
