<template>
  <div class="page-outer">
    <div class="page-container">
      <PageHeader title="주변 은행 검색" description="내 주변 은행을 찾고 영업시간과 위치를 확인하세요." />
      <div class="map-page-wrapper">
        <div class="side-panel">
          <BankList
            :banks="searchedBanks"
            :initial-query="initialQuery"
            @search-result="onSearchResult"
            @select-bank="onSelectBank"
          />
        </div>
        <div class="map-panel">
          <BankMap ref="bankMapRef" :banks="searchedBanks" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import BankMap from '@/components/map/BankMap.vue'
import BankList from '@/components/map/BankList.vue'
import PageHeader from '@/components/common/PageHeader.vue'

const route = useRoute()
const searchedBanks = ref([])
const bankMapRef = ref(null)
const initialQuery = ref('')

onMounted(() => {
  console.log('route.query.bank:', route.query.bank)
  if (route.query.bank) {
    initialQuery.value = route.query.bank
    console.log('initialQuery 설정됨:', initialQuery.value)
  }
})

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
  height: calc(100vh - 260px);
  min-height: 500px;
  overflow: hidden;
  border-radius: 12px;
  border: 1px solid #e1e6e2;
}

.side-panel {
  width: 38%;
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.map-panel {
  width: 62%;
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