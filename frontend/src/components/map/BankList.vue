<template>
  <div class="bank-search">
    <select v-model="selectedSido" @change="onSidoChange">
      <option value="">광역시도 선택</option>
      <option v-for="sido in sidoList" :key="sido" :value="sido">{{ sido }}</option>
    </select>

    <select v-model="selectedGugun" :disabled="!selectedSido || gugunList.length <= 1">
      <option value="">시군구 선택</option>
      <option v-for="gugun in gugunList" :key="gugun" :value="gugun">{{ gugun }}</option>
    </select>

    <input 
      v-model="bankName" 
      placeholder="은행명 (예: 국민은행)" 
      @keyup.enter="searchBanks"
    />

    <button @click="searchBanks">검색</button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { regionData } from '@/utils/regionData'

const emit = defineEmits(['searchResult'])

const selectedSido = ref('')
const selectedGugun = ref('')
const bankName = ref('')
const gugunList = ref([])

const sidoList = Object.keys(regionData)

const onSidoChange = () => {
  selectedGugun.value = ''
  gugunList.value = regionData[selectedSido.value] || []
}

const searchBanks = () => {
  if (!window.kakao || !window.kakao.maps) {
    console.error('카카오맵 SDK가 로드되지 않았습니다.')
    return
  }

  const ps = new window.kakao.maps.services.Places()

  const query = [
    selectedSido.value,
    selectedGugun.value,
    bankName.value || '은행'
  ].filter(Boolean).join(' ')

  ps.keywordSearch(query, (data, status) => {
    if (status === window.kakao.maps.services.Status.OK) {
      emit('searchResult', data)
    } else {
      emit('searchResult', [])
      console.warn('검색 결과 없음 또는 에러:', status)
    }
  }, {
    category_group_code: 'BK9'
  })
}
</script>