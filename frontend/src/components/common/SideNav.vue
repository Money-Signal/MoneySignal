<template>
  <div class="sidenav-wrap" :class="{ open: isOpen }">
    <div class="sidenav-rail">
      <button class="rail-toggle" @click="isOpen = !isOpen" :class="{ active: isOpen }">
        <i class="bi bi-list"></i>
      </button>
    </div>

    <transition name="slide">
      <div v-if="isOpen" class="sidenav-panel">
        <div class="panel-header">
          <span class="panel-title">메뉴</span>
          <button class="panel-close" @click="isOpen = false">
            <i class="bi bi-x"></i>
          </button>
        </div>
        <nav class="panel-nav">
          <RouterLink
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="panel-item"
            :class="{ active: route.path.startsWith(item.path) }"
            @click="isOpen = false"
          >
            <i :class="item.icon"></i>
            <span>{{ item.label }}</span>
          </RouterLink>
        </nav>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const isOpen = ref(false)
const route = useRoute()

const menuItems = [
  { label: '예·적금 상품', path: '/products', icon: 'bi bi-piggy-bank' },
  { label: '환율', path: '/currency', icon: 'bi bi-currency-exchange' },
  { label: '영상 검색', path: '/video', icon: 'bi bi-play-circle' },
  { label: '주변 은행', path: '/map', icon: 'bi bi-map' },
  { label: '금·은 시세', path: '/exchange', icon: 'bi bi-bar-chart-line' },
]
</script>

<style scoped>
.sidenav-wrap {
  display: flex;
  flex-shrink: 0;
  transition: width 0.25s ease;
}
.sidenav-rail {
  width: 52px;
  min-height: calc(100vh - 56px);
  background: #DDD9CC;
  border-right: 0.5px solid #c4bfb0;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 0;
  flex-shrink: 0;
}
.rail-toggle {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: #6A7F5A;
  border: none;
  color: #fff;
  font-size: 18px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s;
}
.rail-toggle:hover { background: #5a6e4b; }
.rail-toggle.active { background: #3B2F26; }

.sidenav-panel {
  width: 200px;
  min-height: calc(100vh - 56px);
  background: #ECEADD;
  border-right: 0.5px solid #c4bfb0;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 16px 12px;
  border-bottom: 0.5px solid #ddd9cc;
}
.panel-title {
  font-size: 13px;
  font-weight: 600;
  color: #3B2F26;
}
.panel-close {
  background: none;
  border: none;
  font-size: 18px;
  color: #999;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.panel-nav {
  padding: 8px 0;
  display: flex;
  flex-direction: column;
}
.panel-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  font-size: 14px;
  color: #555;
  text-decoration: none;
  transition: background 0.15s;
}
.panel-item i { font-size: 16px; color: #A0BAA3; }
.panel-item:hover { background: #DDD9CC; color: #3B2F26; }
.panel-item.active {
  background: #DDD9CC;
  color: #6A7F5A;
  font-weight: 600;
}
.panel-item.active i { color: #6A7F5A; }

.slide-enter-active,
.slide-leave-active {
  transition: width 0.25s ease, opacity 0.25s ease;
  overflow: hidden;
}
.slide-enter-from,
.slide-leave-to {
  width: 0;
  opacity: 0;
}
.slide-enter-to,
.slide-leave-from {
  width: 200px;
  opacity: 1;
}
</style>