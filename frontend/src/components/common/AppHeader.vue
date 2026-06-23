<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ref, onMounted, onBeforeUnmount } from 'vue'

const router = useRouter()
const authStore = useAuthStore()

const isVisible = ref(true)
let lastScrollY = 0

const handleScroll = () => {
  const currentScrollY = window.scrollY
  if (currentScrollY < 10) {
    isVisible.value = true
  } else if (currentScrollY > lastScrollY) {
    isVisible.value = false  // 아래로 스크롤 → 숨김
  } else {
    isVisible.value = true   // 위로 스크롤 → 표시
  }
  lastScrollY = currentScrollY
}

onMounted(() => window.addEventListener('scroll', handleScroll))
onBeforeUnmount(() => window.removeEventListener('scroll', handleScroll))

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<template>
  <header class="app-header" :class="{ hidden: !isVisible }">
    <!-- 기존 template 내용 그대로 -->
    <div class="header-inner">
      <RouterLink to="/" class="brand">
        <div class="logo-icon">
          <span></span><span></span><span></span>
        </div>
        <div class="logo-text">
          <span class="money">money</span><span class="signal">signal</span>
        </div>
      </RouterLink>
      <nav class="header-nav">
        <template v-if="authStore.isLoggedIn">
          <span class="nickname">{{ authStore.user?.nickname }}</span>
          <RouterLink to="/mypage" class="btn-mypage">마이페이지</RouterLink>
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
  background: #DDD9CC;
  border-bottom: 0.5px solid #c4bfb0;
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
.money { color: #3B2F26; }
.signal { color: #6A7F5A; }
.header-nav {
  display: flex;
  align-items: center;
  gap: 10px;
}
.nickname {
  font-size: 13px;
  color: #555;
  font-weight: 500;
}
.btn-mypage {
  padding: 6px 14px;
  border-radius: 20px;
  border: 1.5px solid #6A7F5A;
  background: transparent;
  color: #6A7F5A;
  font-size: 13px;
  text-decoration: none;
  cursor: pointer;
}
.btn-logout {
  font-size: 13px;
  color: #999;
  background: none;
  border: none;
  cursor: pointer;
}
.btn-logout:hover { color: #6A7F5A; }
.btn-signup {
  padding: 6px 16px;
  border-radius: 20px;
  border: none;
  background: #6A7F5A;
  color: #fff;
  font-size: 13px;
  text-decoration: none;
  font-weight: 600;
}
</style>