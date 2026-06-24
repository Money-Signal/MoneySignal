<template>
  <div class="currency-wrapper">
    <div class="currency-page">
      <PageHeader title="환율 조회" description="실시간 환율 및 과거 추이를 확인하세요." class="currency-page-header" />
      <div class="left-col">
        <CurrencyRate v-model:selectedCode="selectedCode" />
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

const selectedCode = ref('USD')

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
.currency-page {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2.5rem 2rem;
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 1.5rem;
  align-items: stretch;
}
.currency-page-header {
  grid-column: 1 / -1;
}
.left-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.right-col {
  display: flex;
  flex-direction: column;
  height: 100%;
}
</style>