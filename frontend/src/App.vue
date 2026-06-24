<template>
  <div class="app-wrapper">
    <AppHeader />
    
    <main class="content">
      <RouterView />
    </main>
    
    <AppFooter />
  </div>
</template>

<script setup>
import AppHeader from '@/components/common/AppHeader.vue'
import AppFooter from '@/components/common/AppFooter.vue'
// SideNav는 제거되었습니다.
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #F8F7F2; font-family: -apple-system, sans-serif; }

.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh; /* 화면 전체 높이 보장 */
}

.content {
  flex: 1; /* 헤더와 푸터 사이의 공간을 가득 채움 */
  width: 100%;
}
</style>