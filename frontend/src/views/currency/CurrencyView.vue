<template>
  <div class="currency-wrapper">
    <div class="currency-page">
      <CurrencyRate v-model:selectedCode="selectedCode" />
      <CurrencyChart :selectedCode="selectedCode" />
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import CurrencyRate from '@/components/currency/CurrencyRate.vue'
import CurrencyChart from '@/components/currency/CurrencyChart.vue'

const selectedCode = ref('')
</script>

<style scoped>
.currency-wrapper {
  background: #EBEADD;
  min-height: 100vh;
  width: 100%;
}
.currency-page {
  max-width: 860px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>