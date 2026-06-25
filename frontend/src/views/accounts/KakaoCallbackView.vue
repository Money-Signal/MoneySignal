<template>
  <div class="callback-wrapper">
    <p class="text-muted">카카오 로그인 처리 중...</p>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useAlert } from '@/composables/useAlert'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const { successConfetti } = useAlert()

onMounted(async () => {
  const access = route.query.access
  const refresh = route.query.refresh
  const isNew = route.query.is_new === 'true'

  if (access && refresh) {
    authStore.loginWithKakao(access, refresh)
    await authStore.fetchProfile()
    await successConfetti(`${authStore.user?.nickname}님 환영합니다! 🎉`, '로그인 성공')
    router.push(isNew ? '/profile/setup' : '/')
  } else {
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
