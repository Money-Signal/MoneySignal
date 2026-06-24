<template>
  <div class="app-wrapper">
    <AppHeader />
    
    <main class="content">
      <RouterView />
    </main>
    
    <AppFooter />
    <ChatBot />
  </div>
  <AlertModal/>
</template>

<script setup>
import AppHeader from '@/components/common/AppHeader.vue'
import AppFooter from '@/components/common/AppFooter.vue'
import ChatBot from '@/components/common/ChatBot.vue'
import AlertModal from './components/common/AlertModal.vue';
</script>

<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { background: #f9f8f5; font-family: -apple-system, sans-serif; }

.app-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex: 1;
  width: 100%;
}
</style>
