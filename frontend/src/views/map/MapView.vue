<template>
  <div class="map-page-wrapper">
    <div class="side-panel">
      <BankList :banks="searchedBanks" @search-result="onSearchResult" @select-bank="onSelectBank" />
    </div>
    
    <div class="map-panel">
      <BankMap :banks="searchedBanks" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import BankMap from '@/components/map/BankMap.vue'
import BankList from '@/components/map/BankList.vue'

const searchedBanks = ref([])

const onSearchResult = (banks) => {
  searchedBanks.value = banks
}

const onSelectBank = (bank) => {
  // 추후 중심좌표 이동 등 연결 가능
}
</script>

<style scoped>
/* 🚀 뷰포트 전체 높이에 맞추어 화면을 가두는 핵심 코드 */
.map-page-wrapper {
  display: flex;
  width: 100%;
  /* 네비게이션 바(헤더) 높이를 고려하여 전체 화면 높이를 완벽하게 등분합니다. */
  height: calc(100vh - 64px); 
  overflow: hidden; /* 페이지 바깥에 쓸데없는 스크롤바가 생기는 현상을 완전 차단 */
  background-color: #ffffff;
}

.side-panel {
  width: 40%; /* 40% ~ 50% 사이 원하시는 만큼 조절하세요! */
  height: 100%; /* 부모 높이를 고스란히 물려받음 */
  display: flex;
  flex-direction: column;
}

.map-panel {
  width: 60%;
  height: 100%;
}

/* 📱 반응형 설정 (화면이 작아질 때 아래로 자연스럽게 배치) */
@media (max-width: 1024px) {
  .map-page-wrapper {
    flex-direction: column;
    height: auto;
    overflow: visible;
  }

  .side-panel {
    width: 100%;
    height: 450px; /* 모바일 리스트 높이 제한 */
    order: 2;
  }

  .map-panel {
    width: 100%;
    height: 400px; /* 모바일 지도 높이 제한 */
    order: 1;
  }
}
</style>