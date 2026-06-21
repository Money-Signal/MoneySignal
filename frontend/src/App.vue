<script setup>
import { computed } from 'vue'
import { useRoute, RouterView } from 'vue-router'
import AppHeader from '@/components/common/AppHeader.vue'

const route = useRoute()

// 헤더를 숨길 페이지 목록
const hideHeaderRoutes = ['login', 'signup']
const showHeader = computed(() => !hideHeaderRoutes.includes(route.name))
</script>

<template>
  <AppHeader v-if="showHeader" />
  <RouterView />
</template>
