<template>
  <div class="map-page-wrapper">
    <div class="side-panel">
      <BankList :banks="searchedBanks" @search-result="onSearchResult" @select-bank="onSelectBank" />
    </div>
    
    <div class="map-panel">
      <BankMap ref="bankMapRef" :banks="searchedBanks" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import BankMap from '@/components/map/BankMap.vue'
import BankList from '@/components/map/BankList.vue'

const searchedBanks = ref([])
// 🚀 자식 BankMap 컴포넌트에 접근하기 위한 ref 변수를 선언합니다.
const bankMapRef = ref(null)

const onSearchResult = (banks) => {
  searchedBanks.value = banks
}

// 🚀 BankList에서 카드를 클릭하면 이 함수가 실행됩니다.
const onSelectBank = (bank) => {
  // 자식 컴포넌트인 BankMap 내부에 선언된 'moveToBank' 함수를 호출하며 선택된 은행 데이터를 전달합니다.
  if (bankMapRef.value && bankMapRef.value.moveToBank) {
    bankMapRef.value.moveToBank(bank)
  }
}
</script>

<style scoped>
/* style 영역은 기존에 작성해두신 코드가 완벽하므로 그대로 유지하시면 됩니다! */
.map-page-wrapper {
  display: flex;
  width: 100%;
  height: calc(100vh - 64px); 
  overflow: hidden;
  background-color: #ffffff;
}

.side-panel {
  width: 40%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.map-panel {
  width: 60%;
  height: 100%;
}

@media (max-width: 1024px) {
  .map-page-wrapper {
    flex-direction: column;
    height: auto;
    overflow: visible;
  }

  .side-panel {
    width: 100%;
    height: 450px;
    order: 2;
  }

  .map-panel {
    width: 100%;
    height: 400px;
    order: 1;
  }
}
</style>