<template>
  <div class="login-wrapper">
    <div class="login-container">

      <!-- 브랜드 -->
      <div class="text-center mb-4">
        <h1 class="brand-title">MoneySignal</h1>
        <p class="text-muted small">나만의 금융 상품 추천 서비스</p>
      </div>

      <div class="login-card">
        <h4 class="fw-bold mb-4">로그인</h4>

        <form @submit.prevent="handleLogin" novalidate>

          <div class="mb-3">
            <label class="form-label fw-semibold">이메일</label>
            <input
              v-model="form.email"
              type="email"
              class="form-control custom-input"
              :class="{ 'is-invalid': errors.email }"
              placeholder="example@email.com"
              autofocus
            />
            <div class="invalid-feedback">{{ errors.email }}</div>
          </div>

          <div class="mb-4">
            <label class="form-label fw-semibold">비밀번호</label>
            <input
              v-model="form.password"
              type="password"
              class="form-control custom-input"
              :class="{ 'is-invalid': errors.password }"
              placeholder="비밀번호를 입력해주세요"
            />
            <div class="invalid-feedback">{{ errors.password }}</div>
          </div>

          <div v-if="serverError" class="alert alert-danger py-2 small">
            {{ serverError }}
          </div>

          <button type="submit" class="btn btn-primary-custom w-100 py-2 mb-3" :disabled="isLoading">
            {{ isLoading ? '로그인 중...' : '로그인' }}
          </button>

          <!-- 소셜 로그인 구분선 -->
          <div class="divider my-3">
            <span class="divider-text">또는</span>
          </div>

          <!-- 카카오 로그인 버튼 -->
          <button type="button" class="btn btn-kakao w-100 py-2 mb-3" @click="loginWithKakao">
            카카오로 로그인
          </button>

          <p class="text-center text-muted small mb-0">
            아직 계정이 없으신가요?
            <RouterLink to="/signup" class="link-custom">회원가입</RouterLink>
          </p>

        </form>
      </div>

    </div>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const isLoading = ref(false)
const serverError = ref('')

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })

// 카카오 인가 URL로 이동 → 카카오 로그인 → 백엔드 콜백 → /oauth/callback
function loginWithKakao() {
  const clientId = import.meta.env.VITE_KAKAO_REST_API_KEY
  const redirectUri = import.meta.env.VITE_KAKAO_REDIRECT_URI
  window.location.href = `https://kauth.kakao.com/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&response_type=code`
}

async function handleLogin() {
  errors.email = ''
  errors.password = ''
  serverError.value = ''
  isLoading.value = true

  try {
    await authStore.login(form)
    router.push('/')
  } catch (err) {
    const data = err.response?.data
    if (data) {
      if (data.email)           errors.email = data.email[0]
      if (data.password)        errors.password = data.password[0]
      // simplejwt는 이메일/비밀번호 불일치 시 detail 필드로 에러 반환
      if (data.detail)          serverError.value = '이메일 또는 비밀번호가 올바르지 않습니다.'
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
.login-wrapper {
  min-height: 100vh;
  background-color: #EBEADD;
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-container {
  width: 100%;
  max-width: 460px;
  padding: 2rem 1rem;
}

.brand-title {
  font-size: 1.8rem;
  font-weight: 800;
  color: #86A78A;
  letter-spacing: -0.5px;
}

.login-card {
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

.link-custom {
  color: #86A78A;
  font-weight: 600;
  text-decoration: none;
}
.link-custom:hover {
  color: #749478;
  text-decoration: underline;
}

.divider {
  display: flex;
  align-items: center;
  text-align: center;
  color: #aaa;
}
.divider::before,
.divider::after {
  content: '';
  flex: 1;
  border-bottom: 1px solid #ddd;
}
.divider-text {
  padding: 0 0.75rem;
  font-size: 0.85rem;
}

.btn-kakao {
  background-color: #FEE500;
  border: none;
  border-radius: 8px;
  color: #3C1E1E;
  font-weight: 600;
  transition: background-color 0.2s;
}
.btn-kakao:hover {
  background-color: #f0d800;
  color: #3C1E1E;
}
</style>
