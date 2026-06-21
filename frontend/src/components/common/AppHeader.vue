<template>
  <header class="app-header">
    <div class="header-inner">

      <!-- 로고 -->
      <RouterLink to="/" class="brand">MoneySignal</RouterLink>

      <!-- 우측 메뉴 -->
      <nav class="header-nav">
        <template v-if="authStore.isLoggedIn">
          <span class="nickname">{{ authStore.user?.nickname }}</span>
          <RouterLink to="/mypage" class="nav-link">마이페이지</RouterLink>
          <button class="btn-logout" @click="handleLogout">로그아웃</button>
        </template>
        <template v-else>
          <RouterLink to="/login"  class="nav-link">로그인</RouterLink>
          <RouterLink to="/signup" class="btn-signup">회원가입</RouterLink>
        </template>
      </nav>

    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

async function handleLogout() {
  await authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-header {
  background-color: white;
  border-bottom: 1px solid #e8e4d8;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1.5rem;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  font-size: 1.2rem;
  font-weight: 800;
  color: #86A78A;
  text-decoration: none;
  letter-spacing: -0.5px;
}

.header-nav {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nickname {
  font-size: 0.9rem;
  color: #555;
  font-weight: 500;
}

.nav-link {
  font-size: 0.9rem;
  color: #555;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
}
.nav-link:hover {
  color: #86A78A;
}

.btn-logout {
  font-size: 0.85rem;
  color: #999;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}
.btn-logout:hover {
  color: #86A78A;
}

.btn-signup {
  font-size: 0.85rem;
  background-color: #86A78A;
  color: white;
  text-decoration: none;
  padding: 0.4rem 1rem;
  border-radius: 20px;
  font-weight: 600;
  transition: background-color 0.2s;
}
.btn-signup:hover {
  background-color: #749478;
}
</style>
