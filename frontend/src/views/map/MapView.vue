<template>
  <div class="map-view">
    <BankList @search-result="onSearchResult" @select-bank="onSelectBank" />
    <BankMap :banks="searchedBanks" />
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
  // 추후: 지도 중심을 해당 은행으로 이동시키는 기능 등 추가 가능
}
</script>