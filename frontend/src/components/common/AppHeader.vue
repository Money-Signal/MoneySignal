<script setup>
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import defaultProfileImg from '@/assets/default-profile.svg'

const BACKEND_URL = import.meta.env.VITE_API_URL

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const isVisible = ref(true)
let lastScrollY = 0

const handleScroll = () => {
  const currentScrollY = window.scrollY
  if (currentScrollY < 10) {
    isVisible.value = true
  } else if (currentScrollY > lastScrollY) {
    isVisible.value = false
  } else {
    isVisible.value = true
  }
  lastScrollY = currentScrollY
}

onMounted(() => window.addEventListener('scroll', handleScroll))
onBeforeUnmount(() => window.removeEventListener('scroll', handleScroll))

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}

const menuItems = [
  { label: '예·적금 상품', path: '/products', icon: 'bi bi-piggy-bank' },
  { label: '환율', path: '/currency', icon: 'bi bi-currency-exchange' },
  { label: '영상 검색', path: '/video', icon: 'bi bi-play-circle' },
  { label: '주변 은행', path: '/map', icon: 'bi bi-map' },
  { label: '금·은 시세', path: '/exchange', icon: 'bi bi-bar-chart-line' },
  { label: '커뮤니티', path: '/community', icon: 'bi bi-people' },
]

const profileImageUrl = computed(() => {
  const img = authStore.user?.profile_image
  if (!img) return defaultProfileImg
  return img.startsWith('http') ? img : `${BACKEND_URL}${img}`
})
</script>

<template>
  <header class="app-header" :class="{ hidden: !isVisible }">
    <div class="header-inner">
      <RouterLink to="/" class="brand">
        <img src="@/assets/logo.png" alt="MoneySignal" class="logo-img" />
      </RouterLink>

      <!-- 추가된 메뉴 -->
      <nav class="main-nav">
        <RouterLink
          v-for="item in menuItems"
          :key="item.path"
          :to="item.path"
          class="nav-item"
          :class="{ active: route.path.startsWith(item.path) }"
        >
          <i :class="item.icon"></i>
          <span>{{ item.label }}</span>
        </RouterLink>
      </nav>

      <nav class="header-nav">
        <template v-if="authStore.isLoggedIn">
          <RouterLink to="/mypage" class="user-profile">
            <img :src="profileImageUrl" alt="프로필" class="profile-avatar" />
            <span class="nickname">{{ authStore.user?.nickname }}</span>
          </RouterLink>
          <button class="btn-logout" @click="handleLogout">로그아웃</button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="btn-mypage">로그인</RouterLink>
          <RouterLink to="/signup" class="btn-signup">회원가입</RouterLink>
        </template>
      </nav>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  background: #5C7050;
  border-bottom: 1px solid #E0D2B0;
  position: sticky;
  top: 0;
  z-index: 100;
  transition: transform 0.3s ease;
}
.app-header.hidden {
  transform: translateY(-100%);
}
.header-inner {
  padding: 0 28px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.brand {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  flex-shrink: 0;
}
.logo-icon {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 20px;
}
.logo-icon span {
  background: #F2C15D;
  border-radius: 3px;
  width: 5px;
  display: block;
}
.logo-icon span:nth-child(1) { height: 9px; }
.logo-icon span:nth-child(2) { height: 14px; }
.logo-icon span:nth-child(3) { height: 20px; }
.logo-text {
  font-size: 17px;
  font-weight: 700;
  letter-spacing: -0.5px;
}
.money { color: #fff; }
.signal { color: #d9e6cf; }

/* 메뉴 */
.main-nav {
  display: flex;
  align-items: center;
  gap: 4px;
  flex: 1;
  justify-content: center;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.nav-item i { font-size: 14px; color: rgba(255, 255, 255, 0.7); }
.nav-item:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}
.nav-item.active {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
  font-weight: 600;
}
.nav-item.active i { color: #fff; }

.header-nav {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.user-profile {
  display: flex;
  align-items: center;
  gap: 7px;
  text-decoration: none;
  padding: 4px 10px 4px 4px;
  border-radius: 20px;
  transition: background 0.15s;
}
.user-profile:hover {
  background: rgba(255, 255, 255, 0.12);
}
.profile-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  border: 1.5px solid rgba(255, 255, 255, 0.6);
  flex-shrink: 0;
}
.nickname {
  font-size: 13px;
  color: #fff;
  font-weight: 600;
}
.btn-mypage {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1.5px solid rgba(255, 255, 255, 0.7);
  background: transparent;
  color: #fff;
  font-size: 13px;
  text-decoration: none;
  cursor: pointer;
}
.btn-logout {
  font-size: 13px;
  color: rgba(255, 255, 255, 0.7);
  background: none;
  border: none;
  cursor: pointer;
}
.btn-logout:hover { color: #fff; }
.btn-signup {
  padding: 6px 16px;
  border-radius: 20px;
  border: none;
  background: #fff;
  color: #5C7050;
  font-size: 13px;
  text-decoration: none;
  font-weight: 600;
}
.btn-signup:hover {
  background: #f1f1f1;
}
.logo-img {
  height: 70px;
  object-fit: contain;
}
</style>