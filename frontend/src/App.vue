<template>
  <AppHeader />
  <div class="app-layout">
    <SideNav />
    <main class="app-main">
      <RouterView />
      <AppFooter />
    </main>
  </div>
</template>

<script setup>
import AppHeader from '@/components/common/AppHeader.vue'
import SideNav from '@/components/common/SideNav.vue'
import AppFooter from '@/components/common/AppFooter.vue'
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #F8F7F2; font-family: -apple-system, sans-serif; }
.app-layout {
  display: flex;
  min-height: calc(100vh - 56px);
}
.app-main {
  flex: 1;
  overflow-x: hidden;  
}
</style>