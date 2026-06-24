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
const bankMapRef = ref(null)

const onSearchResult = (banks) => {
  searchedBanks.value = banks
}

const onSelectBank = (bank) => {
  if (bankMapRef.value && bankMapRef.value.moveToBank) {
    bankMapRef.value.moveToBank(bank)
  }
}
</script>

<style scoped>
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