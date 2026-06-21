<!-- views/map/MapView.vue -->
<template>
  <div class="map-view">
    <BankMap />
    <BankList />
  </div>
</template>

<script setup>
import BankMap from '@/components/map/BankMap.vue'
import BankList from '@/components/map/BankList.vue'
</script>