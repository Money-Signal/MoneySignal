<template>
  <div class="callback-wrapper">
    <p class="text-muted">카카오 로그인 처리 중...</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

onMounted(() => {
  // URL 쿼리 파라미터에서 JWT 토큰 및 신규 유저 여부 추출
  const access = route.query.access
  const refresh = route.query.refresh
  const isNew = route.query.is_new === 'true'

  if (access && refresh) {
    authStore.loginWithKakao(access, refresh)
    // 처음 로그인한 유저는 프로필 설정 페이지로, 기존 유저는 홈으로 이동
    router.push(isNew ? '/profile/setup' : '/')
  } else {
    // 토큰이 없으면 로그인 페이지로 이동
    router.push('/login')
  }
})
</script>

<style scoped>
.callback-wrapper {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
