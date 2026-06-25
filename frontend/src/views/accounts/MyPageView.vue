<template>
  <div class="mypage-wrapper">
    <div class="mypage-container">

      <PageHeader title="마이페이지" description="내 프로필과 관심 상품을 관리하고 금융 정보를 설정하세요." />

      <div class="mypage-layout">
        <!-- 왼쪽: 프로필 + 서비스 메뉴 -->
        <div class="mypage-left">

      <!-- 프로필 카드 -->
      <div class="mypage-card profile-card mb-3">
        <div class="profile-image-wrapper">
          <img :src="profileImageUrl" class="profile-image" alt="프로필 사진" />
          <label v-if="isEditing" class="profile-image-edit">
            <input type="file" accept="image/*" @change="onImageChange" hidden />
            <i class="bi bi-camera-fill"></i>
          </label>
        </div>

        <template v-if="!isEditing">
          <h4 class="fw-bold mt-3 mb-1">{{ user.nickname }}</h4>
          <span class="badge-provider mb-1">
            <i :class="user.provider === 'KAKAO' ? 'bi bi-chat-fill' : 'bi bi-person-fill'"></i>
            {{ user.provider === 'KAKAO' ? '카카오 로그인' : '일반 로그인' }}
          </span>
          <p class="text-muted small mb-2">{{ user.email }}</p>
          <p class="join-date">가입일 {{ formatDate(user.created_at) }}</p>
        </template>
        <template v-else>
          <input v-model="form.nickname" class="form-control mt-3 text-center nickname-input" placeholder="닉네임" />
        </template>

        <div v-if="!isEditing" class="mt-3">
          <button class="btn btn-primary-custom" @click="startEdit">
            <i class="bi bi-pencil-fill me-1"></i>정보 수정
          </button>
        </div>
      </div>

      <!-- 메뉴 섹션 (왼쪽 하단) -->
      <div class="mypage-card desktop-menu mb-3" :class="{ 'menu-dimmed': isEditing }">
        <div class="menu-list">
          <button class="menu-item" disabled>
            <div class="menu-left">
              <span class="menu-icon-wrap bg-purple"><i class="bi bi-headset"></i></span>
              <span class="menu-text">고객 지원</span>
            </div>
            <i class="bi bi-chevron-right menu-arrow"></i>
          </button>
          <button class="menu-item" @click="authStore.logout().then(() => router.push('/login'))">
            <div class="menu-left">
              <span class="menu-icon-wrap bg-gray"><i class="bi bi-box-arrow-right"></i></span>
              <span class="menu-text">로그아웃</span>
            </div>
            <i class="bi bi-chevron-right menu-arrow"></i>
          </button>
          <button class="menu-item menu-item-danger" @click="confirmDelete">
            <div class="menu-left">
              <span class="menu-icon-wrap bg-red"><i class="bi bi-person-x-fill"></i></span>
              <span class="menu-text">회원탈퇴</span>
            </div>
            <i class="bi bi-chevron-right menu-arrow"></i>
          </button>
        </div>
      </div>

        </div><!-- /.mypage-left -->

        <!-- 오른쪽: 금융 정보 -->
        <div class="mypage-right">

      <!-- 금융 정보 -->
      <div class="mypage-card mb-3">
        <p class="section-title"><i class="bi bi-bar-chart-fill me-2"></i>금융 정보</p>

        <template v-if="!isEditing">
          <div class="finance-grid">
            <div class="finance-item">
              <i class="bi bi-person-badge finance-icon"></i>
              <span class="finance-label">연령대</span>
              <span class="finance-value" :class="{ unset: !user.age_group }">{{ user.age_group || '미설정' }}</span>
            </div>
            <div class="finance-item">
              <i class="bi bi-piggy-bank finance-icon"></i>
              <span class="finance-label">월 저축액</span>
              <span class="finance-value" :class="{ unset: !user.monthly_saving }">{{ user.monthly_saving ? user.monthly_saving + '만원' : '미설정' }}</span>
            </div>
            <div class="finance-item">
              <i class="bi bi-graph-up-arrow finance-icon"></i>
              <span class="finance-label">투자 성향</span>
              <span class="finance-value" :class="{ unset: !user.investment_type }">{{ investmentTypeLabel }}</span>
            </div>
            <div class="finance-item">
              <i class="bi bi-bank finance-icon"></i>
              <span class="finance-label">선호 상품</span>
              <span class="finance-value" :class="{ unset: !user.preferred_product_type }">{{ preferredProductLabel }}</span>
            </div>
            <div class="finance-item">
              <i class="bi bi-bullseye finance-icon"></i>
              <span class="finance-label">금융 목표</span>
              <span class="finance-value" :class="{ unset: !user.financial_goal }">{{ financialGoalLabel }}</span>
            </div>
            <div class="finance-item">
              <i class="bi bi-briefcase finance-icon"></i>
              <span class="finance-label">직업</span>
              <span class="finance-value" :class="{ unset: !user.occupation }">{{ occupationLabel }}</span>
            </div>
            <div class="finance-item finance-item-full">
              <i class="bi bi-calendar-check finance-icon"></i>
              <span class="finance-label">투자 기간</span>
              <span class="finance-value" :class="{ unset: !user.investment_period }">{{ user.investment_period ? user.investment_period + '개월' : '미설정' }}</span>
            </div>
          </div>
        </template>

        <template v-else>
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
            <label class="form-label fw-semibold">금융 목표 <span class="text-muted small fw-normal">(복수 선택 가능)</span></label>
            <DropdownSelect
              v-model="form.financial_goal"
              :options="financialGoalOptions"
              :multiple="true"
              placeholder="금융 목표를 선택하세요"
            />
          </div>

          <!-- 직업 -->
          <div class="mb-4">
            <label class="form-label fw-semibold">직업</label>
            <DropdownSelect
              v-model="form.occupation"
              :options="occupationOptions"
              placeholder="직업을 선택하세요"
            />
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
        </template>
      </div>

      <!-- 관심 상품 -->
      <div v-if="!isEditing" class="mypage-card mb-3">
        <p class="section-title"><i class="bi bi-heart-fill me-2" style="color:#c0756a" />관심 상품</p>

        <LoadingSpinner v-if="productStore.isLoading" />

        <div v-else-if="productStore.likedProducts.length === 0" class="liked-empty">
          <i class="bi bi-heart" />
          <p>저장한 상품이 없어요</p>
        </div>

        <div v-else class="liked-scroll">
          <div
            v-for="p in productStore.likedProducts"
            :key="p.id"
            class="liked-card"
            @click="router.push({ name: 'productDetail', params: { id: p.product.id } })"
          >
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span class="liked-bank-chip">{{ p.product.kor_co_nm }}</span>
              <button class="liked-heart-btn" @click.stop="onUnlike(p.product.id)">
                <i class="bi bi-heart-fill" />
              </button>
            </div>
            <p class="liked-card-name">{{ p.product.fin_prdt_nm }}</p>
            <p class="liked-card-member">{{ p.product.join_member || '-' }}</p>
            <div class="liked-card-rate mt-auto">
              <span class="liked-rate-value">{{ p.product.max_intr_rate2 != null ? p.product.max_intr_rate2 + '%' : '-' }}</span>
              <span class="liked-rate-label">최고금리</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 비밀번호 변경 (일반 로그인 유저, 수정 모드일 때만) -->
      <div v-if="user.provider === 'LOCAL' && isEditing" class="mypage-card mb-3">
        <p class="section-title"><i class="bi bi-lock-fill me-2"></i>비밀번호 변경</p>
        <div class="mb-2">
          <label class="form-label">새 비밀번호</label>
          <input v-model="form.password" type="password" class="form-control" placeholder="변경할 비밀번호 입력" />
        </div>
        <div class="mb-2">
          <label class="form-label">새 비밀번호 확인</label>
          <input v-model="form.password_confirm" type="password" class="form-control" placeholder="비밀번호 확인" />
        </div>
      </div>

      <!-- 메뉴 섹션 (모바일에서만 표시) -->
      <div class="mypage-card mobile-menu mb-3" :class="{ 'menu-dimmed': isEditing }">
        <div class="menu-list">
          <button class="menu-item" disabled>
            <div class="menu-left">
              <span class="menu-icon-wrap bg-purple"><i class="bi bi-headset"></i></span>
              <span class="menu-text">고객 지원</span>
            </div>
            <i class="bi bi-chevron-right menu-arrow"></i>
          </button>
          <button class="menu-item" @click="authStore.logout().then(() => router.push('/login'))">
            <div class="menu-left">
              <span class="menu-icon-wrap bg-gray"><i class="bi bi-box-arrow-right"></i></span>
              <span class="menu-text">로그아웃</span>
            </div>
            <i class="bi bi-chevron-right menu-arrow"></i>
          </button>
          <button class="menu-item menu-item-danger" @click="confirmDelete">
            <div class="menu-left">
              <span class="menu-icon-wrap bg-red"><i class="bi bi-person-x-fill"></i></span>
              <span class="menu-text">회원탈퇴</span>
            </div>
            <i class="bi bi-chevron-right menu-arrow"></i>
          </button>
        </div>
      </div>

      <!-- 저장/취소 버튼 (수정 모드) -->
      <div v-if="isEditing" class="save-bar">
        <div v-if="saveError" class="alert alert-danger py-2 small mb-2">{{ saveError }}</div>
        <div class="d-flex gap-2 justify-content-end">
          <button class="btn btn-outline-secondary" @click="cancelEdit">취소</button>
          <button class="btn btn-primary-custom btn-save" :disabled="isSaving" @click="saveProfile">
            <i class="bi bi-check-lg me-1"></i>{{ isSaving ? '저장 중...' : '저장하기' }}
          </button>
        </div>
      </div>

        </div><!-- /.mypage-right -->
      </div><!-- /.mypage-layout -->

    </div>
  </div>
</template>

<script setup>
import 'bootstrap-icons/font/bootstrap-icons.css'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useProductStore } from '@/stores/product'
import defaultProfileImg from '@/assets/default-profile.svg'
import DropdownSelect from '@/components/common/DropdownSelect.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import { useAlert } from '@/composables/useAlert'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const {alert, confirm} = useAlert()

const router = useRouter()
const authStore = useAuthStore()
const productStore = useProductStore()
const user = computed(() => authStore.user)

const isEditing = ref(false)
const isSaving = ref(false)
const saveError = ref('')
const imageFile = ref(null)
const form = ref({})

const ageOptions = ['10대', '20대', '30대', '40대', '50대 이상']

const financialGoalOptions = [
  { value: 'HOME',       label: '내집마련',   emoji: '🏠' },
  { value: 'WEDDING',    label: '결혼자금',   emoji: '💒' },
  { value: 'RETIREMENT', label: '노후준비',   emoji: '👴' },
  { value: 'TRAVEL',     label: '여행/여가',  emoji: '✈️' },
  { value: 'EDUCATION',  label: '자녀교육',   emoji: '🎓' },
  { value: 'EMERGENCY',  label: '비상금 마련', emoji: '🛡️' },
  { value: 'ETC',        label: '기타',       emoji: '📌' },
]

const occupationOptions = [
  { value: 'EMPLOYEE',    label: '직장인',  emoji: '💼' },
  { value: 'SELF_EMPLOY', label: '자영업자', emoji: '🏪' },
  { value: 'STUDENT',     label: '학생',    emoji: '📚' },
  { value: 'HOUSEWIFE',   label: '주부',    emoji: '🏡' },
  { value: 'FREELANCER',  label: '프리랜서', emoji: '💻' },
  { value: 'ETC',         label: '기타',    emoji: '👤' },
]

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

const BACKEND_URL = 'http://127.0.0.1:8000'

// 프로필 사진 URL — 로컬 미리보기 → 백엔드 미디어 경로 → 기본 이미지 순으로 적용
const profileImageUrl = computed(() => {
  if (imageFile.value) return URL.createObjectURL(imageFile.value)
  if (user.value?.profile_image) {
    const img = user.value.profile_image
    return img.startsWith('http') ? img : `${BACKEND_URL}${img}`
  }
  return defaultProfileImg
})

const investmentTypeLabel = computed(() => {
  const map = { CONSERVATIVE: '안정형', MODERATE: '중립형', AGGRESSIVE: '공격형' }
  return map[user.value?.investment_type] || '미설정'
})

const preferredProductLabel = computed(() => {
  const map = { DEPOSIT: '예금', SAVING: '적금', BOTH: '상관없음' }
  return map[user.value?.preferred_product_type] || '미설정'
})

const financialGoalLabel = computed(() => {
  const goals = user.value?.financial_goal
  if (!Array.isArray(goals) || !goals.length) return '미설정'
  return goals
    .map(v => financialGoalOptions.find(o => o.value === v)?.label)
    .filter(Boolean)
    .join(', ')
})

const occupationLabel = computed(() => {
  const opt = occupationOptions.find(o => o.value === user.value?.occupation)
  return opt?.label || '미설정'
})

function formatDate(dateStr) {
  if (!dateStr) return ''
  return dateStr.slice(0, 10)
}

function startEdit() {
  form.value = {
    nickname:               user.value.nickname,
    age_group:              user.value.age_group || '',
    monthly_saving:         user.value.monthly_saving || '',
    investment_type:        user.value.investment_type || '',
    preferred_product_type: user.value.preferred_product_type || '',
    financial_goal:         Array.isArray(user.value.financial_goal) ? [...user.value.financial_goal] : [],
    occupation:             user.value.occupation || '',
    investment_period:      user.value.investment_period || '',
    password:               '',
    password_confirm:       '',
  }
  imageFile.value = null
  isEditing.value = true
}

function cancelEdit() {
  isEditing.value = false
  saveError.value = ''
}

function onImageChange(e) {
  imageFile.value = e.target.files[0]
}

async function saveProfile() {
  isSaving.value = true
  saveError.value = ''
  try {
    const formData = new FormData()
    Object.entries(form.value).forEach(([key, value]) => {
      if (value === '' || value === null || value === undefined) return
      if (Array.isArray(value)) formData.append(key, JSON.stringify(value))
      else formData.append(key, value)
    })
    if (imageFile.value) formData.append('profile_image', imageFile.value)
    await authStore.updateProfile(formData)
    productStore.clearRecommendations()  // 프로필 바뀌었으니 다음 방문 시 추천 재검색
    isEditing.value = false
  } catch {
    saveError.value = '저장에 실패했습니다. 다시 시도해주세요.'
  } finally {
    isSaving.value = false
  }
}

async function confirmDelete() {
  const result = await confirm('정말 탈퇴하시겠습니까?', '회원탈퇴', {
    confirmText: '탈퇴',
    cancelText: '취소'
  })
  if (!result) return
  try {
    await authStore.deleteAccount()
    router.push('/login')
  } catch {
    await alert('회원탈퇴에 실패했습니다.', '오류')
  }
}

async function onUnlike(productId) {
  await productStore.likeProduct(productId)
  await productStore.fetchLikedProducts()
}

onMounted(async () => {
  await authStore.fetchProfile()
  await productStore.fetchLikedProducts()
})
</script>

<style scoped>
.mypage-wrapper {
  min-height: 100vh;
  background-color: #f9f8f5;
  padding: 2rem 2rem 4rem;
}

.mypage-container {
  max-width: 560px;
  margin: 0 auto;
}

.page-title {
  font-size: 1.4rem;
  font-weight: 800;
  color: #3a3a3a;
  margin-bottom: 1.2rem;
}

/* 데스크탑 2컬럼 레이아웃 */
.mypage-layout {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.desktop-menu { display: none; }
.mobile-menu  { display: block; }

@media (min-width: 900px) {
  .mypage-container {
    max-width: 1000px;
  }

  .mypage-layout {
    flex-direction: row;
    align-items: flex-start;
    gap: 1.5rem;
  }

  .mypage-left {
    width: 300px;
    flex-shrink: 0;
    align-self: flex-start;
    position: sticky;
    top: 80px;
  }

  .mypage-right {
    flex: 1;
    min-width: 0;
  }

  .desktop-menu {
  display: block;
  padding: 1.2rem 1.4rem;
}
  .mobile-menu  { display: none; }
}

/* 카드 공통 */
.mypage-card {
  background: white;
  border-radius: 20px;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.06);
  padding: 1.8rem;
}

/* 프로필 카드 */
.profile-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2.5rem 1.8rem 1.8rem;
  background: linear-gradient(160deg, #f4f8f4 0%, #ffffff 60%);
}

.profile-image-wrapper {
  position: relative;
}

.profile-image {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid white;
  box-shadow: 0 6px 24px rgba(134, 167, 138, 0.3);
}

.profile-image-edit {
  position: absolute;
  bottom: 4px;
  right: 0;
  background: #86A78A;
  color: white;
  font-size: 0.8rem;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.badge-provider {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background-color: #eef3ee;
  color: #86A78A;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 20px;
}

.join-date {
  font-size: 0.78rem;
  color: #bbb;
  margin-top: 0.5rem;
  margin-bottom: 0;
}

.nickname-input {
  max-width: 200px;
  text-align: center;
  border-radius: 10px;
}

/* 섹션 타이틀 */
.section-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #555;
  margin-bottom: 0.7rem;
  padding-bottom: 0.5rem;
  border-bottom: 1.5px solid #f0f0f0;
  display: flex;
  align-items: center;
}

/* 금융 정보 그리드 */
.finance-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.7rem;
}

.finance-item {
  background: #f8faf8;
  border-radius: 14px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.finance-item-full {
  grid-column: 1 / -1;
  flex-direction: row;
  align-items: center;
  gap: 0.8rem;
}

.finance-icon {
  font-size: 1.2rem;
  color: #86A78A;
}

.finance-label {
  font-size: 0.72rem;
  color: #aaa;
  font-weight: 600;
  letter-spacing: 0.3px;
}

.finance-value {
  font-size: 0.92rem;
  font-weight: 700;
  color: #3a3a3a;
}

.finance-value.unset {
  color: #ccc;
  font-weight: 400;
  font-size: 0.85rem;
}

.finance-item-full .finance-label {
  margin-left: auto;
  margin-right: 0.3rem;
}

/* 메뉴 리스트 */
.menu-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.menu-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: none;
  border: none;
  padding: 0.5rem 0.4rem;
  border-radius: 10px;
  cursor: pointer;
  transition: background-color 0.15s;
  width: 100%;
}

.menu-item:hover:not(:disabled) {
  background-color: #f8f8f8;
}

.menu-item:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.menu-left {
  display: flex;
  align-items: center;
  gap: 0.85rem;
}

.menu-icon-wrap {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.88rem;
  color: white;
}

.bg-blue   { background-color: #5b9cf6; }
.bg-purple { background-color: #a78abf; }
.bg-gray   { background-color: #aaa; }
.bg-red    { background-color: #e07070; }

.menu-text {
  font-size: 0.92rem;
  font-weight: 600;
  color: #3a3a3a;
}

.menu-item-danger .menu-text {
  color: #e07070;
}

.menu-arrow {
  color: #ccc;
  font-size: 0.8rem;
}

/* 버튼 */
.btn-primary-custom {
  background-color: #86A78A;
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 600;
  padding: 0.45rem 1.4rem;
  font-size: 0.9rem;
  transition: background-color 0.2s, transform 0.1s;
}

.btn-primary-custom:hover:not(:disabled) {
  background-color: #749478;
  color: white;
  transform: translateY(-1px);
}

.btn-primary-custom:disabled {
  background-color: #A0BAA3;
  color: white;
}

.btn-outline-secondary {
  border-radius: 10px;
  font-size: 0.9rem;
  padding: 0.45rem 1.4rem;
}

.menu-dimmed {
  display: none;
}

@media (min-width: 900px) {
  .desktop-menu.menu-dimmed {
    display: block;
    opacity: 0.4;
    pointer-events: none;
    user-select: none;
  }
}

.save-bar {
  margin-top: 0.5rem;
}

.btn-save {
  padding: 0.55rem 2rem;
  font-size: 0.95rem;
}

/* 회원가입과 동일한 금융정보 입력 스타일 */
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
  box-shadow: 0 1px 6px rgba(0,0,0,0.2);
}

.slider-tick {
  font-size: 0.72rem;
  color: #aaa;
}

/* ── 관심 상품 ── */
.liked-empty {
  text-align: center;
  padding: 2rem 0;
  color: #ccc;
}
.liked-empty i {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}
.liked-empty p { font-size: 0.88rem; margin: 0; }

.liked-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 4px 2px 8px;
  scrollbar-width: thin;
  scrollbar-color: #c8d9c9 transparent;
}
.liked-scroll::-webkit-scrollbar { height: 4px; }
.liked-scroll::-webkit-scrollbar-thumb { background: #c8d9c9; border-radius: 2px; }

.liked-card {
  flex: 0 0 170px;
  background: #fafaf6;
  border: 1.5px solid #e4e3d4;
  border-radius: 12px;
  padding: 14px;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}
.liked-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(134,167,138,0.15);
  border-color: #A0BAA3;
}

.liked-bank-chip {
  font-size: 0.72rem;
  padding: 2px 8px;
  border-radius: 20px;
  background: #ebebeb;
  color: #4a4a4a;
}

.liked-heart-btn {
  background: none;
  border: none;
  padding: 2px 4px;
  font-size: 0.95rem;
  color: #c0756a;
  cursor: pointer;
  line-height: 1;
  transition: opacity 0.15s;
}
.liked-heart-btn:hover { opacity: 0.6; }

.liked-card-name {
  font-size: 0.82rem;
  font-weight: 600;
  color: #2d2d25;
  margin: 6px 0 4px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

.liked-card-member {
  font-size: 0.75rem;
  color: #a0a090;
  margin: 0;
}

.liked-card-rate {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin-top: 10px;
}

.liked-rate-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: #5a8a5e;
}

.liked-rate-label {
  font-size: 0.72rem;
  color: #a0a090;
}
</style>
