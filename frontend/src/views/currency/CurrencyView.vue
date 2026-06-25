<template>
  <div class="currency-wrapper">
    <div class="currency-header-area">
      <PageHeader title="환율 조회" description="실시간 환율 및 과거 추이를 확인하세요." />
    </div>

    <LoadingSpinner v-if="isLoading" class="page-loading" />

    <div v-show="!isLoading" class="currency-content">
      <div class="left-col">
        <CurrencyRate v-model:selectedCode="selectedCode" @loaded="isLoading = false" />
      </div>
      <div class="right-col">
        <CurrencyChart :selectedCode="selectedCode" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import CurrencyRate from '@/components/currency/CurrencyRate.vue'
import CurrencyChart from '@/components/currency/CurrencyChart.vue'
import PageHeader from '@/components/common/PageHeader.vue'
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

const selectedCode = ref('USD')
const isLoading = ref(true)

onMounted(() => {
  const temp = selectedCode.value
  selectedCode.value = ''
  setTimeout(() => {
    selectedCode.value = temp
  }, 100)
})
</script>

<style scoped>
.currency-wrapper {
  background: #f9f8f5;
  min-height: 100vh;
  width: 100%;
}

.currency-header-area {
  max-width: 1320px;
  margin: 0 auto;
  padding: 2.5rem 2rem 0;
}

.page-loading {
  padding-top: 6rem;
}

.currency-content {
  max-width: 1320px;
  margin: 0 auto;
  padding: 1rem 2rem 2.5rem;
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  column-gap: 1.5rem;
  row-gap: 1rem;
  align-items: start;
}

.left-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.right-col {
  display: flex;
  flex-direction: column;
}
</style>
